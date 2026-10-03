---
name: podium-webhook-reliability
description: Operate a Podium webhook receiver that survives the delivery-side failures —
  forged events without signature verification, replay attacks against a stateless handler,
  duplicate processing from Podium's 24h retry policy, lost events with no dead-letter queue,
  out-of-order batch deliveries, and timing-attack-vulnerable HMAC compares. Use when building
  a webhook endpoint for call transcripts, webchat events, conversation lifecycle, or review
  notifications; hardening an existing handler that processes events twice or drops them
  silently; or wiring a DLQ + replay path before the on-call rotation starts. Trigger with
  "podium webhook", "podium hmac", "podium signature", "podium webhook idempotency",
  "podium webhook replay", "podium dlq", "podium webhook retries".
allowed-tools: Read, Write, Edit, Bash(curl:*), Bash(jq:*), Bash(python3:*), Bash(redis-cli:*), Grep
version: 2.11.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
compatibility: Designed for Claude Code
tags:
  - podium
  - webhooks
  - hmac
  - idempotency
  - dlq
  - security
---

# Podium Webhook Reliability

## Overview

Receive Podium webhooks in production without forged events, double-charged AI side-effects, lost notifications, or out-of-order conversation events. This is not an introductory webhook walkthrough — it is the receiver code your integration runs when Podium retries a 5xx response six times over 24 hours, when a leaked secret lets an attacker POST forged events, when a batch delivery arrives with `conversation.deleted` ahead of `conversation.created`, and when on-call needs to drain and replay 800 failed events without re-firing the ones that already succeeded.

The six production failures this skill prevents:

1. **Missing signature verification** — a webhook endpoint that accepts any POST will accept forged events. An attacker who learns the URL can create phantom contacts, fire phantom review requests, or impersonate a real customer in a webchat. HMAC-SHA256 over the raw request body is non-optional and must run before any handler logic.
2. **Replay attacks against a stateless handler** — a valid signed event POSTed twice (or 1000 times) re-runs every side effect each time. Signature validity alone is not enough — the receiver must reject events whose timestamp falls outside a 5-minute window AND whose nonce has already been seen.
3. **Duplicate event processing from Podium retries** — Podium retries webhook delivery on 5xx for up to 24 hours. Without an idempotency cache, every retry re-runs the handler (writes the contact again, fires the review request again, double-charges an AI call). `SET NX EX 86400` on the event_id is the cheapest fix that exists.
4. **Lost events without a dead-letter queue** — if a handler raises and Podium retries six times and gives up, the event is gone. On-call has nothing to replay. Every handler exception must persist the raw signed payload to a DLQ before the response returns 5xx, so the event is recoverable independent of Podium's retry clock.
5. **Batch event reordering** — Podium can deliver multiple events in one POST and ordering across deliveries is not guaranteed. A naive handler processes `conversation.deleted` before `conversation.created` and the system observes a delete on a contact that does not exist. Within a batch, sort by `occurred_at` before dispatch; across batches, gate causally-dependent handlers on the precondition existing.
6. **Timing-attack vulnerability on signature compare** — `received_sig == computed_sig` with `==` short-circuits on the first byte mismatch. An attacker measures response latency to recover the signature byte-by-byte over a few thousand probes. Always use `hmac.compare_digest`, which is constant-time over the longer of the two inputs.

## Prerequisites

- Python 3.10+ with `fastapi`, `uvicorn`, `httpx`, and `redis` (in-memory fallback for dev is provided)
- Podium account with an OAuth app authorized for webhook delivery: Settings → Developer → Apps → Webhooks
- The webhook signing secret from the app's Webhooks tab (saved to a secret store — never committed)
- A receiver URL reachable from Podium (publicly resolvable HTTPS endpoint with valid cert)
- Redis 6+ for production dedup + DLQ; an in-memory dict + SQLite file fallback exists for dev
- A `podium-auth` instance if your handler needs to call back into the Podium API after processing

## Instructions

Build in this order. Each section neutralizes one production failure mode.

### 1. HMAC-SHA256 signature verification on the raw body (neutralizes forgery)

Verify the signature against the **raw, unparsed** request body. Any framework middleware that JSON-decodes-and-re-encodes before signature check will fail because whitespace and key ordering change. Read the body once, verify, then parse:

```python
import hmac, hashlib
from fastapi import FastAPI, Request, HTTPException, Header

app = FastAPI()
SIGNING_SECRET = os.environ["PODIUM_WEBHOOK_SECRET"].encode("utf-8")

@app.post("/webhooks/podium")
async def receive(request: Request, x_podium_signature: str = Header(None)):
    raw = await request.body()              # bytes — DO NOT decode/re-encode
    if not x_podium_signature:
        raise HTTPException(401, "missing X-Podium-Signature")
    if not verify_signature(raw, x_podium_signature):
        raise HTTPException(401, "signature mismatch")
    # ... continue with replay/dedup/dispatch
```

```python
def verify_signature(body: bytes, header_value: str) -> bool:
    # Podium signature header format: "t=<unix_ts>,v1=<hex_hmac>"
    # Adapt to current spec — verify against the Podium developer docs at integration time.
    parts = dict(p.split("=", 1) for p in header_value.split(",") if "=" in p)
    ts, sig = parts.get("t"), parts.get("v1")
    if not ts or not sig:
        return False
    signed_payload = f"{ts}.".encode("utf-8") + body
    expected = hmac.new(SIGNING_SECRET, signed_payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, sig)    # constant-time, byte-by-byte safe
```

The `t=` timestamp is what makes the next mitigation possible. A signature alone with no timestamp is replayable forever.

### 2. Replay-attack window (neutralizes timestamp replay)

Reject any event whose signed timestamp is more than 5 minutes from now (in either direction — clock skew goes both ways). This bounds the replay window an attacker has even if they capture a valid signed event off the wire:

```python
import time

REPLAY_WINDOW_SECONDS = 300        # 5 minutes; tune to your clock-skew tolerance

def within_replay_window(ts_str: str) -> bool:
    try:
        ts = int(ts_str)
    except (TypeError, ValueError):
        return False
    return abs(time.time() - ts) <= REPLAY_WINDOW_SECONDS
```

Wire `within_replay_window(parts["t"])` immediately after signature verification. A failed window check is a 401 — do not return 200, do not enqueue, do not log the body (the attacker is probing).

### 3. Idempotent dedup with `SET NX EX 86400` (neutralizes duplicate processing)

Every Podium webhook carries an `event_id` (or equivalent unique identifier — verify against the current schema). Reject any event whose `event_id` is already in the dedup cache. Use Redis `SET key value NX EX 86400` so the check and the claim are atomic; 86400 seconds matches Podium's 24-hour retry ceiling:

```python
import redis.asyncio as redis

REDIS = redis.from_url(os.environ.get("REDIS_URL", "redis://localhost:6379/0"))

async def claim_event(event_id: str) -> bool:
    # Returns True if this process is the first to see this event_id.
    # Returns False if the event_id is already in the cache (duplicate).
    return await REDIS.set(f"podium:evt:{event_id}", "1", nx=True, ex=86400)
```

In the handler:

```python
event = json.loads(raw)
event_id = event["id"]
if not await claim_event(event_id):
    return {"status": "duplicate", "event_id": event_id}     # 200 — Podium stops retrying
```

Returning 200 on duplicate is correct — Podium has correctly delivered, the receiver has correctly identified it as already processed. The handler is idempotent by construction.

For dev / smoke environments without Redis, fall back to an in-memory `set()` with a periodic eviction loop. Documented in `references/implementation.md`.

### 4. Dead-letter queue before responding 5xx (neutralizes silent event loss)

Wrap every handler invocation in a try/except. On any exception, persist the **raw signed payload plus the timestamp plus the signature** to the DLQ before letting the exception bubble. The DLQ entry is the recovery anchor — `dlq_replay.py` can re-POST it to the handler later:

```python
async def safe_dispatch(event: dict, raw: bytes, sig_header: str):
    try:
        await dispatch(event)
    except Exception as e:
        await dlq_persist({
            "event_id": event.get("id"),
            "event_type": event.get("type"),
            "raw_body": raw.decode("utf-8", errors="replace"),
            "signature_header": sig_header,
            "occurred_at": event.get("occurred_at"),
            "received_at": time.time(),
            "exception": f"{type(e).__name__}: {e}",
        })
        raise          # let FastAPI return 5xx; Podium will retry
```

DLQ backend options (in priority order):

| Backend | When |
|---|---|
| Redis list `LPUSH podium:dlq` + scheduled archiver to S3/GCS | Default for prod |
| SQLite file at `/var/lib/podium-dlq.sqlite` | Single-node deployments, dev |
| Append-only JSONL at `/var/log/podium-dlq.jsonl` | Fallback when nothing else is available — durable, parseable, ugly |

The DLQ is durable independent of the Redis dedup cache. If Redis dies, dedup is degraded but events are still recoverable.

### 5. Batch event ordering by `occurred_at` (neutralizes reordering)

Podium can deliver multiple events in one POST. Within the batch, sort by `occurred_at` ascending before dispatch. Across batches, do not assume earlier-timestamped events arrived first — guard causally-dependent handlers with an existence check:

```python
async def dispatch_batch(events: list[dict]):
    events.sort(key=lambda e: (e.get("occurred_at", 0), e.get("id", "")))
    for event in events:
        await safe_dispatch_one(event)

async def handle_conversation_deleted(event: dict):
    convo_id = event["data"]["conversation_id"]
    # Guard: if the create event hasn't been processed yet, defer this delete.
    if not await convo_exists(convo_id):
        await dlq_persist({
            "reason": "out_of_order_delete_before_create",
            "event_id": event["id"],
            "raw_body": json.dumps(event),
            "received_at": time.time(),
        })
        return
    await delete_conversation_locally(convo_id)
```

Sorting within a batch is cheap and correct. Cross-batch ordering is undecidable from the receiver side — the DLQ + replay path is the recovery mechanism when out-of-order delivery violates a precondition.

### 6. Constant-time HMAC compare (neutralizes signature-byte timing leak)

The single most common implementation bug in webhook receivers is `received == expected` with `==`. Python string `==` short-circuits on the first differing byte; an attacker measures response latency over a few thousand probes and reconstructs the signature byte by byte.

```python
# WRONG — leaks signature byte-by-byte via timing
if received_sig == expected_sig:
    return True

# CORRECT — constant-time over the longer of the two inputs
if hmac.compare_digest(received_sig, expected_sig):
    return True
```

`hmac.compare_digest` is the only acceptable comparison. The same rule applies to Node (`crypto.timingSafeEqual`), Go (`hmac.Equal`), and Rust (`subtle::ConstantTimeEq`).

## Error Handling

| HTTP returned | Internal condition | Caller (Podium) behavior |
|---|---|---|
| `401 Unauthorized` | Signature mismatch, missing header, replay window failed | Podium does NOT retry — log + audit |
| `400 Bad Request` | Body is not parseable JSON post-signature-verify | Podium does NOT retry — investigate Podium-side payload |
| `200 OK (duplicate)` | `event_id` already in dedup cache | Podium stops retrying — system is idempotent |
| `200 OK (processed)` | Handler dispatched successfully | Podium stops retrying — normal path |
| `200 OK (deferred)` | Out-of-order event written to DLQ; will resolve via replay | Podium stops retrying — recovery is internal |
| `500 Internal Server Error` | Handler raised; DLQ entry persisted | Podium retries with exponential backoff up to 24h |
| `503 Service Unavailable` | Redis dedup unreachable; handler refuses | Podium retries — fail-closed is the safe default |

## Examples

### Verify a captured webhook payload from the command line

```bash
# Use the CLI bundled with the skill to verify a captured payload + header against the secret.
python3 scripts/signature_verify.py \
  --body-file /tmp/captured_webhook_body.json \
  --signature-header "t={your-timestamp},v1={your-podium-signature}" \
  --secret-env PODIUM_WEBHOOK_SECRET
# exit 0 = valid; exit 1 = signature mismatch; exit 2 = replay window exceeded
```

### Manually check if an event_id has been seen

```bash
python3 scripts/dedup_check.py --event-id evt_{your-event-identifier} --redis-url redis://localhost:6379/0
# exit 0 = first sight (would be processed); exit 1 = duplicate (would be rejected)
```

### Drain the DLQ and replay events through the handler

```bash
# After a handler bug is fixed, replay DLQ entries through the receiver.
# The replay path goes through the SAME endpoint as Podium, so signature + dedup still apply.
python3 scripts/dlq_replay.py \
  --target-url https://your-receiver.example.com/webhooks/podium \
  --secret-env PODIUM_WEBHOOK_SECRET \
  --batch-size 25 \
  --rate-per-sec 10
```

The replay script reuses the original signature header captured at DLQ-persist time — Podium's signing secret is the same secret your replayer uses to compute the header, so no re-signing is required for events captured within the secret's lifetime.

### Boot the receiver locally for development

```bash
export PODIUM_WEBHOOK_SECRET={your-webhook-secret}
export REDIS_URL=redis://localhost:6379/0   # or unset to use in-memory fallback
uvicorn scripts.webhook_server:app --host 0.0.0.0 --port 8080 --reload
```

## Output

- FastAPI receiver with HMAC verification on the raw body, replay window, dedup, DLQ, and batch ordering
- Signature verifier CLI (`signature_verify.py`) for incident forensics on captured payloads
- Dedup-cache checker CLI (`dedup_check.py`) for confirming a specific event was already processed
- DLQ replayer CLI (`dlq_replay.py`) for draining persisted failures after a handler fix
- Redis-backed dedup with 24h TTL aligned to Podium's retry ceiling
- DLQ persistence with multiple backend options (Redis list, SQLite, JSONL)
- `.gitignore` rules covering the webhook secret + captured payload files

## Resources

- [Podium API docs — Webhooks](https://docs.podium.com/reference/webhooks)
- [Podium API docs — Webhook signatures](https://docs.podium.com/reference/webhook-signatures)
- [config/settings.yaml](config/settings.yaml) — replay window, dedup TTL, DLQ backend selection, batch sizing
- [references/errors.md](references/errors.md) — ERR_WHK_* codes with cause + solution
- [references/examples.md](references/examples.md) — 10 worked examples (single handler, batch, multi-tenant, replay)
- [references/implementation.md](references/implementation.md) — Node.js port, Redis schema, DLQ backends, in-memory fallback
- [scripts/webhook_server.py](scripts/webhook_server.py) — FastAPI receiver with the full pipeline wired
- [scripts/signature_verify.py](scripts/signature_verify.py) — CLI: verify a captured payload + signature
- [scripts/dedup_check.py](scripts/dedup_check.py) — CLI: check if an event_id is already cached
- [scripts/dlq_replay.py](scripts/dlq_replay.py) — CLI: drain the DLQ and re-POST to the receiver
