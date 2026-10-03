#!/usr/bin/env python3
"""Parse event JSON for data.resolved_with and debug_meta.

Scripts own the parse. Agents must not invent matchers.
has debug_meta is not has a matching artifact bundle.
Uploading maps later does not rewrite events already stored.

Read-only. `--apply` is refused.
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

# Help Center "How were my source maps resolved" (RL06). Do not extend.
KNOWN_RESOLVED_WITH = (
    "debug-id",
    "url",
    "index",
    "release",
    "release-old",
    "scraping",
    "unknown",
)

TOKEN_RE = re.compile(r"sntrys_[A-Za-z0-9._\-]+")


def _frames_from_stack(stack: Any) -> list[dict[str, Any]]:
    if not isinstance(stack, dict):
        return []
    frames = stack.get("frames")
    if not isinstance(frames, list):
        return []
    return [f for f in frames if isinstance(f, dict)]


def _walk_exception(values: Any, *, source: str, out: list[dict[str, Any]]) -> None:
    if not isinstance(values, list):
        return
    for index, value in enumerate(values):
        if not isinstance(value, dict):
            continue
        for which, key in (("stacktrace", "stacktrace"), ("raw_stacktrace", "raw_stacktrace")):
            for frame_i, frame in enumerate(_frames_from_stack(value.get(key))):
                data = frame.get("data") if isinstance(frame.get("data"), dict) else {}
                resolved = data.get("resolved_with")
                out.append({
                    "source": source,
                    "exception_index": index,
                    "stack": which,
                    "frame_index": frame_i,
                    "filename": frame.get("filename") or frame.get("abs_path"),
                    "function": frame.get("function"),
                    "abs_path": frame.get("abs_path"),
                    "resolved_with": resolved,
                    "resolved_with_known": resolved in KNOWN_RESOLVED_WITH if resolved else False,
                    "in_app": frame.get("in_app"),
                })


def collect_frames(event: dict[str, Any]) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    exc = event.get("exception")
    if isinstance(exc, dict):
        _walk_exception(exc.get("values"), source="exception", out=found)
    threads = event.get("threads")
    if isinstance(threads, dict):
        _walk_exception(threads.get("values"), source="threads", out=found)
    # Some fixtures put frames at the top for the eval.
    if isinstance(event.get("frames"), list):
        for frame_i, frame in enumerate(event["frames"]):
            if not isinstance(frame, dict):
                continue
            data = frame.get("data") if isinstance(frame.get("data"), dict) else {}
            resolved = frame.get("resolved_with", data.get("resolved_with"))
            found.append({
                "source": "fixture.frames",
                "exception_index": 0,
                "stack": "stacktrace",
                "frame_index": frame_i,
                "filename": frame.get("filename"),
                "function": frame.get("function"),
                "abs_path": frame.get("abs_path"),
                "resolved_with": resolved,
                "resolved_with_known": resolved in KNOWN_RESOLVED_WITH if resolved else False,
                "in_app": frame.get("in_app"),
            })
    return found


def debug_meta(event: dict[str, Any]) -> dict[str, Any]:
    meta = event.get("debug_meta")
    images = []
    if isinstance(meta, dict) and isinstance(meta.get("images"), list):
        for image in meta["images"]:
            if not isinstance(image, dict):
                continue
            images.append({
                "type": image.get("type"),
                "debug_id": image.get("debug_id"),
                "code_file": image.get("code_file"),
            })
    return {
        "has_debug_meta": bool(images),
        "images": images,
        "has_matching_bundle": None,
        "matching_bundle_note": (
            "has debug_meta != has a matching artifact bundle. "
            "This script does not look up uploaded artifacts and will not claim a match."
        ),
    }


def redact(text: str) -> str:
    return TOKEN_RE.sub("[REDACTED_SNTRYS]", text)


def build(event: dict[str, Any], *, mode: str, maps_release: str | None) -> dict[str, Any]:
    frames = collect_frames(event)
    meta = debug_meta(event)
    counts: dict[str, int] = {}
    invented: list[str] = []
    scraping = False
    for frame in frames:
        rw = frame.get("resolved_with")
        if not isinstance(rw, str):
            continue
        counts[rw] = counts.get(rw, 0) + 1
        if rw not in KNOWN_RESOLVED_WITH and rw not in invented:
            invented.append(rw)
        if rw == "scraping":
            scraping = True

    sdk_release = event.get("release")
    if sdk_release is None and isinstance(event.get("tags"), list):
        for tag in event["tags"]:
            if isinstance(tag, dict) and tag.get("key") == "release":
                sdk_release = tag.get("value")
    mismatch = bool(maps_release and sdk_release and maps_release != sdk_release)
    return {
        "mode": mode,
        "event_id": event.get("event_id") or event.get("id"),
        "platform": event.get("platform"),
        "sdk_release": sdk_release,
        "maps_release": maps_release,
        "release_mismatch": mismatch,
        "handoff": (
            "sentry-release-medic / sourcemap-uploader"
            if mismatch
            else None
        ),
        "handoff_note": (
            "Release id on the event differs from the release the maps were uploaded to. "
            "Do not invent a second upload procedure here. "
            "Read the labeled ci-sourcemap-upload copy; owner is sourcemap-uploader."
            if mismatch
            else None
        ),
        "debug_meta": meta,
        "frames": frames,
        "resolved_with_counts": counts,
        "unknown_matchers": invented,
        "known_matchers": list(KNOWN_RESOLVED_WITH),
        "scraping_seen": scraping,
        "scraping_note": (
            "At least one frame resolved_with=scraping. Sentry fetched source from the web. "
            "That is not a Debug ID success. Do not ship maps on a public CDN so scraping can work."
            if scraping
            else None
        ),
        "not_retroactive": True,
        "backfill_note": (
            "Uploading source maps later does not rewrite events already stored. "
            "Fingerprint rules do not restack events already accepted. "
            "Only later events can pick up new artifacts."
        ),
        "symbolication_scope": "javascript-debug-id-only",
        "native_note": (
            "ProGuard, dSYM, and other native artifact types are named and unspecified. "
            "Do not invent those steps."
        ),
        "wrote": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", dest="json_path", help="Event JSON path, or '-' for stdin.")
    parser.add_argument("--event-id", help="Event id for a live read (not implemented).")
    parser.add_argument("--maps-release", help="Release id maps were uploaded under, if known.")
    parser.add_argument("--apply", action="store_true", help="Refused. Does not upload or reprocess.")
    args = parser.parse_args(argv)

    client = client_from_env()
    if args.apply:
        try:
            client.refuse_write("reprocess event / upload source maps")
        except SentryReadOnlyError as exc:
            print(json.dumps({"ok": False, "wrote": False, "error": str(exc)}))
            return 2

    mode = "advisory"
    if args.json_path:
        raw = sys.stdin.read() if args.json_path == "-" else Path(args.json_path).read_text()
        raw = redact(raw)
        try:
            event = client.fetch_event_json(args.event_id or "pasted", pasted=raw)
        except SentryReadOnlyError as exc:
            print(json.dumps({"ok": False, "mode": "advisory", "error": str(exc)}))
            return 2
    else:
        try:
            if not args.event_id:
                raise SentryReadOnlyError(
                    "No event JSON. Pass --json. Do not guess an event id."
                )
            event = client.fetch_event_json(args.event_id)
            mode = "live"
        except SentryReadOnlyError as exc:
            print(json.dumps({
                "ok": False,
                "mode": "advisory",
                "error": str(exc),
                "hint": "Pass --json with the pasted event. Live fetch is not implemented.",
            }))
            return 2

    report = build(event, mode=mode, maps_release=args.maps_release)
    report["ok"] = True
    text = json.dumps(report, indent=2)
    sys.stdout.write(redact(text) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
