#!/usr/bin/env python3
"""
HTTP layer for the derivatives tracker: live requests, recording and replay.

Every public endpoint the tracker reads goes through `Http`. In live mode it
calls the exchange. With `record_path` set it also saves each raw response.
In replay mode (the `--demo` flag and the test suite) it serves those saved
responses, so recorded data passes through exactly the same parsers as live
data, and the clock is pinned to the recording time.

Standard library only: no API keys, no third-party packages.
"""

from __future__ import annotations

import json
import socket
import threading
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

USER_AGENT = "tracking-crypto-derivatives/2.0 (+https://tonsofskills.com)"


class FetchError(Exception):
    """A request that did not return usable data, with a reason a person can act on."""

    def __init__(self, reason: str, status: Optional[int] = None, body: Any = None):
        super().__init__(reason)
        self.reason = reason
        self.status = status
        self.body = body  # parsed error body when the venue sent JSON, else None


def describe_status(status: int) -> str:
    """Turn an HTTP status into a plain reason."""
    if status == 451:
        return "refused from this network (HTTP 451, region restriction)"
    if status == 403:
        return "refused from this network (HTTP 403, likely a region restriction)"
    if status == 429:
        return "rate limited (HTTP 429); wait and retry"
    if status == 404:
        return "not found (HTTP 404); the symbol may not be listed here"
    if status >= 500:
        return f"exchange error (HTTP {status}); try again later"
    return f"unexpected response (HTTP {status})"


def _key(method: str, url: str, body: Optional[dict]) -> str:
    if body is None:
        return f"{method} {url}"
    return f"{method} {url} {json.dumps(body, sort_keys=True, separators=(',', ':'))}"


@dataclass
class Recording:
    """A saved set of raw responses plus the time they were captured."""

    recorded_at: datetime
    responses: dict
    note: str = ""

    @classmethod
    def load(cls, path: Path) -> "Recording":
        raw = json.loads(Path(path).read_text())
        return cls(
            recorded_at=datetime.fromisoformat(raw["recorded_at"].replace("Z", "+00:00")),
            responses=raw["responses"],
            note=raw.get("note", ""),
        )


class Http:
    """Fetch JSON from public endpoints, optionally recording or replaying."""

    def __init__(
        self,
        timeout: float = 10.0,
        replay: Optional[Recording] = None,
        record_path: Optional[Path] = None,
    ):
        self.timeout = timeout
        self.replay = replay
        self.record_path = Path(record_path) if record_path else None
        self._recorded: dict = {}
        self._lock = threading.Lock()
        # One clock per run, so time-based URLs and "next funding" agree with the recording.
        self._started = replay.recorded_at if replay is not None else datetime.now(timezone.utc)

    @property
    def is_replay(self) -> bool:
        return self.replay is not None

    def now(self) -> datetime:
        """The run's clock: when this run started, or the recording time when replaying."""
        return self._started

    def get_json(self, url: str) -> Any:
        return self._request("GET", url, None)

    def post_json(self, url: str, body: dict) -> Any:
        return self._request("POST", url, body)

    def _request(self, method: str, url: str, body: Optional[dict]) -> Any:
        key = _key(method, url, body)
        if self.replay is not None:
            if key not in self.replay.responses:
                raise FetchError("not in the recorded demo data")
            entry = self.replay.responses[key]
            if entry.get("status", 200) != 200:
                raise FetchError(describe_status(entry["status"]), entry["status"], entry.get("body"))
            return entry["body"]

        data = json.dumps(body).encode() if body is not None else None
        headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
        if data is not None:
            headers["Content-Type"] = "application/json"
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        started = time.monotonic()
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
                self._save(key, 200, payload)
                return payload
        except urllib.error.HTTPError as exc:
            try:
                err_body = json.loads(exc.read().decode("utf-8"))
            except (ValueError, OSError):
                err_body = None
            self._save(key, exc.code, err_body)
            raise FetchError(describe_status(exc.code), exc.code, err_body) from None
        except (urllib.error.URLError, socket.timeout, TimeoutError) as exc:
            elapsed = time.monotonic() - started
            reason = getattr(exc, "reason", exc)
            if isinstance(reason, (socket.timeout, TimeoutError)) or elapsed >= self.timeout:
                raise FetchError(f"timed out after {self.timeout:.0f}s") from None
            raise FetchError(f"network error: {reason}") from None
        except json.JSONDecodeError:
            raise FetchError("response was not JSON") from None

    def _save(self, key: str, status: int, body: Any) -> None:
        if self.record_path is None:
            return
        with self._lock:
            self._recorded[key] = {"status": status, "body": body}

    def write_recording(self, note: str = "") -> None:
        """Write everything fetched in this run to `record_path`."""
        if self.record_path is None:
            return
        doc = {
            "recorded_at": self.now().isoformat().replace("+00:00", "Z"),
            "note": note,
            "responses": dict(sorted(self._recorded.items())),
        }
        # One response per line keeps the file small and its diffs readable.
        lines = [f"  {json.dumps(k)}: {json.dumps(v, separators=(',', ':'))}" for k, v in doc["responses"].items()]
        head = json.dumps({k: doc[k] for k in ("recorded_at", "note")}, indent=1)[:-2]
        self.record_path.write_text(head + ',\n "responses": {\n' + ",\n".join(lines) + "\n }\n}\n")
