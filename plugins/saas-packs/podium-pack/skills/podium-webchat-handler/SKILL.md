---
name: podium-webchat-handler
description: Ingest Podium webchat messages in production and survive the webchat-side failures —
  invalid phone formats accepted at the widget, contact auto-creation races producing duplicate
  records, session timeouts mid-conversation, attachment size overflows, cross-location chat
  routing wrong, and opt-out propagation lag. Use when hardening a webchat → API integration,
  building a multi-location chat widget, debugging duplicate contacts, or recovering from a
  cross-location routing incident. Trigger with "podium webchat", "podium chat widget",
  "podium phone validation", "podium contact dedup", "podium webchat session", "podium opt-out",
  "podium location routing".
allowed-tools: Read, Write, Edit, Bash(curl:*), Bash(jq:*), Bash(python3:*), Grep
version: 2.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
compatibility: Designed for Claude Code
tags:
  - podium
  - webchat
  - phone-validation
  - e164
  - contact-dedup
  - multi-location
---

# Podium Webchat Handler

## Overview

Ingest Podium webchat messages into your production system and operate the webchat layer when it breaks. This is not a setup walkthrough — it is the handler code your integration runs at 11am on a Saturday when a Brisbane customer's webchat lands on the Sydney store's queue, when two simultaneous webchats from the same phone produce two duplicate contact records, when a customer types `1` of a `1-2-3` answer and the session dies before they finish, and when a customer types STOP and the next session five minutes later still tries to SMS them.

The six production failures this skill prevents:

1. **Invalid phone formats accepted** — Webchat asks for a phone number and a customer types `0412 345 678` (Australian local) or `(415) 555-1234` (US local) without E.164 normalization. The handler stores the local form. The later SMS reply attempt fails silently because Podium expects `+61412345678` / `+14155551234`. The agent thinks they replied; the customer never receives anything.
2. **Contact auto-creation race produces duplicates** — Two webchats arrive within milliseconds from the same phone (customer opens two tabs, or a webhook retry overlaps the first delivery). Both handlers check "does a contact with this phone exist?", both see no, both create — and now the same human is two contact records, with conversation history split across both.
3. **Webchat sessions time out mid-conversation** — Podium webchat sessions have a server-side expiry (default ~30 min idle). A customer types `1` of a `1-2-3` multiple-choice answer, walks away to grab lunch, comes back to finish, and discovers the agent picked up the conversation in fresh context without the `1` they sent.
4. **Attachment size overflows** — Podium accepts attachments up to 25MB. Webchat-to-API integrations that don't validate size client-side before upload fail server-side with a 413 — but only after the customer has waited through the upload progress bar. The customer thinks the image was sent; the agent never sees it.
5. **Cross-location chat routing is wrong** — A Sydney-based store and a Burleigh Heads–based store share the same Podium org. The webchat widget is embedded on a single corporate site and doesn't pass `location_uid` on the initial message. Every chat lands in the default location's queue regardless of which store the customer was actually browsing.
6. **Opt-out propagation lag** — A customer types STOP in an SMS thread. The opt-out flag is recorded in the SMS subsystem but not propagated to the webchat subsystem. Five minutes later the customer starts a new webchat session; the integration still tries to send an SMS confirmation reply and trips a compliance violation.

## Prerequisites

- Python 3.10+ (examples) or Node.js 18+
- `podium-auth` skill installed and a working `PodiumAuth` instance for OAuth token management
- `podium-webhook-reliability` skill installed if consuming webchat events via webhook (HMAC + dedup live there)
- `phonenumbers` library (Google's libphonenumber port): `pip install phonenumbers`
- Podium org with at least one location configured; for multi-location, the full `location_uid` list
- A contact store with a unique index on the normalized E.164 phone column (the natural dedup key)

## Instructions

Build in this order. Each section neutralizes one production failure mode.

### 1. E.164 phone normalization at the widget edge (neutralizes invalid phone formats)

Normalize phone numbers to E.164 **at the widget input boundary** before the message ever reaches your API. The widget knows the customer's locale context; the API does not. Use `phonenumbers` for the parse + validation:

```python
import phonenumbers
from phonenumbers import NumberParseException, PhoneNumberFormat, is_valid_number

class PhoneValidationError(Exception):
    pass

def normalize_phone(raw: str, default_country: str = "AU") -> str:
    """Parse a raw phone string and return E.164 form. Raises on invalid."""
    try:
        parsed = phonenumbers.parse(raw, default_country)
    except NumberParseException as e:
        raise PhoneValidationError(f"unparseable phone {raw!r}: {e}")
    if not is_valid_number(parsed):
        raise PhoneValidationError(f"invalid phone for region {default_country}: {raw!r}")
    return phonenumbers.format_number(parsed, PhoneNumberFormat.E164)

# Examples
assert normalize_phone("0412 345 678", "AU") == "+61412345678"
assert normalize_phone("(415) 555-1234", "US") == "+14155551234"
assert normalize_phone("+61 412 345 678", "AU") == "+61412345678"
```

The `default_country` parameter is the location's country (Sydney → AU, Burleigh Heads → AU, San Francisco → US). Pass it from the widget context, never hardcode globally. If the widget runs on a multi-region site and cannot determine the default, fail closed — refuse to accept the message until the customer enters a `+`-prefixed number explicitly.

### 2. Contact auto-creation race (neutralizes duplicate contact records)

The naive pattern — `if not contact_exists(phone): create_contact(phone)` — has a TOCTOU race. Under simultaneous webchat arrivals from the same phone, both branches see "no" and both create. The fix is **idempotent upsert keyed on the E.164 phone** with a unique index in the contact store, and retry-on-conflict semantics:

```python
import httpx
from podium_auth import PodiumAuth

async def upsert_contact_by_phone(
    auth: PodiumAuth,
    phone_e164: str,
    location_uid: str,
    first_name: str | None = None,
    last_name: str | None = None,
) -> dict:
    """Idempotent contact creation. Returns the contact record; never creates a duplicate."""
    token = await auth.get_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Step 1: lookup by phone
    async with httpx.AsyncClient(timeout=10) as c:
        r = await c.get(
            "https://api.podium.com/v4/contacts",
            headers=headers,
            params={"phone": phone_e164, "location_uid": location_uid},
        )
    if r.status_code == 200 and r.json().get("data"):
        return r.json()["data"][0]

    # Step 2: create — but tolerate 409 conflict from a racing creator
    async with httpx.AsyncClient(timeout=10) as c:
        r = await c.post(
            "https://api.podium.com/v4/contacts",
            headers=headers,
            json={
                "phone": phone_e164,
                "location_uid": location_uid,
                "first_name": first_name,
                "last_name": last_name,
            },
        )
    if r.status_code in (200, 201):
        return r.json()
    if r.status_code == 409:
        # The race lost — refetch and return the winner's record
        async with httpx.AsyncClient(timeout=10) as c:
            r2 = await c.get(
                "https://api.podium.com/v4/contacts",
                headers=headers,
                params={"phone": phone_e164, "location_uid": location_uid},
            )
        if r2.status_code == 200 and r2.json().get("data"):
            return r2.json()["data"][0]
    raise WebchatError(f"contact upsert failed: {r.status_code} {r.text}")

class WebchatError(Exception):
    pass
```

In your local contact mirror (if you maintain one), enforce a database-level unique index on `phone_e164` so a parallel writer hits the constraint instead of silently double-inserting. The deeper mechanics — collision resolution when the same phone owns conflicting first/last names across sources — live in `podium-contact-dedup`. This skill prevents the most common race; that skill handles the harder reconciliation cases.

### 3. Webchat session timeout monitor (neutralizes mid-conversation context loss)

Podium webchat sessions have a server-side idle timeout. Detect approaching-expiry on your side and either prompt the customer to confirm they're still there, or buffer the partial answer so the agent picks up the conversation with context preserved:

```python
import time
from dataclasses import dataclass, field

SESSION_IDLE_WARN_SECONDS  = 20 * 60   # 20 min — prompt customer
SESSION_IDLE_CLOSE_SECONDS = 28 * 60   # 28 min — close cleanly before Podium expires

@dataclass
class WebchatSession:
    session_uid: str
    phone_e164: str
    location_uid: str
    last_message_at: float
    partial_state: dict = field(default_factory=dict)  # buffered multi-step answers

    def idle_seconds(self) -> float:
        return time.time() - self.last_message_at

    def status(self) -> str:
        idle = self.idle_seconds()
        if idle >= SESSION_IDLE_CLOSE_SECONDS: return "close"
        if idle >= SESSION_IDLE_WARN_SECONDS:  return "warn"
        return "active"

async def scan_sessions(sessions: dict[str, WebchatSession]) -> None:
    """Run on a 60s loop. Emit prompts and clean closures."""
    for uid, s in list(sessions.items()):
        st = s.status()
        if st == "warn":
            await send_keepalive_prompt(s.session_uid)   # "still there? type anything to continue"
        elif st == "close":
            await persist_partial_state(s)               # save the `1` of `1-2-3` answer
            await close_session_cleanly(s.session_uid)
            del sessions[uid]
```

The buffered `partial_state` is the load-bearing piece. When the next message arrives on the same `phone_e164 + location_uid`, hydrate the previous partial state so the customer is not asked to start over.

### 4. Attachment size validation client-side (neutralizes 413 surprises)

Podium's 25MB attachment limit is documented but the API only returns the 413 after the upload completes. Validate at the widget — before the upload starts — so the customer is told immediately:

```python
PODIUM_ATTACHMENT_MAX_BYTES = 25 * 1024 * 1024   # 25 MiB

class AttachmentTooLargeError(Exception):
    pass

def validate_attachment_size(size_bytes: int) -> None:
    if size_bytes > PODIUM_ATTACHMENT_MAX_BYTES:
        raise AttachmentTooLargeError(
            f"attachment is {size_bytes / 1024 / 1024:.1f} MiB; "
            f"Podium accepts up to {PODIUM_ATTACHMENT_MAX_BYTES / 1024 / 1024:.0f} MiB"
        )
```

In the widget, wire this to the file-input `change` event. In the API handler, double-check the `Content-Length` of incoming uploads and reject with a 413 of your own before forwarding to Podium — this saves both the egress cost and the user-visible failure when the upload finishes and then dies.

### 5. Multi-location routing (neutralizes wrong-store routing)

A multi-location org needs `location_uid` on every webchat-originated request. The widget must know which location it represents — either via a per-location embed snippet or via a URL/cookie hint resolved at chat-open time. The handler must **reject** messages that arrive without a valid `location_uid`:

```python
VALID_LOCATION_UIDS: set[str] = set()   # populate at startup from Podium /v4/locations

async def load_locations(auth: PodiumAuth) -> None:
    token = await auth.get_token()
    async with httpx.AsyncClient(timeout=10) as c:
        r = await c.get(
            "https://api.podium.com/v4/locations",
            headers={"Authorization": f"Bearer {token}"},
        )
    r.raise_for_status()
    VALID_LOCATION_UIDS.clear()
    VALID_LOCATION_UIDS.update(loc["uid"] for loc in r.json()["data"])

def validate_location(location_uid: str | None) -> str:
    if not location_uid:
        raise WebchatError("location_uid is required — refusing to route to a default")
    if location_uid not in VALID_LOCATION_UIDS:
        raise WebchatError(f"unknown location_uid {location_uid!r}")
    return location_uid
```

The "Sydney store gets a Brisbane customer" failure mode happens specifically when the integration falls back to a default location on missing `location_uid`. Do not have a default. Refuse the request and surface a config error to the widget operator.

### 6. Opt-out propagation across SMS + webchat (neutralizes compliance drift)

A STOP message in either channel must propagate to both. Maintain a single opt-out store keyed on E.164 phone, and consult it on every outbound message attempt regardless of channel:

```python
OPTOUT_KEYWORDS = {"STOP", "UNSUBSCRIBE", "QUIT", "END", "CANCEL", "OPTOUT"}

async def check_optout(phone_e164: str) -> bool:
    """Returns True if this phone is opted out across ALL channels."""
    # Backed by a database table or KV store; this is the unified view.
    return await optout_store.is_opted_out(phone_e164)

async def record_optout(phone_e164: str, source_channel: str) -> None:
    """Called from BOTH the SMS handler and the webchat handler on STOP keywords."""
    await optout_store.set_opted_out(phone_e164, source_channel, recorded_at=time.time())
    # Mirror to Podium so their compliance view matches yours
    await mark_contact_optout_in_podium(phone_e164)

async def handle_inbound_webchat(message: dict, auth: PodiumAuth) -> None:
    phone = normalize_phone(message["from"], message.get("country") or "AU")
    text = message["body"].strip().upper()
    if text in OPTOUT_KEYWORDS:
        await record_optout(phone, source_channel="webchat")
        return  # do NOT send any reply
    if await check_optout(phone):
        # Customer previously opted out via SMS; refuse to handle the webchat
        # outbound side. Log for audit, do not reply.
        log_optout_blocked(phone, channel="webchat")
        return
    await process_webchat_message(message, auth)
```

The opt-out check must run on every outbound attempt — not just at session start — because the opt-out can land between the session opening and a reply being composed. Cache the opt-out lookup for at most 60 seconds; longer caching reintroduces the propagation lag.

## Error Handling

| HTTP Status | Podium Error | Root Cause | Action |
|---|---|---|---|
| `400 Bad Request` | `invalid_phone_format` | Phone not in E.164 | Normalize at the widget before submit |
| `400 Bad Request` | `invalid_location_uid` | Unknown or wrong-format location_uid | Reload the locations list; validate before submit |
| `409 Conflict` | `contact_already_exists` | Race lost on contact creation | Refetch by phone; return the winner |
| `413 Payload Too Large` | `attachment_exceeds_limit` | Attachment > 25 MiB | Validate client-side before upload |
| `429 Too Many Requests` | `rate_limited` | Burst exceeded Podium per-location cap | Honor `Retry-After`; see `podium-rate-limit-survival` |
| `451 Unavailable For Legal Reasons` | `contact_opted_out` | Outbound to a STOP'd contact | Block at your handler before the call ever reaches Podium |

## Examples

### Normalize a phone at the widget

```bash
python3 scripts/phone_normalize.py --phone "0412 345 678" --default-country AU
# +61412345678
python3 scripts/phone_normalize.py --phone "(415) 555-1234" --default-country US
# +14155551234
```

### Wire the ingest handler into a FastAPI webhook

```python
from fastapi import FastAPI, Request, HTTPException
from podium_auth import PodiumAuth
from webchat_ingest import process_inbound_webchat

app = FastAPI()
auth = PodiumAuth(...)

@app.post("/podium/webchat")
async def webchat_webhook(req: Request):
    payload = await req.json()
    try:
        await process_inbound_webchat(payload, auth)
    except WebchatError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"status": "ok"}
```

### Idle-session scan as a background task

```python
import asyncio
from webchat_ingest import sessions, scan_sessions

async def session_loop():
    while True:
        await scan_sessions(sessions)
        await asyncio.sleep(60)

# In your app startup
asyncio.create_task(session_loop())
```

### Audit opt-out propagation for a phone

```bash
python3 scripts/optout_audit.py --phone "+61412345678"
```

Output:

```json
{
  "phone": "+61412345678",
  "optout_store": {"opted_out": true, "source": "sms", "recorded_at": 1746000000},
  "podium_contact": {"opted_out": true},
  "consistent": true
}
```

## Output

- E.164 normalization helper invoked at the widget input boundary
- Idempotent contact upsert with race-tolerant 409 handling
- Webchat session timeout monitor with partial-state buffering
- Client-side attachment size validation (≤ 25 MiB)
- `location_uid` validation against a startup-loaded valid set (no default fallback)
- Unified opt-out store consulted on every outbound across SMS + webchat

## Resources

- [Podium API docs — Webchat](https://docs.podium.com/reference/webchat)
- [Podium API docs — Contacts](https://docs.podium.com/reference/contacts)
- [Podium API docs — Locations](https://docs.podium.com/reference/locations)
- [Google libphonenumber](https://github.com/google/libphonenumber) — the canonical phone parser/validator
- [phonenumbers (Python port)](https://pypi.org/project/phonenumbers/)
- [config/settings.yaml](config/settings.yaml) — session timeouts, attachment limits, opt-out keywords, default country
- [references/errors.md](references/errors.md) — ERR_WEBCHAT_* codes with cause + solution
- [references/examples.md](references/examples.md) — 10 worked examples (ingest, dedup, routing, opt-out)
- [references/implementation.md](references/implementation.md) — Node.js equivalents, FastAPI wiring, opt-out store schema
- [scripts/phone_normalize.py](scripts/phone_normalize.py) — CLI: normalize a phone to E.164 with carrier metadata
- [scripts/webchat_ingest.py](scripts/webchat_ingest.py) — FastAPI handler for webchat events
- [scripts/session_timeout_monitor.py](scripts/session_timeout_monitor.py) — CLI: scan in-flight sessions
- [scripts/optout_audit.py](scripts/optout_audit.py) — CLI: confirm opt-out flag across all layers
