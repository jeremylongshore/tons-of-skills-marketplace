#!/usr/bin/env python3
"""List Sentry scrub hooks near Sentry.init. Local files only. No network.

Does not apply a patch. --apply is refused by the shared read-only client.
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

HOOKS = (
    "beforeSendTransaction",
    "beforeSendSpan",
    "beforeSendLog",
    "beforeSendMetric",
    "beforeSend",
    "beforeBreadcrumb",
)
SKIP = {".git", "node_modules", "dist", "build", ".venv", "venv", "__pycache__"}
INIT = re.compile(r"Sentry\.init\s*\(")
PII_TRUE = re.compile(r"sendDefaultPii\s*:\s*true")
PII_FALSE = re.compile(r"sendDefaultPii\s*:\s*false")
REPLAY = re.compile(r"replayIntegration|sentryReplayIntegration|maskAllText|sentry-unmask")
NULL_RETURN = re.compile(r"beforeSend\s*:\s*(?:\(\)\s*=>\s*null|function\s*\([^)]*\)\s*\{\s*return\s+null)")


def scan_text(text: str) -> dict:
    hooks = {name: (name in text) for name in HOOKS}
    # beforeSendTransaction contains the substring beforeSend; already recorded separately.
    return {
        "hooks": hooks,
        "sendDefaultPii": True if PII_TRUE.search(text) else False if PII_FALSE.search(text) else None,
        "replay_markers": bool(REPLAY.search(text)),
        "beforeSend_returns_null": bool(NULL_RETURN.search(text)),
        "has_init": bool(INIT.search(text)),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Scrub hook coverage")
    parser.add_argument("--root", help="Repo or file to scan")
    parser.add_argument("--pasted", help="Raw source string")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    client = client_from_env()
    if args.apply:
        try:
            client.refuse_write("SDK scrub patch")
        except SentryReadOnlyError as exc:
            print(json.dumps({"applied": False, "refused": str(exc)}))
            raise SystemExit(3) from exc
    files: list[dict] = []
    if args.pasted:
        files.append({"file": "<pasted>", **scan_text(args.pasted)})
    elif args.root:
        root = Path(args.root)
        paths = [root] if root.is_file() else list(root.rglob("*"))
        for path in paths:
            if not path.is_file():
                continue
            if any(part in SKIP for part in path.parts):
                continue
            if path.suffix.lower() not in {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".py", ".rb", ".java", ".kt"}:
                continue
            if path.stat().st_size > 1_000_000:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            if "Sentry" not in text and "sentry" not in text:
                continue
            row = scan_text(text)
            if row["has_init"] or row["replay_markers"] or any(row["hooks"].values()):
                files.append({"file": str(path), **row})
    else:
        raise SystemExit("pass --root or --pasted")
    replay_on = any(f["replay_markers"] for f in files)
    nulls = [f["file"] for f in files if f["beforeSend_returns_null"]]
    json.dump(
        {
            "files": files,
            "replay_on": replay_on,
            "spawn_replay_privacy": replay_on,
            "beforeSend_covers_replay": False,
            "null_beforeSend_files": nulls,
            "null_beforeSend_is_outage": bool(nulls),
            "applied": False,
            "writes": "none",
            "recommends_not_applies": True,
        },
        sys.stdout,
        indent=2,
    )
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
