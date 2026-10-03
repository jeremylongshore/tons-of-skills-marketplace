#!/usr/bin/env python3
"""webhook_server.py — FastAPI receiver for Podium webhooks with the full reliability pipeline.

Pipeline: signature verify → replay window → JSON parse → dedup claim → batch sort →
safe dispatch (try/except → DLQ).

Run:
  export PODIUM_WEBHOOK_SECRET={your-webhook-secret}
  export REDIS_URL=redis://localhost:6379/0
  uvicorn scripts.webhook_server:app --host 0.0.0.0 --port 8080

Endpoints:
  POST /webhooks/podium   — receive a webhook delivery
  GET  /healthz            — health probe (returns dedup backend status)
"""

from __future__ import annotations
import hmac
import hashlib
import json
import os
import re
import sys
import time
import logging
from typing import Any

from fastapi import FastAPI, Request, HTTPException, Header

try:
    import redis.asyncio as redis_async

    _HAS_REDIS = True
except ImportError:
    _HAS_REDIS = False

REPLAY_WINDOW_SECONDS = int(os.environ.get("PODIUM_REPLAY_WINDOW", "300"))
DEDUP_TTL_SECONDS = int(os.environ.get("PODIUM_DEDUP_TTL", "86400"))
KEY_PREFIX = "podium:evt:"
DLQ_KEY = "podium:dlq"

SECRET_BYTES: bytes = os.environ.get("PODIUM_WEBHOOK_SECRET", "").encode("utf-8")
if not SECRET_BYTES:
    print("FATAL: PODIUM_WEBHOOK_SECRET not set", file=sys.stderr)
    # Do not exit at import time — let healthz expose the misconfiguration

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

logging.basicConfig(level=logging.INFO, format='{"ts": "%(asctime)s", "lvl": "%(levelname)s", "msg": "%(message)s"}')
log = logging.getLogger("podium-webhook")

_LOG_CONTROL_CHARS_RE = re.compile(r"[\r\n\x00-\x1f\x7f]")


def safe_log_value(value: object) -> str:
    """Strip CR/LF and other control characters from a value before it is
    interpolated into a log message. Webhook payload fields (event type, event
    id) are attacker-influenced even when the request signature is valid, so
    they must never reach the logger unsanitized (CodeQL py/log-injection)."""
    # Explicit CR/LF removal first: CodeQL models str.replace of newlines as a
    # log-injection sanitizer but not a regex substitution. The regex then
    # strips the remaining control characters.
    text = str(value).replace("\r", "").replace("\n", "")
    return _LOG_CONTROL_CHARS_RE.sub("", text)


app = FastAPI()

_redis_client: Any = None
_memory_dedup: dict[str, float] = {}
_memory_dlq: list[dict] = []


async def _get_redis():
    global _redis_client
    if _redis_client is None and _HAS_REDIS:
        _redis_client = redis_async.from_url(REDIS_URL, decode_responses=True)
    return _redis_client


def verify_signature(body: bytes, header_value: str) -> tuple[bool, str | None]:
    """Returns (is_valid, timestamp_str). Constant-time compare via hmac.compare_digest."""
    if not header_value or not SECRET_BYTES:
        return False, None
    parts: dict[str, str] = {}
    for p in header_value.split(","):
        if "=" in p:
            k, v = p.split("=", 1)
            parts[k.strip()] = v.strip()
    ts, sig = parts.get("t"), parts.get("v1")
    if not ts or not sig:
        return False, None
    signed_payload = f"{ts}.".encode("utf-8") + body
    expected = hmac.new(SECRET_BYTES, signed_payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, sig), ts


def within_replay_window(ts_str: str | None, window: int = REPLAY_WINDOW_SECONDS) -> bool:
    if not ts_str:
        return False
    try:
        ts = int(ts_str)
    except (TypeError, ValueError):
        return False
    return abs(time.time() - ts) <= window


async def claim_event(event_id: str) -> bool:
    """Atomic dedup claim. Returns True on first sight, False on duplicate.
    Raises on backend unavailable — caller decides fail-open vs fail-closed."""
    r = await _get_redis()
    if r is not None:
        try:
            res = await r.set(f"{KEY_PREFIX}{event_id}", "1", nx=True, ex=DEDUP_TTL_SECONDS)
            return bool(res)
        except Exception as e:
            log.error(f"ERR_WHK_006 dedup_backend_unavailable: {e}")
            raise
    # Memory fallback — dev only.
    now = time.time()
    expired = [k for k, v in _memory_dedup.items() if v < now]
    for k in expired:
        _memory_dedup.pop(k, None)
    if event_id in _memory_dedup:
        return False
    _memory_dedup[event_id] = now + DEDUP_TTL_SECONDS
    return True


async def dlq_persist(entry: dict) -> None:
    entry["dlq_persisted_at"] = time.time()
    r = await _get_redis()
    if r is not None:
        try:
            await r.lpush(DLQ_KEY, json.dumps(entry))
            return
        except Exception as e:
            log.error(f"ERR_WHK_008 dlq_persist_failed (redis): {e}")
            # fall through to memory backup
    _memory_dlq.append(entry)


async def dispatch(event: dict) -> None:
    """Application-specific. Override in your deployment.
    Default no-op logs the event type."""
    log.info(f"dispatch event_type={safe_log_value(event.get('type'))} event_id={safe_log_value(event.get('id'))}")


async def safe_dispatch(event: dict, raw: bytes, sig_header: str) -> None:
    try:
        await dispatch(event)
    except Exception as e:
        await dlq_persist(
            {
                "event_id": event.get("id"),
                "event_type": event.get("type"),
                "raw_body": raw.decode("utf-8", errors="replace"),
                "signature_header": sig_header,
                "occurred_at": event.get("occurred_at"),
                "received_at": time.time(),
                "exception": f"{type(e).__name__}: {e}",
            }
        )
        raise


@app.post("/webhooks/podium")
async def receive(request: Request, x_podium_signature: str | None = Header(default=None)):
    raw = await request.body()
    if not x_podium_signature:
        raise HTTPException(401, "ERR_WHK_001 missing signature header")

    ok, ts = verify_signature(raw, x_podium_signature)
    if not ok:
        raise HTTPException(401, "ERR_WHK_002 signature mismatch")
    if not within_replay_window(ts):
        raise HTTPException(401, "ERR_WHK_003 replay window exceeded")

    try:
        body = json.loads(raw)
    except json.JSONDecodeError:
        raise HTTPException(400, "ERR_WHK_004 body not parseable")

    events = body.get("events") if isinstance(body, dict) and "events" in body else [body]
    if not isinstance(events, list):
        events = [body]

    # Within-batch ordering by (occurred_at, id) for stable causal order.
    events.sort(key=lambda e: (e.get("occurred_at", 0), e.get("id", "")))

    results = []
    for event in events:
        event_id = event.get("id")
        if not event_id:
            results.append({"status": "skipped_no_id"})
            continue
        try:
            first_sight = await claim_event(event_id)
        except Exception:
            raise HTTPException(503, "ERR_WHK_006 dedup backend unavailable")
        if not first_sight:
            results.append({"event_id": event_id, "status": "duplicate"})
            continue
        await safe_dispatch(event, raw, x_podium_signature)
        results.append({"event_id": event_id, "status": "ok"})
    return {"results": results}


@app.get("/healthz")
async def healthz():
    r = await _get_redis()
    backend = "redis" if r else "memory"
    redis_ok: bool | None = None
    if r is not None:
        try:
            await r.ping()
            redis_ok = True
        except Exception:
            redis_ok = False
    return {
        "ok": True,
        "secret_loaded": bool(SECRET_BYTES),
        "dedup_backend": backend,
        "redis_ok": redis_ok,
    }
