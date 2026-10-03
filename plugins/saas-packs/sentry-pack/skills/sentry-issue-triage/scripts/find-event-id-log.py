#!/usr/bin/env python3
"""Search a repo for code that writes a Sentry event id into logs.

Does not call Sentry. Does not install an APM. If nothing matches, say so.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

NEEDLES = (
    "event_id",
    "event.event_id",
    "eventId",
    "sentry.event_id",
    "last_event_id",
    "Sentry.lastEventId",
)
SKIP_DIRS = {".git", "node_modules", "dist", "build", ".venv", "venv", "__pycache__"}


def scan(root: Path) -> list[dict[str, str]]:
    hits: list[dict[str, str]] = []
    if not root.exists():
        return hits
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.suffix.lower() not in {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".py", ".rb", ".go", ".java", ".kt"}:
            continue
        if path.stat().st_size > 1_000_000:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for i, line in enumerate(text.splitlines(), 1):
            if any(n in line for n in NEEDLES):
                hits.append({"file": str(path), "line": str(i), "text": line.strip()[:240]})
                if len(hits) >= 40:
                    return hits
    return hits


def main() -> None:
    parser = argparse.ArgumentParser(description="Find event id log writes")
    parser.add_argument("--root", required=True)
    parser.add_argument("--event-id", default="")
    args = parser.parse_args()
    root = Path(args.root)
    hits = scan(root)
    event_id = args.event_id.strip()
    if hits:
        field = "event_id"
        query = f'{field}:"{event_id}"' if event_id else f"{field}:<event id from the issue>"
        verdict = "log query possible"
    else:
        query = None
        verdict = "codebase never writes it"
    json.dump(
        {
            "verdict": verdict,
            "event_id": event_id or None,
            "query": query,
            "hits": hits,
            "datadog_install": False,
            "writes": "none",
        },
        sys.stdout,
        indent=2,
    )
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
