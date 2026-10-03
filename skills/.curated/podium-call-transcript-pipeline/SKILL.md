---
name: podium-call-transcript-pipeline
description: Durable, idempotent ingest pipeline for Podium call transcripts — the layer between
  Podium's transcript webhook and a downstream RAG/LLM queue. Survives minutes-to-hours transcript
  latency, partial-then-final overwrites, non-English callers, PII leakage to downstream
  consumers, queue-write failures, and speaker-diarization loss. Use when wiring Podium phone-call
  transcripts into an AI-assist queue, hardening an existing ingest against transcript drift,
  redacting PII before transcripts reach an LLM, or building the durable ack/replay layer that
  feeds podium-rag-context-bridge. Trigger with "podium call transcripts", "podium transcript
  webhook", "podium transcript ingest", "podium transcript pii redact", "podium transcript
  chunking", "podium transcript queue".
allowed-tools: Read, Write, Edit, Bash(curl:*), Bash(jq:*), Bash(python3:*), Bash(redis-cli:*), Grep
version: 2.11.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
compatibility: Designed for Claude Code
tags:
  - podium
  - call-transcripts
  - webhooks
  - pii-redaction
  - rag-pipeline
  - language-detection
---

# Podium Call Transcript Pipeline

## Overview

Ingest Podium phone-call transcripts and stage them on a downstream queue so an LLM (with RAG context) can assist the team answering the phone. This is not a real-time transcription tool — Podium emits transcripts on a webhook minutes-to-hours after the call ends, and the design assumes that asynchrony. The skill is the durable layer between Podium and the RAG bridge: webhook lands, transcript is verified and de-duplicated, PII is redacted on ingest, speaker structure is preserved, language is detected, and a chunked record is enqueued for the next stage.

The six production failures this skill prevents:

1. **Assuming transcripts arrive in real-time** — they don't. Transcripts land on the webhook minutes to hours after the call ends. Pipelines designed around the call-ended event blocking until transcript availability either time out or hold an HTTP request open for hours. The ingest must be webhook-driven and ack-decoupled.
2. **Partial-transcript update events overwrite the final transcript** — Podium can emit `call.transcript.partial` before `call.transcript.completed`. Naive handlers store the partial as final, and the LLM downstream sees a truncated transcript. The ingest must key on `(transcript_id, event_type)` and only promote a record to "final" on a `completed` event.
3. **No language detection on ingest** — non-English transcripts sent to an English-only LLM produce nonsense answers that the on-phone agent reads to the customer. Detection on ingest routes non-English transcripts to a separate handling path before they reach the RAG layer.
4. **PII leakage to downstream consumers** — call transcripts contain credit card numbers, full phone numbers, addresses, and dates of birth. Once these reach a third-party LLM or RAG vector store they are effectively un-redactable. Redaction must happen on ingest, before the queue write, with an auditable per-redaction log.
5. **Queueing failures lose transcripts permanently** — the webhook handler returns 200 to Podium but the downstream queue write fails. The transcript is gone with no replay path. The ingest must persist the raw transcript to a local durable store **before** acking the webhook; the queue write happens from that durable store with retries.
6. **Missing speaker diarization fields** — Podium's transcript JSON tags each segment with a speaker role (caller vs agent). Flat ingest that concatenates segments destroys the structure the LLM needs. The chunker must be speaker-aware and never split a segment across speakers.

## Authentication

This skill does not authenticate to Podium directly. Two distinct auth paths are involved and **both are consumed by reference** from sibling skills — never re-implemented:

- **Inbound webhook auth** — HMAC signature verification is delegated to `podium-webhook-reliability::verify_webhook(raw, signature)`. The webhook secret lives in the verifier's config. The handler fails closed if the verifier is not importable.
- **Outbound Podium API auth** — the fallback poller acquires an OAuth bearer token via `podium-auth::PodiumAuth.get_token()`. Credentials live in `podium-auth`'s secret store.

The pipeline inherits the auth posture of both skills. Operator checklist when installing:

1. Verify that `podium-auth` and `podium-webhook-reliability` are both installed and configured.
2. Configure `.gitignore` to exclude the inbox database (`*.db`) and the redaction audit log (`redactions.jsonl`).
3. Run a regex grep across the host repo for Podium client-secret formats and Stripe-style live keys (the canonical patterns are listed in `references/implementation.md`) to confirm no inline credentials leaked.
4. Set `PODIUM_TRANSCRIPT_INBOX_PATH` to a writable path with mode 0600 ownership.
5. Configure the downstream queue backend (Redis Streams, SQS, or SQLite-as-queue) before enabling webhook traffic.

## Prerequisites

- Python 3.10+
- `podium-auth` skill installed (consumed for outbound API auth)
- `podium-webhook-reliability` skill installed (consumed for HMAC verification)
- `podium-rate-limit-survival` skill installed (consumed by the fallback poller)
- A durable inbox store — SQLite default; Postgres or DynamoDB are drop-in replacements
- A downstream queue — Redis Streams (default), AWS SQS, or local SQLite-as-queue for dev
- `langdetect` (default) or `fasttext-langdetect` for language detection
- `presidio-analyzer` + `presidio-anonymizer` for high-recall PII, or the bundled regex layer alone

## Instructions

Build in this order. Each section neutralizes one production failure mode.

### 1. Webhook-driven, ack-decoupled ingest

The webhook handler returns 200 fast and does all transcript work asynchronously. The handler's only synchronous job is verify-and-store-raw; everything else happens out-of-band in the processor.

```python
import json, time
from fastapi import FastAPI, Request, HTTPException
from podium_webhook_reliability import verify_webhook   # consumed by reference
from podium_call_transcript_pipeline import inbox

app = FastAPI()

@app.post("/podium/transcripts")
async def transcript_webhook(request: Request):
    raw = await request.body()
    sig = request.headers.get("podium-signature", "")
    if not verify_webhook(raw, sig):
        raise HTTPException(401, "invalid signature")
    event = json.loads(raw)
    if not event.get("type", "").startswith("call.transcript."):
        return {"status": "ignored"}

    # Durable write happens BEFORE returning 200. If this fails, return 5xx so Podium retries.
    inbox.insert(
        transcript_id=event["data"]["transcript_id"],
        event_type=event["type"],
        received_at=time.time(),
        raw_payload=raw,
    )
    return {"status": "accepted"}
```

### 2. Partial-vs-completed de-duplication

Podium emits these event types on a single call:

| Event type | Meaning | Handling |
|---|---|---|
| `call.ended` | Audio capture complete | Note arrival; no transcript yet |
| `call.transcript.partial` | Best-effort transcript while final generates | Store as partial; never promote to final |
| `call.transcript.completed` | Final transcript ready | Promote to final; supersedes any partial |
| `call.transcript.failed` | Transcription failed | Record failure; alert if call duration was material |

The inbox table is keyed on `(transcript_id, event_type)`. A separate `transcripts` table is keyed on `transcript_id` alone. A `completed` event always supersedes a `partial` for the same `transcript_id`. A late-arriving `partial` after `completed` is ignored — the processor checks current status before writing.

### 3. Language detection on ingest

Detect language before redaction (redaction patterns are language-aware downstream). The default policy: English transcripts proceed to the standard RAG queue; non-English transcripts go to a separate queue with a translation step inserted.

```python
from langdetect import detect_langs, DetectorFactory
DetectorFactory.seed = 0   # deterministic detection across runs

def detect_transcript_language(text: str) -> tuple[str, float]:
    if len(text.strip()) < 20:
        return ("und", 0.0)   # too short to detect reliably
    try:
        top = detect_langs(text)[0]
        return (top.lang, top.prob)
    except Exception:
        return ("und", 0.0)
```

Routing rule: English with confidence ≥ 0.85 → `queue:rag.transcripts.en`; confidence < 0.50 → `queue:rag.transcripts.review` (human review); otherwise → per-language queue.

### 4. PII redaction on ingest

Redaction is **non-optional** and happens before the transcript is written to the outbound queue. The redaction is auditable — for every redaction the system records category, character offsets, and the rule's id. Conservative regex layer for high-precision categories; presidio/spaCy for lower-precision recall categories (names, addresses).

```python
import re
from dataclasses import dataclass

@dataclass
class Redaction:
    category: str
    rule_id: str
    start: int
    end: int

PATTERNS = [
    ("CREDIT_CARD", "card_luhn_16", re.compile(r"\b(?:\d[ -]?){13,19}\b")),
    ("PHONE",       "phone_intl",   re.compile(r"\+?\d{1,3}[ -]?\(?\d{2,4}\)?[ -]?\d{3,4}[ -]?\d{3,4}")),
    ("EMAIL",       "email_basic",  re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")),
    ("SSN_US",      "ssn_us",       re.compile(r"\b\d{3}-\d{2}-\d{4}\b")),
]

def luhn_valid(s: str) -> bool:
    digits = [int(c) for c in s if c.isdigit()]
    if not 13 <= len(digits) <= 19: return False
    checksum = 0
    for pos, d in enumerate(reversed(digits)):
        if pos % 2 == 1:
            d *= 2
            if d > 9: d -= 9
        checksum += d
    return checksum % 10 == 0
```

Wire presidio after the regex pass and union both result lists into one audit log keyed by `transcript_id`. Never ship a redaction module that silently swallows detections — every detection must either redact-and-log or pass-through-and-log with a documented reason.

### 5. Durable inbox + queue write with replay

The webhook writes to a durable store (SQLite default) before acking. A separate processor moves records from the inbox to the outbound queue. Failed queue writes stay in the inbox with `attempt_count` and `next_attempt_at` — the processor's next scan picks them up.

```python
SCHEMA = """
CREATE TABLE IF NOT EXISTS inbox (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transcript_id TEXT NOT NULL,
    event_type    TEXT NOT NULL,
    received_at   REAL NOT NULL,
    raw_payload   BLOB NOT NULL,
    processed_at  REAL,
    enqueued_at   REAL,
    attempt_count INTEGER NOT NULL DEFAULT 0,
    next_attempt_at REAL,
    last_error    TEXT,
    UNIQUE(transcript_id, event_type)
);
"""
# UNIQUE(transcript_id, event_type) makes webhook redelivery idempotent.
# 3600 seconds = 1h cap on exponential backoff; 12-attempt budget = ~4 days before dead-letter.
```

Failed queue writes increment `attempt_count`, set `next_attempt_at = now + min(2^attempts, 3600)`. After 12 attempts the row moves to `inbox_deadletter` and pages on-call.

### 6. Speaker-aware chunking

Podium's transcript JSON has a `segments[]` array with `{speaker_role, start_ms, end_ms, text}` per utterance. Two rules:

1. **Never split a segment across speakers.** A chunk boundary always lands at a segment boundary.
2. **Mark every chunk with its speaker turn-set.** A chunk carries `speakers: [...]`.

```python
# target_tokens=1500 fits a chunk inside a 4k context with room for RAG-retrieved
# companion chunks plus prompt scaffolding. overlap_tokens=200 preserves cross-chunk
# context without doubling the token budget.
def chunk_transcript(segments, target_tokens=1500, overlap_tokens=200):
    chunks, current = [], Chunk(chunk_index=0)
    for seg in segments:
        seg_tokens = estimate_tokens(seg.text)
        if current.token_count + seg_tokens > target_tokens and current.segments:
            chunks.append(current)
            overlap = build_overlap(current.segments, overlap_tokens)
            current = Chunk(chunk_index=len(chunks), segments=list(overlap),
                            token_count=sum(estimate_tokens(s.text) for s in overlap))
        current.segments.append(seg)
        current.token_count += seg_tokens
        if seg.speaker_role not in current.speakers:
            current.speakers.append(seg.speaker_role)
    if current.segments:
        chunks.append(current)
    return chunks
```

The outbound record consumed by `podium-rag-context-bridge` carries `transcript_id`, `call_id`, `location_uid`, `detected_language`, `language_confidence`, `redaction_count`, and `chunks[]` with per-chunk `speakers` and `segments`.

## Error Handling

| Code | Source | Root Cause | Action |
|---|---|---|---|
| `401` on webhook | Handler | Signature verification failed | Reject; verifier config wrong |
| `5xx` to Podium | Inbox write failed | SQLite unwritable | Return 5xx so Podium retries; page on-call |
| `ERR_TXP_001` | Reconciler | `partial` after `completed` | Ignored by design; logged |
| `ERR_TXP_002` | Reconciler | No transcript within N hours | Fallback poller fetches directly |
| `ERR_TXP_003` | Language detector | Transcript < 20 chars | Route to review queue |
| `ERR_TXP_004` | Redactor | Presidio unavailable | Regex-only mode active; warn per transcript |
| `ERR_TXP_005` | Queue write | Redis/SQS error | Increment attempts; exponential backoff |
| `ERR_TXP_006` | Chunker | Single segment > target_tokens | Allow oversize chunk; warn |
| `ERR_TXP_007` | Processor | attempts > 12 | Move to dead-letter; page on-call |

## Examples

### Minimal end-to-end ingest

```bash
uvicorn podium_call_transcript_pipeline.webhook_ingest:app --host 0.0.0.0 --port 8080 &
python3 scripts/transcript_chunker.py --process-loop --interval 5
sqlite3 podium_transcripts.db "SELECT transcript_id, event_type, processed_at FROM inbox ORDER BY received_at DESC LIMIT 10;"
```

### Redact a transcript via the CLI

```bash
python3 scripts/pii_redact.py --input transcript-raw.json --output transcript-redacted.json --audit-log redactions.jsonl
```

### Fallback poller for missing webhooks

```bash
python3 scripts/transcript_poller.py --since-hours 12 --max-age-hours 4 --location-uid "{location-uid}"
```

### Chunk with speaker-preserving overlap

```bash
python3 scripts/transcript_chunker.py --input transcript-redacted.json --output chunks.json --target-tokens 1500 --overlap-tokens 200
```

## Output

- Webhook handler that verifies + durably stores transcript events before acking
- Inbox table with UNIQUE constraint making webhook redelivery idempotent
- Reconciler that promotes `completed` over `partial` and never the inverse
- Language detector with deterministic seeding and confidence thresholds
- PII redactor with auditable per-redaction log, Luhn-validated card detection
- Speaker-aware chunker (1500-token target, 200-token overlap, never splits across speakers)
- Fallback poller for missing-webhook recovery
- Outbound record shape consumed directly by `podium-rag-context-bridge`

## Resources

- [Podium API docs — Conversations & Transcripts](https://docs.podium.com/reference/conversations)
- [Podium Webhooks reference](https://docs.podium.com/reference/webhooks)
- [config/settings.yaml](config/settings.yaml) — chunk size, redaction policy, queue backend, language routing
- [references/errors.md](references/errors.md) — `ERR_TXP_*` codes with cause + solution
- [references/examples.md](references/examples.md) — 10 worked examples (multi-location, presidio, SQS, AU PII)
- [references/implementation.md](references/implementation.md) — Node port, presidio wiring, queue backend tradeoffs, dead-letter handling
- [scripts/webhook_ingest.py](scripts/webhook_ingest.py) — FastAPI handler (verify + inbox insert + 200)
- [scripts/transcript_poller.py](scripts/transcript_poller.py) — CLI: poll conversations API when webhook missed
- [scripts/pii_redact.py](scripts/pii_redact.py) — CLI: redact a transcript JSON + audit log
- [scripts/transcript_chunker.py](scripts/transcript_chunker.py) — CLI: chunk with speaker-preserving overlap
