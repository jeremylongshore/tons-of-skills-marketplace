#!/usr/bin/env python3
"""Enforce report-only-gate deadlines in CI.

Scans workflow .yml/.yaml and script comments for directives of the form:

    # REPORT-ONLY-UNTIL: YYYY-MM-DD

Also checks REPORT-ONLY-UNTIL keys in script and policy baseline JSON (root,
config, .github), and explicit expires clauses in active scan-allowlist waivers.
Documentation, plugin content, dependencies, fixtures and examples are outside
this governance scope. Quoted examples and Python docstrings are not directives.

Each marker represents a CI gate that's been intentionally relaxed to
report-only mode but MUST be flipped to blocking (or the gate fixed, or
the deadline extended) by the named date. The marker is a contract with
future-us: "I deferred this; here's when it costs me."

If today > the marker date, this script exits 1 and prints a clear
remediation message. The script is invoked from CI; after the deadline,
every PR fails until the maintainer takes action.

Exit codes:
  0   — all markers are in the future (or no markers found)
  1   — one or more markers have lapsed (deadline passed)
  2   — usage / parse error

Usage:
  python3 scripts/check-ci-deadlines.py
  python3 scripts/check-ci-deadlines.py --workflows .github/workflows
  python3 scripts/check-ci-deadlines.py --warn-days 14   # also warn if <N days out
"""

from __future__ import annotations

import argparse
import datetime as dt
import io
import json
import os
import re
import sys
import tokenize
from pathlib import Path

import yaml

# Scope is repository governance, not plugin payloads, historical documents,
# dependency trees, or fixture/example data. Root hidden baselines are included.
SOURCE_SUFFIXES = {".py", ".sh", ".bash", ".js", ".mjs", ".cjs", ".ts", ".mts", ".cts"}
EXCLUDED_DIRS = {"node_modules", "vendor", "fixtures", "__fixtures__", "examples", "__pycache__", ".git"}
DIRECTIVE = re.compile(r"^\s*REPORT-ONLY-UNTIL\s*:(.*)$", re.IGNORECASE)
DATE_VALUE = re.compile(r"^(\d{4}-\d{2}-\d{2})(?:\s+\((.*)\))?\s*$")
# Consume strings before comments, including multiline template/shell strings.
# Heredocs are examples/data, not executable shell comments.
QUOTED = r""""(?:\\[\s\S]|[^"\\])*"|'(?:\\[\s\S]|[^'\\])*' """.strip()
JS_QUOTED = r""""(?:\\[\s\S]|[^"\\\r\n])*"|'(?:\\[\s\S]|[^'\\\r\n])*' """.strip()
JS_TOKENS = re.compile(JS_QUOTED + r"|`(?:\\[\s\S]|[^`\\])*`|/\*[\s\S]*?\*/|//[^\n]*")
SHELL_TOKENS = re.compile(
    r"<<-?\s*(?P<quote>['\"]?)(?P<delimiter>[A-Za-z_][A-Za-z_0-9]*)(?P=quote)[^\n]*\n"
    r"[\s\S]*?^\t*(?P=delimiter)[ \t]*$|\\[\s\S]|" + QUOTED + r"|(?<![^\s;|&()<>])\#[^\n]*",
    re.MULTILINE,
)


def parse_date(path: Path, line: int, value: object) -> tuple[Path, int, dt.date, str]:
    match = DATE_VALUE.fullmatch(value.strip()) if isinstance(value, str) else None
    try:
        if match is None:
            raise ValueError("expected YYYY-MM-DD and optional parenthesized note")
        date = dt.date.fromisoformat(match.group(1))
    except ValueError as error:
        raise ValueError(f"{path}:{line}: Invalid REPORT-ONLY-UNTIL date {value!r}: {error}") from error
    return path, line, date, (match.group(2) or "").strip()


def source_comments(path: Path, source: str):
    if path.suffix in {".yml", ".yaml"}:
        yield from workflow_comments(source)
        return
    if path.suffix == ".py":
        for token in tokenize.generate_tokens(io.StringIO(source).readline):
            if token.type == tokenize.COMMENT:
                yield token.start[0], token.string[1:]
        return
    javascript = path.suffix in {".js", ".mjs", ".cjs", ".ts", ".mts", ".cts"}
    lexer = JS_TOKENS if javascript else SHELL_TOKENS
    for token in lexer.finditer(source):
        value = token.group()
        prefix = "//" if javascript else "#"
        if value.startswith(prefix):
            yield source.count("\n", 0, token.start()) + 1, value[len(prefix) :]
        elif javascript and value.startswith("/*"):
            # A directive may occupy an entire block comment. Prose/examples
            # inside a documentation block are not directives.
            yield source.count("\n", 0, token.start()) + 1, value[2:-2].strip()


def workflow_comments(source: str):
    """YAML scalar quotes are not shell quotes; only run scalars contain code."""
    tokens = list(yaml.scan(source))

    def values(node, key):
        if isinstance(node, yaml.nodes.MappingNode):
            return [
                value for name, value in node.value if isinstance(name, yaml.nodes.ScalarNode) and name.value == key
            ]
        return []

    run_positions = set()
    for jobs in values(yaml.compose(source, Loader=yaml.SafeLoader), "jobs"):
        if not isinstance(jobs, yaml.nodes.MappingNode):
            continue
        for _, job in jobs.value:
            for steps in values(job, "steps"):
                if not isinstance(steps, yaml.nodes.SequenceNode):
                    continue
                for step in steps.value:
                    for run in values(step, "run"):
                        if isinstance(run, yaml.nodes.ScalarNode):
                            run_positions.add(run.start_mark.index)
    outside_scalars = list(source)
    for token in tokens:
        if not isinstance(token, yaml.tokens.ScalarToken):
            continue
        for position in range(token.start_mark.index, token.end_mark.index):
            if outside_scalars[position] != "\n":
                outside_scalars[position] = " "
        if token.style in {"|", ">"}:
            header = source[token.start_mark.index : token.end_mark.index].split("\n", 1)[0]
            if "#" in header:
                yield token.start_mark.line + 1, header.split("#", 1)[1]
        if token.start_mark.index in run_positions:
            code = token.value
            offset = token.start_mark.line + (1 if token.style in {"|", ">"} else 0)
            if token.style == "|":
                # Keep source line numbers and indentation for literal scripts.
                code = source[token.start_mark.index : token.end_mark.index].split("\n", 1)[1]
            for line_no, comment in source_comments(Path("run.sh"), code):
                yield offset + line_no, comment
    for line_no, line in enumerate("".join(outside_scalars).splitlines(), 1):
        if "#" in line:
            yield line_no, line.split("#", 1)[1]


def scan_file(path: Path) -> list[tuple[Path, int, dt.date, str]]:
    if path.is_symlink():
        raise ValueError(f"{path}: policy files must not be symlinks")
    source = path.read_text(encoding="utf-8")
    out = []
    if path.suffix == ".json":

        def object_pairs(pairs):
            for key, value in pairs:
                if key.lower() == "report-only-until":
                    # Locate the declaration, not a prose mention of the name.
                    key_match = re.search(r'"REPORT-ONLY-UNTIL"\s*:', source, re.IGNORECASE)
                    line = source.count("\n", 0, key_match.start()) + 1 if key_match else 1
                    out.append(parse_date(path, line, value))
            return dict(pairs)

        json.loads(source, object_pairs_hook=object_pairs)
        return out
    if path.name == "scan-allowlist.txt":
        for line_no, line in enumerate(source.splitlines(), 1):
            if not line.strip():
                continue
            if line.lstrip().startswith("#"):
                marker = DIRECTIVE.match(line.lstrip()[1:])
                if marker:
                    out.append(parse_date(path, line_no, marker.group(1)))
                continue
            waiver = re.match(r"^\s*\S+?:[A-Za-z0-9-]+(?:\s{2,}|\s*#\s*|\s+)(.+)$", line)
            if not waiver:
                continue
            for clause in waiver.group(1).split(";"):
                marker = DIRECTIVE.match(clause)
                expiry = re.match(r"^\s*expires\b(.*)$", clause, re.IGNORECASE)
                if marker or expiry:
                    out.append(parse_date(path, line_no, (marker or expiry).group(1)))
        return out
    if "report-only-until" not in source.lower():
        return out
    for line_no, comment in source_comments(path, source):
        marker = DIRECTIVE.match(comment)
        if marker:
            out.append(parse_date(path, line_no, marker.group(1)))
    return out


def policy_files(root: Path, workflow_dir: Path) -> list[Path]:
    paths = set()
    for directory in [workflow_dir, root / "scripts", root / "config", root / ".github"]:
        if not directory.is_dir():
            continue
        for parent, directories, files in os.walk(directory, followlinks=False):
            directories[:] = sorted(d for d in directories if d not in EXCLUDED_DIRS)
            for name in files:
                path = Path(parent) / name
                if directory == workflow_dir:
                    selected = path.suffix in {".yml", ".yaml"}
                elif directory == root / "scripts":
                    selected = (
                        path.suffix in SOURCE_SUFFIXES | {".json"}
                        or name == "scan-allowlist.txt"
                        or (not path.suffix and (path.is_symlink() or path.read_bytes().startswith(b"#!")))
                    )
                else:
                    selected = "baseline" in name.lower() and path.suffix == ".json"
                if selected:
                    paths.add(path)
    paths.update(path for path in root.glob("*baseline*.json") if path.is_file() or path.is_symlink())
    return sorted(paths)


def scan_workflows(workflow_dir: Path) -> list[tuple[Path, int, dt.date, str]]:
    """Compatibility entry point for callers scanning only workflow files."""
    return [
        entry
        for path in sorted(workflow_dir.rglob("*"))
        if path.suffix in {".yml", ".yaml"}
        for entry in scan_file(path)
    ]


def scan_policy(root: Path, workflow_dir: Path) -> list[tuple[Path, int, dt.date, str]]:
    return [entry for path in policy_files(root, workflow_dir) for entry in scan_file(path)]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--workflows",
        default=".github/workflows",
        help="Directory containing workflow YAML files",
    )
    parser.add_argument(
        "--warn-days",
        type=int,
        default=7,
        help="Warn (don't fail) when a deadline is N days or fewer away (default: 7)",
    )
    args = parser.parse_args()

    workflow_dir = Path(args.workflows)
    if not workflow_dir.is_dir():
        print(f"workflows dir not found: {workflow_dir}", file=sys.stderr)
        return 2

    try:
        markers = scan_policy(Path("."), workflow_dir)
    except (OSError, ValueError, tokenize.TokenError, IndentationError, yaml.YAMLError) as error:
        print(f"::error::{error}", file=sys.stderr)
        return 2
    if not markers:
        print("No REPORT-ONLY-UNTIL markers found. Nothing to enforce.")
        return 0

    today = dt.date.today()
    expired: list[tuple[Path, int, dt.date, str]] = []
    upcoming: list[tuple[Path, int, dt.date, str]] = []
    future: list[tuple[Path, int, dt.date, str]] = []

    for entry in markers:
        _, _, d, _ = entry
        days = (d - today).days
        if days < 0:
            expired.append(entry)
        elif days <= args.warn_days:
            upcoming.append(entry)
        else:
            future.append(entry)

    print(f"CI deadline check — {today.isoformat()} (today)")
    print(f"  Total markers:  {len(markers)}")
    print(f"  Expired:        {len(expired)}")
    print(f"  Upcoming (≤{args.warn_days}d): {len(upcoming)}")
    print(f"  Future:         {len(future)}")
    print()

    if upcoming:
        print("UPCOMING deadlines (act soon):")
        for f, ln, d, note in sorted(upcoming, key=lambda x: x[2]):
            days = (d - today).days
            extra = f" — {note}" if note else ""
            print(f"  ⚠  {f}:{ln}  {d.isoformat()}  ({days} day(s) left){extra}")
            print(f"     ::warning file={f},line={ln}::Report-only gate deadline in {days} day(s)")
        print()

    if future:
        print("Future deadlines:")
        for f, ln, d, note in sorted(future, key=lambda x: x[2]):
            days = (d - today).days
            extra = f" — {note}" if note else ""
            print(f"  ✓  {f}:{ln}  {d.isoformat()}  ({days} day(s) out){extra}")
        print()

    if expired:
        print("EXPIRED deadlines (this is what fails the build):")
        for f, ln, d, note in sorted(expired, key=lambda x: x[2]):
            days_over = (today - d).days
            extra = f" — {note}" if note else ""
            print(f"  ✗  {f}:{ln}  {d.isoformat()}  ({days_over} day(s) overdue){extra}")
            print(
                f"     ::error file={f},line={ln}::Report-only deadline lapsed {days_over} day(s) ago. Flip to blocking, fix the gate, or extend the deadline."
            )
        print()
        print("Remediation options for each expired marker:")
        print("  1. Fix the underlying issues, then flip the gate to blocking")
        print("     (remove --report-only / change `exit 0` to `exit $fail`).")
        print("  2. Extend the deadline by editing the date in the YAML")
        print("     (commit message: 'chore(ci): extend deadline for <gate> to YYYY-MM-DD because <reason>').")
        print("  3. Remove the gate entirely if it's no longer needed.")
        return 1

    print("All deadlines are in the future. Build passes.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
