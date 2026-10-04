#!/usr/bin/env python3
"""Pull fingerprint, grouping source, and id-like message tokens from one event.

Deterministic. Does not claim a rule restacks existing issues. Does not write.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

_LIB = Path(__file__).resolve().parents[3] / "scripts" / "lib"
if _LIB.is_dir() and str(_LIB) not in sys.path:
    sys.path.insert(0, str(_LIB))
from sentry_readonly import SentryReadOnlyError, client_from_env  # noqa: E402

_UUID = re.compile(r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b")
_DIGITS = re.compile(r"\d{2,}")


def _message(data: dict[str, Any]) -> str:
    msg = data.get("message") or data.get("logentry") or data.get("title") or ""
    if isinstance(msg, dict):
        msg = msg.get("formatted") or msg.get("message") or ""
    return str(msg or "")


def _exception(data: dict[str, Any]) -> tuple[str | None, str | None, bool]:
    exc = data.get("exception") or {}
    values = exc.get("values") if isinstance(exc, dict) else None
    if not values and isinstance(data.get("entries"), list):
        for entry in data["entries"]:
            if isinstance(entry, dict) and entry.get("type") == "exception":
                values = (entry.get("data") or {}).get("values")
                break
    if not isinstance(values, list) or not values:
        return None, None, False
    last = values[-1] if isinstance(values[-1], dict) else {}
    frames = ((last.get("stacktrace") or {}).get("frames")) or []
    return (
        last.get("type") if isinstance(last.get("type"), str) else None,
        last.get("value") if isinstance(last.get("value"), str) else None,
        bool(frames),
    )


def analyze(data: dict[str, Any]) -> dict[str, Any]:
    message = _message(data)
    exc_type, exc_value, has_stack = _exception(data)
    text = " ".join(t for t in (message, exc_value) if t)
    fingerprint = data.get("fingerprint")
    if fingerprint is None:
        fp_list: list[Any] = []
    elif isinstance(fingerprint, list):
        fp_list = fingerprint
    else:
        fp_list = [fingerprint]
    fp_strings = [str(x) for x in fp_list]
    has_default = any(x.strip() == "{{ default }}" for x in fp_strings)
    fully_custom = bool(fp_strings) and not has_default and fp_strings != ["{{ default }}"]
    # SDK default is often the literal "default" or absent — treat absent as built-in.
    if not fp_strings or fp_strings == ["default"]:
        fully_custom = False
        has_default = False
    return {
        "fingerprint": fp_strings,
        "includes_default_placeholder": has_default,
        "fully_custom_fingerprint": fully_custom,
        "ai_grouping_opt_out": fully_custom,
        "exception_type": exc_type,
        "exception_value": exc_value,
        "has_stack": has_stack,
        "message": message,
        "message_has_id_like_token": bool(_UUID.search(text) or _DIGITS.search(text)),
        "grouping_hint": (
            "stack" if has_stack else "exception-or-message" if (exc_type or exc_value or message) else "unknown"
        ),
        "prospective_only": True,
        "backfill": False,
        "note": "Fingerprint and stack-trace rules do not affect issues that already exist (OP04).",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Fingerprint facts from one event")
    parser.add_argument("--pasted", help="JSON file, raw JSON, or - for stdin")
    parser.add_argument("--event-id")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    client = client_from_env()
    if args.apply:
        try:
            client.refuse_write("fingerprint rule update")
        except SentryReadOnlyError as exc:
            print(json.dumps({"ok": False, "wrote": False, "error": str(exc)}))
            return 2
    if args.pasted:
        raw = Path(args.pasted).read_text(encoding="utf-8") if Path(args.pasted).is_file() else args.pasted
        if raw == "-":
            raw = sys.stdin.read()
        data = client.fetch_event_json("pasted", pasted=raw)
        mode = "advisory"
    elif args.event_id:
        try:
            data = client.fetch_event_json(args.event_id)
            mode = "live"
        except SentryReadOnlyError as exc:
            raise SystemExit(f"advisory required: {exc}") from exc
    else:
        raise SystemExit("pass --pasted or --event-id")
    out = analyze(data)
    out["mode"] = "advisory" if client.advisory or mode == "advisory" else mode
    out["writes"] = "none"
    json.dump(out, sys.stdout, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    raise SystemExit(main())
