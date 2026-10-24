#!/usr/bin/env python3
"""Replay the frozen census without network access or repository writes."""

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys


def verify(root, census, compare_worktree=False):
    ref = census["source_ref"]
    if not re.fullmatch(r"[0-9a-f]{40}", ref):
        raise ValueError("source_ref must be a full Git commit SHA")

    def git(*args):
        return subprocess.check_output(["git", *args], cwd=root)

    entries = {}
    for entry in git("ls-tree", "-r", "-z", ref, "--", "plugins").split(b"\0"):
        if not entry:
            continue
        metadata, path = entry.split(b"\t", 1)
        mode, kind, _ = metadata.split()
        if kind == b"blob" and mode in (b"100644", b"100755"):
            entries[path.decode()] = mode.decode()

    suffixes = {".ts", ".tsx", ".cts", ".mts", ".js", ".mjs", ".cjs", ".py", ".json"}
    mcp_paths = {p for p in entries if p.startswith("plugins/mcp/") and Path(p).suffix in suffixes}
    hook_paths = {p for p in entries if p.endswith("/hooks.json")}
    wanted = sorted({p for p in entries if p.endswith(".md")} | mcp_paths | hook_paths)
    contents = {}
    process = subprocess.Popen(
        ["git", "cat-file", "--batch"],
        cwd=root,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )
    try:
        for path in wanted:
            if "\n" in path:
                raise ValueError("newline in Git path is unsupported by the batch reader")
            process.stdin.write(f"{ref}:{path}\n".encode())
            process.stdin.flush()
            header = process.stdout.readline().decode().split()
            if len(header) != 3 or header[1] != "blob":
                raise ValueError(f"missing source blob: {path}")
            contents[path] = process.stdout.read(int(header[2]))
            if process.stdout.read(1) != b"\n":
                raise ValueError(f"invalid batch framing: {path}")
    finally:
        process.stdin.close()
        process.wait()
    if process.returncode:
        raise ValueError("Git batch reader failed")

    # Use the canonical parser only when its working bytes equal the frozen source.
    parser_path = root / "scripts/validate-skills-schema.py"
    if parser_path.read_bytes() != git("show", f"{ref}:scripts/validate-skills-schema.py"):
        raise ValueError("canonical parser differs from the snapshot; use matching source")
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location("platform_census_validator", parser_path)
    validator = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = validator
    spec.loader.exec_module(validator)

    broad = []
    errors = {}
    explicit = 0
    unrestricted = {"Bash", "Bash:*", "Bash(*)", "Bash(*:*)", "*"}
    for path, raw in contents.items():
        if not path.endswith(".md"):
            continue
        text = raw.decode("utf-8", errors="replace")
        if not text.startswith("---"):
            continue
        digest = hashlib.sha256(raw).hexdigest()
        try:
            front, _ = validator.parse_frontmatter(text)
        except ValueError:
            errors[path] = digest
            continue
        if "allowed-tools" not in front:
            continue
        explicit += 1
        tokens = validator.parse_allowed_tools(front["allowed-tools"])
        matches = [t for t in tokens if t in unrestricted]
        if matches:
            broad.append(
                {
                    "path": path,
                    "sha256": digest,
                    "allowed_tools": front["allowed-tools"],
                    "tokens": tokens,
                    "broad": matches,
                    "disallowed_tools": front.get("disallowed-tools"),
                }
            )
    if sorted(broad, key=lambda r: r["path"]) != census["broad_artifacts"]:
        raise ValueError("broad candidate census differs from the frozen Git universe")
    if errors != {r["path"]: r["sha256"] for r in census["parse_exceptions"]}:
        raise ValueError("parse-exception census differs from the frozen Git universe")
    if explicit != census["counts"]["explicit_allowed_tools_fields"]:
        raise ValueError("explicit-field denominator differs")
    if hook_paths != {r["path"] for r in census["hooks"]}:
        raise ValueError("hook configuration universe differs")
    for row in census["hooks"]:
        if json.loads(contents[row["path"]]) != row["config"]:
            raise ValueError(f"hook configuration differs: {row['path']}")
    if mcp_paths != {r["path"] for r in census["mcp_files"]}:
        raise ValueError("MCP source/configuration universe differs")
    mcp_roots = sorted(
        {
            "/".join(p.split("/")[:3])
            for p in entries
            if p.startswith("plugins/mcp/") and "/".join(p.split("/")[:3]) + "/.claude-plugin/plugin.json" in entries
        }
    )
    if mcp_roots != census["mcp_roots"]:
        raise ValueError("MCP plugin-root universe differs")
    if any(b"anthropic/maxResultSizeChars" in contents[p] for p in mcp_paths):
        raise ValueError("annotation literal occurs in the frozen MCP universe")

    computed_counts = {
        "explicit_allowed_tools_fields": explicit,
        "broad_artifacts": len(broad),
        "broad_roots": len({"/".join(row["path"].split("/")[:3]) for row in broad}),
        "parse_exceptions": len(errors),
        "hook_configs": len(hook_paths),
        "mcp_source_files": len(mcp_paths),
    }
    if computed_counts != census["counts"]:
        raise ValueError("recorded census counts differ from the frozen source")
    for key in ("broad_artifacts", "parse_exceptions", "hooks", "mcp_files"):
        if len(census[key]) != len({row["path"] for row in census[key]}):
            raise ValueError(f"duplicate path within {key}")

    records = census["broad_artifacts"] + census["parse_exceptions"] + census["hooks"] + census["mcp_files"]
    hashes = {r["path"]: r["sha256"] for r in records}
    for path, expected in hashes.items():
        if hashlib.sha256(contents[path]).hexdigest() != expected:
            raise ValueError(f"source hash differs: {path}")
        if compare_worktree:
            current = root / path
            if current.is_symlink() or current.read_bytes() != contents[path]:
                raise ValueError(f"working bytes differ: {path}")
    catalog = census["catalog_source"]
    raw_catalog = git("show", f"{ref}:{catalog['path']}")
    if hashlib.sha256(raw_catalog).hexdigest() != catalog["sha256"]:
        raise ValueError("catalog source hash differs")
    if len(json.loads(raw_catalog)["plugins"]) != catalog["entry_count"]:
        raise ValueError("catalog snapshot count differs")
    return {
        "source_ref": ref,
        "explicit_fields": explicit,
        "broad_artifacts": len(broad),
        "parse_exceptions": len(errors),
        "hook_configs": len(hook_paths),
        "mcp_roots": len(mcp_roots),
        "mcp_source_files": len(mcp_paths),
        "distinct_bound_blobs": len(hashes),
        "annotation_literal_matches": 0,
        "worktree_compared": compare_worktree,
        "mismatches": 0,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compare-worktree", action="store_true")
    parser.add_argument(
        "--census",
        type=Path,
        default=Path(__file__).with_name("2026-10-23-platform-feature-census.json"),
    )
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    result = verify(root, json.loads(args.census.read_text()), args.compare_worktree)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
