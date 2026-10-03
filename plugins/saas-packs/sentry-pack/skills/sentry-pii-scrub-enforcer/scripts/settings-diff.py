#!/usr/bin/env python3
"""Diff project settings or SDK inits against a written scrub standard.

Flags dirty projects only. Does not restate tracesSampler decision order.
Does not apply settings. Read-only client; refuse_write on --apply.
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
from sentry_readonly import SentryReadOnlyError, client_from_env  # noqa: E402

# Compared as equality when the standard contains the key.
SCRUB_KEYS = (
    "sendDefaultPii",
    "dataScrubber",
    "scrubIPAddresses",
    "maskAllText",
    "blockAllMedia",
    "networkDetailAllowUrls",
    "networkCaptureBodies",
)
# Present in standard → project must include every listed string.
LIST_KEYS = ("sensitiveFields", "scrubFields")
# Numeric sample fields. Drift is reported; sampling ORDER is not evaluated.
SAMPLE_KEYS = ("tracesSampleRate", "profilesSampleRate", "sampleRate", "replaysSessionSampleRate")


def _load(path: str) -> Any:
    if path == "-":
        raw = sys.stdin.read()
    else:
        candidate = Path(path)
        raw = candidate.read_text(encoding="utf-8") if candidate.is_file() else path
    return json.loads(raw)


def _projects(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        rows = payload
    elif isinstance(payload, dict) and isinstance(payload.get("projects"), list):
        rows = payload["projects"]
    elif isinstance(payload, dict) and ("slug" in payload or "project" in payload or "settings" in payload):
        rows = [payload]
    else:
        raise SystemExit("projects JSON must be a list or {projects: [...]}")
    out = []
    for row in rows:
        if not isinstance(row, dict):
            raise SystemExit("each project must be an object")
        settings = row.get("settings") if isinstance(row.get("settings"), dict) else {
            k: v for k, v in row.items() if k not in {"slug", "project", "name"}
        }
        slug = str(row.get("slug") or row.get("project") or row.get("name") or "unknown")
        out.append({"slug": slug, "settings": settings})
    return out


def _diff_one(slug: str, settings: dict[str, Any], standard: dict[str, Any]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for key in SCRUB_KEYS:
        if key not in standard or key not in settings:
            continue
        if settings[key] != standard[key]:
            findings.append(
                {
                    "project": slug,
                    "key": key,
                    "found": settings[key],
                    "expected": standard[key],
                    "kind": "scrub",
                }
            )
    for key in LIST_KEYS:
        if key not in standard or key not in settings:
            continue
        expected = set(standard[key] or [])
        found = set(settings[key] or [])
        missing = sorted(expected - found)
        if missing:
            findings.append(
                {
                    "project": slug,
                    "key": key,
                    "missing": missing,
                    "kind": "scrub",
                }
            )
    for key in SAMPLE_KEYS:
        if key not in standard or key not in settings:
            continue
        if settings[key] != standard[key]:
            findings.append(
                {
                    "project": slug,
                    "key": key,
                    "found": settings[key],
                    "expected": standard[key],
                    "kind": "sample-rate",
                    "order": "not evaluated — owner is quota volume-cutter sampler-and-filters",
                }
            )
    # tracesSampler presence is a flag, not an order rewrite.
    if "tracesSampler" in settings and settings["tracesSampler"] not in (None, False, ""):
        if standard.get("tracesSampler") in (None, False, "absent") or "tracesSampler" not in standard:
            findings.append(
                {
                    "project": slug,
                    "key": "tracesSampler",
                    "found": "present",
                    "kind": "sample-rate",
                    "order": "not restated",
                }
            )
    return findings


def main() -> None:
    parser = argparse.ArgumentParser(description="Scrub/sample settings drift")
    parser.add_argument("--projects", help="JSON file or - for stdin")
    parser.add_argument("--standard", help="Written standard JSON")
    parser.add_argument("--project", help="Live slug via read-only client (advisory if no token)")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    client = client_from_env()
    if args.apply:
        try:
            client.refuse_write("project scrub settings update")
        except SentryReadOnlyError as exc:
            print(json.dumps({"applied": False, "refused": str(exc)}))
            raise SystemExit(3) from exc

    if args.projects:
        payload = _load(args.projects)
        mode = "advisory"
    elif args.project:
        try:
            payload = client.fetch_project_settings(args.project)
            mode = "live"
        except SentryReadOnlyError as exc:
            raise SystemExit(f"advisory required: {exc}") from exc
    else:
        raise SystemExit("pass --projects or --project")

    standard: dict[str, Any] = {}
    if args.standard:
        loaded = _load(args.standard)
        if not isinstance(loaded, dict):
            raise SystemExit("standard must be an object")
        standard = loaded.get("settings", loaded) if isinstance(loaded.get("settings"), dict) else loaded

    rows = _projects(payload)
    findings: list[dict[str, Any]] = []
    for row in rows:
        findings.extend(_diff_one(row["slug"], row["settings"], standard))
    dirty = sorted({f["project"] for f in findings})
    report = {
        "mode": "advisory" if client.advisory or mode == "advisory" else mode,
        "dirty_projects": dirty,
        "clean_projects": [r["slug"] for r in rows if r["slug"] not in dirty],
        "findings": findings,
        "sampling_order_restated": False,
        "applied": False,
        "writes": "none",
        "recommends_not_applies": True,
    }
    json.dump(report, sys.stdout, indent=2)
    sys.stdout.write("\n")
    raise SystemExit(2 if dirty else 0)


if __name__ == "__main__":
    main()
