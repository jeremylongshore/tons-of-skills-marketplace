#!/usr/bin/env python3
"""Read-only inventory of agent-system artifacts under a bounded root."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path


SKIP_DIRS = {".git", ".hg", ".svn", "node_modules", "vendor", "dist", "build"}
MAX_FILES = 100_000


def classify(relative: Path) -> set[str]:
    kinds: set[str] = set()
    name = relative.name
    parts = relative.parts

    if name == "SKILL.md":
        kinds.add("agent-skill")
    if name == "eval-spec.yaml":
        kinds.add("evaluation-spec")
    if name == ".mcp.json":
        kinds.add("mcp-config")
    if name == "hooks.json" or "hooks" in parts and name.endswith(".json"):
        kinds.add("hook-config")
    if name == "marketplace.json":
        kinds.add("marketplace-catalog")
    if name == "plugin.json" and any(part in {".claude-plugin", ".codex-plugin"} for part in parts):
        kinds.add("plugin-manifest")
    if name.endswith(".md") and "agents" in parts:
        kinds.add("subagent")
    return kinds


def inventory(root: Path) -> dict[str, object]:
    resolved = root.resolve(strict=True)
    if not resolved.is_dir():
        raise ValueError("target must be a directory")

    artifacts: dict[str, list[str]] = {}
    scanned = 0
    for current, directories, files in os.walk(resolved, followlinks=False):
        directories[:] = sorted(
            directory
            for directory in directories
            if directory not in SKIP_DIRS and not (Path(current) / directory).is_symlink()
        )
        for filename in sorted(files):
            scanned += 1
            if scanned > MAX_FILES:
                raise ValueError(f"target exceeds the {MAX_FILES}-file inventory bound")
            path = Path(current) / filename
            if path.is_symlink():
                continue
            relative = path.relative_to(resolved)
            for kind in classify(relative):
                artifacts.setdefault(kind, []).append(relative.as_posix())

    return {
        "schema_version": 1,
        "root": str(resolved),
        "files_scanned": scanned,
        "artifacts": {key: artifacts[key] for key in sorted(artifacts)},
    }


def self_test() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        (root / "skills" / "example").mkdir(parents=True)
        (root / "skills" / "example" / "SKILL.md").write_text("fixture\n", encoding="utf-8")
        (root / ".claude-plugin").mkdir()
        (root / ".claude-plugin" / "plugin.json").write_text("{}\n", encoding="utf-8")
        (root / "agents").mkdir()
        (root / "agents" / "reviewer.md").write_text("fixture\n", encoding="utf-8")
        result = inventory(root)
        assert result["artifacts"] == {
            "agent-skill": ["skills/example/SKILL.md"],
            "plugin-manifest": [".claude-plugin/plugin.json"],
            "subagent": ["agents/reviewer.md"],
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", nargs="?", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        print(json.dumps({"status": "PASS", "self_test": True}, sort_keys=True))
        return 0
    if args.target is None:
        parser.error("target is required unless --self-test is used")
    try:
        print(json.dumps(inventory(args.target), indent=2, sort_keys=True))
    except (OSError, ValueError) as error:
        print(json.dumps({"status": "FAIL", "error": str(error)}, sort_keys=True))
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
