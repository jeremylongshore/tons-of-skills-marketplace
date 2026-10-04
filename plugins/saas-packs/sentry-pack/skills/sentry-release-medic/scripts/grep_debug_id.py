#!/usr/bin/env python3
"""Grep built JS artifacts for a Debug ID comment.

Source of truth is the artifact, not the action-release docs.
Absence of `debugId` in the files that will run means those bytes were not injected.
A `.map` that contains `debug_id` does not count as the running bytes.

Does not call the Sentry API. `--apply` is refused via sentry_readonly.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_LIB = Path(__file__).resolve().parents[3] / "scripts" / "lib"
if _LIB.is_dir() and str(_LIB) not in sys.path:
    sys.path.insert(0, str(_LIB))

from sentry_readonly import SentryReadOnlyError, client_from_env  # noqa: E402

JS_SUFFIXES = {".js", ".mjs", ".cjs", ".html", ".htm"}
MAP_SUFFIXES = {".map"}
SKIP_DIRS = {".git", "node_modules", ".next", "coverage"}

HELP_CENTER = "https://www.sentry.help/en/articles/13965232-javascript-how-do-i-verify-debug-ids-for-source-maps"
BLOG = "https://blog.sentry.io/how-to-fix-source-map-upload-errors/"
ACTIONS_DOC = "https://docs.sentry.io/product/releases/setup/release-automation/github-actions/"

# Both claims stay. Do not delete one to "resolve" the conflict.
CITATIONS = {
    "help_center_claims_action_v3_injects": HELP_CENTER,
    "blog_claims_github_action_cannot_inject": BLOG,
    "actions_doc_upload_and_release_not_a_winner": ACTIONS_DOC,
    "rule": (
        "Cite both the Help Center and the blog. Do not pick a winner URL. "
        "Trust this grep. Re-check the action source at build time."
    ),
}


def _iter_files(root: Path) -> list[Path]:
    if root.is_file():
        return [root]
    found: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.suffix.lower() in JS_SUFFIXES | MAP_SUFFIXES or path.suffix == "":
            # Keep unknown suffixes out; empty suffix is not a bundle.
            if path.suffix.lower() in JS_SUFFIXES | MAP_SUFFIXES:
                found.append(path)
    return found


def scan(paths: list[Path]) -> dict:
    js_hits: list[dict] = []
    map_hits: list[dict] = []
    scanned = 0
    for path in paths:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            return {"ok": False, "error": f"{path}: {exc}"}
        scanned += 1
        suffix = path.suffix.lower()
        if suffix in JS_SUFFIXES:
            count = text.count("debugId")
            if count:
                js_hits.append({"path": str(path), "debugId_count": count})
        elif suffix in MAP_SUFFIXES:
            count = text.count("debug_id") + text.count("debugId")
            if count:
                map_hits.append({"path": str(path), "debug_id_count": count})
    present = bool(js_hits)
    return {
        "ok": True,
        "verdict": "PRESENT" if present else "ABSENT",
        "running_bytes_injected": present,
        "files_scanned": scanned,
        "js_debugId_hits": js_hits,
        "map_debug_id_hits": map_hits,
        "map_only_does_not_count": bool(map_hits) and not present,
        "next_step": None
        if present
        else (
            "debugId is absent in the built JS. Run `sentry-cli sourcemaps inject` "
            "or a current bundler plugin (>= 2.0.0) BEFORE upload, then deploy THOSE files. "
            "Do not upload maps for a different build than the one that will run."
        ),
        "citations": CITATIONS,
        "symbolication_scope": "javascript-debug-id-only",
        "wrote": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="+", help="Built file or directory to grep.")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    client = client_from_env()
    if args.apply:
        try:
            client.refuse_write("upload source maps / create release")
        except SentryReadOnlyError as exc:
            print(json.dumps({"ok": False, "wrote": False, "error": str(exc)}))
            return 1
    files: list[Path] = []
    for raw in args.path:
        path = Path(raw)
        if not path.exists():
            print(json.dumps({"ok": False, "error": f"path not found: {raw}"}))
            return 1
        files.extend(_iter_files(path))
    if not files:
        print(
            json.dumps(
                {
                    "ok": False,
                    "verdict": "ABSENT",
                    "error": "no JS or source-map files under the given path",
                    "citations": CITATIONS,
                }
            )
        )
        return 2
    report = scan(files)
    if report.get("ok") is False:
        print(json.dumps(report))
        return 1
    print(json.dumps(report, indent=2))
    return 0 if report["verdict"] == "PRESENT" else 2


if __name__ == "__main__":
    sys.exit(main())
