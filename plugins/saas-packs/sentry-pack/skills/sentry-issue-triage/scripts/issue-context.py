#!/usr/bin/env python3
"""Extract severity inputs from a Sentry issue or event JSON.

Reads pasted JSON or, when implemented, the shared read-only client.
Does not invent timestamps, releases, or counts. Does not write.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

_LIB = Path(__file__).resolve().parents[3] / "scripts" / "lib"
if _LIB.is_dir() and str(_LIB) not in sys.path:
    sys.path.insert(0, str(_LIB))
from sentry_readonly import SentryReadOnlyClient, SentryReadOnlyError, client_from_env  # noqa: E402


def _int(value: Any) -> int:
    if value is None or value == "":
        return 0
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _tag(data: dict[str, Any], key: str) -> str | None:
    tags = data.get("tags")
    if isinstance(tags, dict):
        val = tags.get(key)
        return str(val) if val else None
    if isinstance(tags, list):
        for item in tags:
            if isinstance(item, dict) and item.get("key") == key and item.get("value"):
                return str(item["value"])
            if isinstance(item, (list, tuple)) and len(item) == 2 and item[0] == key and item[1]:
                return str(item[1])
    return None


def _release(data: dict[str, Any]) -> str | None:
    for candidate in (
        data.get("release"),
        (data.get("release") or {}).get("version") if isinstance(data.get("release"), dict) else None,
        _tag(data, "release"),
    ):
        if isinstance(candidate, str) and candidate.strip():
            return candidate.strip()
    return None


def _environment(data: dict[str, Any]) -> str | None:
    env = data.get("environment") or _tag(data, "environment")
    if isinstance(env, str) and env.strip():
        return env.strip()
    return None


def severity(data: dict[str, Any]) -> dict[str, Any]:
    """Rubric shared with references/severity-rubric.md. First match wins."""
    status = str(data.get("status") or "unresolved").lower()
    level = str(data.get("level") or data.get("metadata", {}).get("level") or "").lower()
    users = _int(data.get("userCount") if "userCount" in data else data.get("user_count"))
    count = _int(data.get("count"))
    env = (_environment(data) or "").lower()
    prod = env in {"production", "prod"}

    if status in {"resolved", "ignored"}:
        sev, why = "SEV-4", f"status is {status}; not an active page"
    elif level == "fatal" or (level == "error" and users >= 100) or (
        level == "error" and count >= 1000 and prod
    ):
        sev, why = "SEV-1", "fatal, or error with userCount>=100, or prod error with count>=1000"
    elif level == "error" or users >= 10 or count >= 100:
        sev, why = "SEV-2", "error, or userCount>=10, or count>=100"
    elif level == "warning":
        sev, why = "SEV-3", "warning below the SEV-2 counts"
    else:
        sev, why = "SEV-4", "info/debug/unknown level below the count gates"

    release = _release(data)
    first = data.get("firstSeen") or data.get("first_seen")
    last = data.get("lastSeen") or data.get("last_seen")
    event_ts = data.get("dateCreated") or data.get("timestamp")
    timeline = [t for t in (first, last, event_ts) if isinstance(t, str) and t]
    return {
        "severity": sev,
        "severity_reason": why,
        "status": status,
        "level": level or None,
        "userCount": users,
        "count": count,
        "environment": _environment(data),
        "suspect_release": release,
        "suspect_release_note": None
        if release
        else "unknown — do not invent a release",
        "timeline_timestamps": timeline,
        "postmortem_times_rule": "use only timeline_timestamps; do not invent times",
        "filtered_plus_dropped": "do not sum; this script does not read stats",
    }


def load_payload(args: argparse.Namespace, client: SentryReadOnlyClient) -> tuple[dict[str, Any], str]:
    if args.pasted:
        raw = Path(args.pasted).read_text(encoding="utf-8") if Path(args.pasted).is_file() else args.pasted
        if raw == "-":
            raw = sys.stdin.read()
        return client.fetch_event_json("pasted", pasted=raw), "advisory"
    if args.event_id:
        try:
            return client.fetch_event_json(args.event_id), "live"
        except SentryReadOnlyError as exc:
            raise SystemExit(f"advisory required: {exc}") from exc
    raise SystemExit("pass --pasted <file|json|-> or --event-id")


def main() -> None:
    parser = argparse.ArgumentParser(description="Issue severity from payload only")
    parser.add_argument("--pasted", help="JSON file, raw JSON, or - for stdin")
    parser.add_argument("--event-id", help="Live read via sentry_readonly (no write)")
    parser.add_argument("--apply", action="store_true", help="Rejected")
    args = parser.parse_args()
    client = client_from_env()
    if args.apply:
        client.refuse_write("issue status update")
    data, mode = load_payload(args, client)
    out = severity(data)
    out["mode"] = "advisory" if client.advisory or mode == "advisory" else mode
    out["writes"] = "none"
    json.dump(out, sys.stdout, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
