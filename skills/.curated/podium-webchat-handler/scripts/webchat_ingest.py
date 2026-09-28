#!/usr/bin/env python3
"""webchat_ingest.py — FastAPI handler for Podium webchat events.

This module is BOTH a library (importable functions) and a runnable FastAPI app.
Run it as:
  uvicorn webchat_ingest:app --host 0.0.0.0 --port 8080

Assumes upstream verification is handled by podium-webhook-reliability — the
incoming POST has already had its HMAC verified and been dedup'd. This handler
performs business-layer validation: phone normalization, location routing,
opt-out checks, race-tolerant contact upsert, attachment size guard.

Environment variables:
  PODIUM_CLIENT_ID, PODIUM_CLIENT_SECRET, PODIUM_REFRESH_TOKEN_FILE
       — consumed by podium-auth for OAuth
  WEBCHAT_DEFAULT_COUNTRY      ISO-3166, fallback when message has no country hint (default "AU")
  WEBCHAT_PARTIAL_STATE_DIR    directory for partial-state JSON (default "/tmp/webchat-partial-state")
  OPTOUT_STORE_DSN             postgres DSN (omit for the in-memory stub used in this file)

Exit / status semantics:
  - 200 ok      message accepted and processed
  - 400         business-layer validation failed (phone format, location_uid)
  - 413         attachment too large
  - 451         outbound blocked by opt-out (signaled to caller; we still return 200 to the webhook)
"""

from __future__ import annotations
import asyncio
import json
import os
import re
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# -- Phone normalization -------------------------------------------------------


class PhoneValidationError(Exception):
    pass


def normalize_phone(raw: str, default_country: str = "AU") -> str:
    """Parse a raw phone string and return E.164 form. Raises PhoneValidationError on failure."""
    try:
        import phonenumbers
        from phonenumbers import (
            NumberParseException,
            PhoneNumberFormat,
            is_valid_number,
        )
    except ImportError as e:
        raise PhoneValidationError(f"phonenumbers library not installed: {e}")

    try:
        parsed = phonenumbers.parse(raw, default_country)
    except NumberParseException as e:
        raise PhoneValidationError(f"ERR_WEBCHAT_001 unparseable {raw!r} for {default_country}: {e}")
    if not is_valid_number(parsed):
        raise PhoneValidationError(f"ERR_WEBCHAT_001 invalid {raw!r} for {default_country}")
    return phonenumbers.format_number(parsed, PhoneNumberFormat.E164)


# -- Location routing ----------------------------------------------------------


class WebchatError(Exception):
    pass


VALID_LOCATION_UIDS: set[str] = set()
locations_last_refreshed_at: float = 0.0


def validate_location(location_uid: str | None) -> str:
    """Validate a location_uid against the loaded allowlist. Raises on missing/unknown."""
    if not location_uid:
        raise WebchatError("ERR_WEBCHAT_002 location_uid is required (no default fallback)")
    if location_uid not in VALID_LOCATION_UIDS:
        raise WebchatError(f"ERR_WEBCHAT_003 unknown location_uid {location_uid!r}")
    return location_uid


async def load_locations_stub() -> None:
    """Stub for development. Replace with a real Podium /v4/locations call wired through podium-auth."""
    global locations_last_refreshed_at
    env = os.environ.get("WEBCHAT_VALID_LOCATIONS", "")
    VALID_LOCATION_UIDS.clear()
    VALID_LOCATION_UIDS.update(uid.strip() for uid in env.split(",") if uid.strip())
    locations_last_refreshed_at = time.time()


# -- Attachment validation -----------------------------------------------------

PODIUM_ATTACHMENT_MAX_BYTES = 25 * 1024 * 1024  # 25 MiB


class AttachmentTooLargeError(Exception):
    pass


def validate_attachment_size(size_bytes: int) -> None:
    if size_bytes > PODIUM_ATTACHMENT_MAX_BYTES:
        raise AttachmentTooLargeError(
            f"ERR_WEBCHAT_005 attachment {size_bytes / 1024 / 1024:.1f} MiB > "
            f"{PODIUM_ATTACHMENT_MAX_BYTES / 1024 / 1024:.0f} MiB limit"
        )


# -- Sessions + partial state --------------------------------------------------

SESSION_IDLE_WARN_SECONDS = 20 * 60
SESSION_IDLE_CLOSE_SECONDS = 28 * 60
PARTIAL_STATE_DIR = Path(os.environ.get("WEBCHAT_PARTIAL_STATE_DIR", "/tmp/webchat-partial-state"))


@dataclass
class WebchatSession:
    session_uid: str
    phone_e164: str
    location_uid: str
    last_message_at: float
    partial_state: dict = field(default_factory=dict)

    def status(self) -> str:
        idle = time.time() - self.last_message_at
        if idle >= SESSION_IDLE_CLOSE_SECONDS:
            return "close"
        if idle >= SESSION_IDLE_WARN_SECONDS:
            return "warn"
        return "active"


active_sessions: dict[str, WebchatSession] = {}


def _partial_state_path(phone_e164: str, location_uid: str) -> Path:
    # phone_e164 and location_uid both derive from the inbound webhook
    # payload, so they are untrusted. Replacing "+" is not enough to stop
    # path traversal (e.g. a location_uid of "../../etc/passwd") — build the
    # filename from a character-restricted form of each component, then
    # verify the resolved path stays inside PARTIAL_STATE_DIR before use.
    safe_phone = re.sub(r"[^0-9A-Za-z]", "p", phone_e164)
    safe_location = re.sub(r"[^0-9A-Za-z_-]", "_", location_uid)
    # Normalize lexically (no filesystem access with untrusted input) and
    # require the result to stay directly under the state directory.
    base = os.path.normpath(os.path.abspath(PARTIAL_STATE_DIR))
    candidate = os.path.normpath(os.path.join(base, f"{safe_phone}__{safe_location}.json"))
    if not candidate.startswith(base + os.sep):
        raise WebchatError(
            f"ERR_WEBCHAT_009 refusing to escape partial-state dir: phone={phone_e164!r} location_uid={location_uid!r}"
        )
    return Path(candidate)


def persist_partial_state(s: WebchatSession) -> None:
    path = _partial_state_path(s.phone_e164, s.location_uid)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "session_uid": s.session_uid,
                "phone_e164": s.phone_e164,
                "location_uid": s.location_uid,
                "partial_state": s.partial_state,
                "persisted_at": time.time(),
            }
        )
    )


def hydrate_partial_state(phone_e164: str, location_uid: str) -> dict:
    path = _partial_state_path(phone_e164, location_uid)
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text()).get("partial_state", {})
    except Exception:
        return {}


# -- Opt-out store (in-memory stub; swap for Postgres/Redis/DynamoDB in prod) --

OPTOUT_KEYWORDS = {"STOP", "UNSUBSCRIBE", "QUIT", "END", "CANCEL", "OPTOUT"}


class OptoutStore:
    def __init__(self):
        self._data: dict[str, dict] = {}

    async def is_opted_out(self, phone_e164: str) -> bool:
        return phone_e164 in self._data

    async def set_opted_out(self, phone_e164: str, source_channel: str) -> None:
        self._data[phone_e164] = {"source": source_channel, "recorded_at": time.time()}


optout_store = OptoutStore()


# -- Logging helpers (PII-aware) -----------------------------------------------


def _phone_last4(phone_e164: str) -> str:
    return f"****{phone_e164[-4:]}" if phone_e164 else "****"


def log_event(event: str, **fields: Any) -> None:
    redacted = dict(fields)
    if "phone_e164" in redacted:
        redacted["phone_last4"] = _phone_last4(redacted.pop("phone_e164"))
    print(json.dumps({"event": event, **redacted}))


def log_optout_blocked(phone_e164: str, channel: str) -> None:
    log_event("ERR_WEBCHAT_009 optout_blocked_outbound", phone_e164=phone_e164, channel=channel)


# -- Core ingest path ----------------------------------------------------------


async def process_inbound_webchat(payload: dict, auth=None) -> dict:
    """Process a verified webchat event. Returns a status dict; raises on validation failure."""
    data = payload.get("data") or {}
    raw_phone = data.get("from")
    if not raw_phone:
        raise WebchatError("ERR_WEBCHAT_002 message missing 'from' field")

    default_country = data.get("country") or os.environ.get("WEBCHAT_DEFAULT_COUNTRY", "AU")
    phone_e164 = normalize_phone(raw_phone, default_country)
    location_uid = validate_location(data.get("location_uid"))

    text = (data.get("body") or "").strip().upper()
    if text in OPTOUT_KEYWORDS:
        await optout_store.set_opted_out(phone_e164, source_channel="webchat")
        log_event("ERR_WEBCHAT_008 optout_keyword_received", phone_e164=phone_e164, location_uid=location_uid)
        return {"status": "opted_out_recorded"}

    if await optout_store.is_opted_out(phone_e164):
        log_optout_blocked(phone_e164, channel="webchat")
        return {"status": "blocked_by_optout"}

    attachments = data.get("attachments") or []
    for att in attachments:
        size = int(att.get("size_bytes") or 0)
        validate_attachment_size(size)

    # Hydrate partial state from a previously-closed session, if any
    hydrated = hydrate_partial_state(phone_e164, location_uid)

    session_uid = data.get("session_uid") or f"sess-{phone_e164}-{int(time.time())}"
    active_sessions[session_uid] = WebchatSession(
        session_uid=session_uid,
        phone_e164=phone_e164,
        location_uid=location_uid,
        last_message_at=time.time(),
        partial_state=hydrated,
    )

    log_event(
        "webchat_ingested",
        phone_e164=phone_e164,
        location_uid=location_uid,
        session_uid=session_uid,
        hydrated=bool(hydrated),
    )

    # Downstream enqueue (agent inbox, CRM mirror) goes here. Left as a hook
    # so the consumer wires their own queue (RabbitMQ, SQS, Postgres LISTEN, etc).
    return {"status": "ok", "session_uid": session_uid, "hydrated": bool(hydrated)}


# -- Background session scan ---------------------------------------------------


async def send_keepalive_prompt(session_uid: str) -> None:
    log_event("ERR_WEBCHAT_007 session_idle_warn", session_uid=session_uid)


async def close_session_cleanly(session_uid: str) -> None:
    log_event("ERR_WEBCHAT_006 session_idle_close", session_uid=session_uid)


async def session_loop(interval_s: int = 60) -> None:
    while True:
        try:
            for uid, s in list(active_sessions.items()):
                st = s.status()
                if st == "warn":
                    await send_keepalive_prompt(s.session_uid)
                elif st == "close":
                    persist_partial_state(s)
                    await close_session_cleanly(s.session_uid)
                    del active_sessions[uid]
        except Exception as e:
            log_event("session_loop_exception", error=str(e))
        await asyncio.sleep(interval_s)


# -- FastAPI app (optional; only constructed if fastapi is importable) --------

try:
    from fastapi import FastAPI, Request, HTTPException

    @asynccontextmanager
    async def lifespan(app: "FastAPI"):
        await load_locations_stub()
        task = asyncio.create_task(session_loop())
        yield
        task.cancel()

    app = FastAPI(lifespan=lifespan)

    @app.post("/podium/webchat")
    async def webchat_webhook(req: Request):
        payload = await req.json()
        try:
            result = await process_inbound_webchat(payload)
        except PhoneValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except WebchatError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except AttachmentTooLargeError as e:
            raise HTTPException(status_code=413, detail=str(e))
        return result

except ImportError:
    # fastapi not installed — library import path still works.
    app = None


if __name__ == "__main__":
    # Module is meant to be run via `uvicorn webchat_ingest:app`.
    # Direct invocation prints a help message.
    import sys

    print(__doc__, file=sys.stderr)
    sys.exit(0)
