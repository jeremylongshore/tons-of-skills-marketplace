#!/usr/bin/env python3
"""Redact secrets from a support-bundle draft.

debug-bundler must not print sntrys_ tokens or SENTRY_AUTH_TOKEN values.
DSN host may remain; the raw auth token may not. Read-only.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

_LIB = Path(__file__).resolve().parents[3] / "scripts" / "lib"
if _LIB.is_dir() and str(_LIB) not in sys.path:
    sys.path.insert(0, str(_LIB))

from sentry_readonly import SentryReadOnlyError, client_from_env  # noqa: E402

SNTRYS = re.compile(r"sntrys_[A-Za-z0-9._\-]+")
AUTH_ASSIGN = re.compile(
    r"(SENTRY_AUTH_TOKEN\s*[=:]\s*)(\S+)",
    re.IGNORECASE,
)
BEARER = re.compile(r"(Authorization:\s*Bearer\s+)(\S+)", re.IGNORECASE)


def redact(text: str) -> tuple[str, dict[str, int]]:
    counts = {"sntrys": 0, "auth_token_assign": 0, "bearer": 0}

    def sn(m: re.Match[str]) -> str:
        counts["sntrys"] += 1
        return "[REDACTED_SNTRYS]"

    def auth(m: re.Match[str]) -> str:
        counts["auth_token_assign"] += 1
        return m.group(1) + "[REDACTED]"

    def bearer(m: re.Match[str]) -> str:
        counts["bearer"] += 1
        return m.group(1) + "[REDACTED]"

    text = SNTRYS.sub(sn, text)
    text = AUTH_ASSIGN.sub(auth, text)
    text = BEARER.sub(bearer, text)
    return text, counts


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", help="Optional pasted bundle text path, or '-' for stdin.")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    client = client_from_env()
    if args.apply:
        try:
            client.refuse_write("upload support bundle to Sentry")
        except SentryReadOnlyError as exc:
            print(json.dumps({"ok": False, "wrote": False, "error": str(exc)}))
            return 2
    if args.json:
        raw = sys.stdin.read() if args.json == "-" else Path(args.json).read_text()
    else:
        raw = sys.stdin.read()
    cleaned, counts = redact(raw)
    leftovers = [
        name
        for name, rx in (("sntrys_", SNTRYS), ("SENTRY_AUTH_TOKEN", AUTH_ASSIGN), ("Bearer", BEARER))
        if rx.search(cleaned) and not all(m.group(0).endswith("[REDACTED]") for m in rx.finditer(cleaned))
    ]
    if leftovers:
        print(json.dumps({"ok": False, "error": f"redaction failed; still present: {leftovers}"}))
        return 2
    print(
        json.dumps(
            {
                "ok": True,
                "wrote": False,
                "redactions": counts,
                "contains_sntrys": False,
                "text": cleaned,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
