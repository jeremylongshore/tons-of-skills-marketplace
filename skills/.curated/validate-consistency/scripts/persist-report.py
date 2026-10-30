#!/usr/bin/env python3
"""File a consistency report through Intent OS's canonical disclosure adapter.

Read JSON from stdin: {"report": "...", "repairs": [{"summary": "...", "evidence": "..."}]}.
The audited repository is never modified. This command only files the supplied
report; it does not run checks, adjudicate findings, or perform repairs.
"""

from __future__ import annotations

import argparse
import datetime as dt
import fcntl
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path

LIMIT = 1024 * 1024
PART_A = "## Part A — Deterministic Findings"
PART_B = "## Part B — Advisory Findings (LLM-judged, never blocking)"


class Held(Exception):
    """A content-free, operator-facing failure code."""


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def regular(path: Path) -> None:
    """Refuse symlinks in any component before using a local policy or sink."""
    for parent in [*reversed(path.parents), path]:
        if parent.is_symlink():
            raise Held("symlink-path")
    if not path.is_file():
        raise Held("missing-required-file")


def parse_payload(raw: bytes) -> tuple[str, str]:
    if len(raw) > LIMIT:
        raise Held("input-too-large")
    try:
        value = json.loads(raw)
    except (ValueError, UnicodeError):
        raise Held("invalid-input-json") from None
    if not isinstance(value, dict) or set(value) - {"report", "repairs"}:
        raise Held("invalid-input-fields")
    report = value.get("report")
    if not isinstance(report, str) or not report.strip():
        raise Held("missing-report")
    lines = report.splitlines()
    if lines.count(PART_A) != 1 or lines.count(PART_B) != 1 or lines.index(PART_A) > lines.index(PART_B):
        raise Held("missing-separated-report-lanes")
    repairs = value.get("repairs", [])
    if not isinstance(repairs, list) or len(repairs) > 100:
        raise Held("invalid-repair-record")
    repair_lines = [
        "## Caller-reported repairs",
        "",
        "The audit does not perform repairs or independently adjudicate repair claims.",
        "",
    ]
    if not repairs:
        repair_lines.append("No repairs supplied. This run is report-only.")
    raw_strings = [report]
    for repair in repairs:
        if not isinstance(repair, dict) or set(repair) != {"summary", "evidence"}:
            raise Held("invalid-repair-record")
        if not all(isinstance(v, str) and v.strip() and len(v) <= 20000 for v in repair.values()):
            raise Held("invalid-repair-record")
        raw_strings.extend(repair.values())
        # Keep caller text as quoted data; it cannot introduce a new report lane.
        for label, text in [("Summary", repair["summary"]), ("Evidence (caller supplied)", repair["evidence"])]:
            repair_lines.append(f"**{label}:**")
            repair_lines.extend("> " + line for line in text.splitlines())
            repair_lines.append("")
    return report.rstrip() + "\n\n" + "\n".join(repair_lines) + "\n", "\n".join(raw_strings)


def screen(root: Path, rendered: str, raw_text: str, timestamp: float, *, audited_root: Path | None = None) -> dict:
    adapter = root / "ops/disclosure-policy/adapters/enforce.sh"
    policy = root / "ops/disclosure-policy/policy.py"
    regular(adapter)
    regular(policy)
    # Classify both unescaped caller text and the exact rendered body. Never use
    # redaction: accepting a placeholder would silently discard the report.
    run_id = str(uuid.uuid4())
    candidates = [{"id": run_id + "-raw", "text": raw_text}, {"id": run_id + "-report", "text": rendered}]
    temporary_parent = Path(tempfile.gettempdir()).resolve()
    protected = [root.resolve(), *([audited_root.resolve()] if audited_root is not None else [])]
    if any(temporary_parent.is_relative_to(path) for path in protected):
        raise Held("temporary-directory-inside-protected-tree")
    with tempfile.TemporaryDirectory(prefix="consistency-disclosure-", dir=temporary_parent) as folder:
        receipts = Path(folder) / "receipts.jsonl"
        run_receipt = Path(folder) / "run.json"
        try:
            result = subprocess.run(
                [
                    "bash",
                    str(adapter),
                    "--sink",
                    "evidence-ingest",
                    "--receipts",
                    str(receipts),
                    "--run-receipt",
                    str(run_receipt),
                    "--ts",
                    str(timestamp),
                ],
                input="".join(json.dumps(row, ensure_ascii=False) + "\n" for row in candidates),
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
            accepted = [json.loads(line) for line in result.stdout.splitlines()]
            rows = [json.loads(line) for line in receipts.read_text().splitlines()]
            run = json.loads(run_receipt.read_text())
        except (OSError, ValueError, subprocess.TimeoutExpired):
            raise Held("disclosure-unavailable") from None
    expected_counts = {"pass": 2, "rejected": 0, "redacted": 0, "held": 0}
    if not isinstance(run, dict) or not all(isinstance(row, dict) for row in rows):
        raise Held("invalid-disclosure-receipt")
    if result.returncode != 0 or accepted != candidates or run.get("counts") != expected_counts:
        raise Held("disclosure-held")
    if (
        run.get("sink") != "evidence-ingest"
        or run.get("n_records") != 2
        or run.get("run_ts") != timestamp
        or len(rows) != 2
    ):
        raise Held("invalid-disclosure-receipt")
    for receipt, candidate in zip(rows, candidates, strict=True):
        if (
            receipt.get("decision") != "pass"
            or receipt.get("sink") != "evidence-ingest"
            or receipt.get("doc_id") != candidate["id"]
            or receipt.get("ts") != timestamp
            or receipt.get("content_sha256") != digest(candidate["text"].encode())
        ):
            raise Held("invalid-disclosure-receipt")
    receipt_lines = [json.dumps(row, sort_keys=True) for row in rows]
    if run.get("records_sha256") != digest("\n".join(sorted(receipt_lines)).encode()):
        raise Held("invalid-disclosure-receipt")
    return {
        "sink": "evidence-ingest",
        "policy_sha256": digest(policy.read_bytes()),
        "body_sha256": digest(rendered.encode()),
        "receipt_sha256": run["records_sha256"],
    }


def numbered_tree(docs: Path) -> list[Path]:
    entries = []

    def unreadable(_error):
        raise Held("document-tree-unreadable")

    for current, directories, files in os.walk(docs, followlinks=False, onerror=unreadable):
        for name in [*directories, *files]:
            path = Path(current) / name
            if path.is_symlink():
                raise Held("symlink-in-document-tree")
            entries.append(path)
    return entries


def next_number(entries: list[Path]) -> int:
    highest = 0
    for path in entries:
        match = re.match(r"^(\d{3})(?:[a-z]|-\d+)?-", path.name)
        if match:
            highest = max(highest, int(match[1]))
    if highest >= 999:
        raise Held("number-range-exhausted")
    return highest + 1


def persist(root: Path, raw: bytes, at: dt.datetime, *, audited_root: Path) -> dict:
    body, raw_text = parse_payload(raw)
    root = root.absolute()
    audited_root = audited_root.resolve(strict=True)
    if not audited_root.is_dir():
        raise Held("audited-root-must-be-directory")
    if (root / "000-docs").resolve().is_relative_to(audited_root):
        raise Held("destination-inside-audited-tree")
    index = root / "000-docs/000-INDEX.md"
    regular(index)
    if not (root / ".git").exists():
        raise Held("not-intent-os-checkout")
    proof = screen(root, body, raw_text, at.timestamp(), audited_root=audited_root)
    fingerprint = digest(raw)
    docs = index.parent
    # Lock the existing index without introducing another persistent lock file.
    docs_fd = os.open(docs, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        index_fd = os.open("000-INDEX.md", os.O_RDWR | os.O_APPEND | os.O_NOFOLLOW, dir_fd=docs_fd)
    except OSError:
        os.close(docs_fd)
        raise
    try:
        try:
            fcntl.flock(index_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise Held("index-busy") from None
        before = os.fstat(index_fd)
        if not stat.S_ISREG(before.st_mode) or (before.st_dev, before.st_ino) != (
            index.stat().st_dev,
            index.stat().st_ino,
        ):
            raise Held("index-changed")
        # A retry of identical input must not create a second audit entry.
        entries = numbered_tree(docs)
        if any(path.match(f"*-AA-AUDR-consistency-*-{fingerprint[:16]}.md") for path in entries):
            raise Held("already-recorded")
        number = next_number(entries)
        name = f"{number:03d}-AA-AUDR-consistency-{at.strftime('%Y-%m-%dT%H%M%SZ')}-{fingerprint[:16]}.md"
        content = (
            f"---\ntitle: Document consistency audit\ndate: {at.date().isoformat()}\n---\n\n"
            + body
            + "\n## Disclosure receipt\n\n"
            + "The digests cover the body above, before this content-free receipt.\n\n"
            + "```json\n"
            + json.dumps(proof, sort_keys=True, indent=2)
            + "\n```\n"
        ).encode()
        # Exclusive creation never overwrites a prior record or follows a leaf
        # symlink. The existing index gets one append, preserving unrelated edits.
        fd = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=docs_fd)
        with os.fdopen(fd, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        tail = os.pread(index_fd, 2, max(0, before.st_size - 2))
        separator = "" if tail.endswith(b"\n\n") else "\n" if tail.endswith(b"\n") else "\n\n"
        entry = (
            separator
            + f"## Consistency audit {number:03d} — {at.date().isoformat()}\n\n"
            + f"[{name}]({name}) — Document consistency audit; caller-reported repairs and disclosure receipt.\n"
        ).encode()
        try:
            if os.write(index_fd, entry) != len(entry):
                raise OSError("short index write")
            os.fsync(index_fd)
            latest = index.lstat()
            if (latest.st_dev, latest.st_ino) != (before.st_dev, before.st_ino):
                raise OSError("index replaced during append")
        except OSError:
            # Retain the reviewed report; never delete evidence or rewrite an
            # index that another editor may have changed. Signal incomplete work.
            raise Held("report-saved-index-incomplete") from None
        return {"status": "saved", "path": "000-docs/" + name, "sha256": digest(content), "disclosure": proof}
    finally:
        os.close(index_fd)
        os.close(docs_fd)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--intent-os", type=Path, required=True)
    parser.add_argument(
        "--audited-root", type=Path, required=True, help="Audited tree; destination writes must stay outside it"
    )
    parser.add_argument("--at", help="UTC ISO timestamp; defaults to the current time")
    args = parser.parse_args()
    try:
        at = dt.datetime.fromisoformat(args.at.replace("Z", "+00:00")) if args.at else dt.datetime.now(dt.timezone.utc)
        if at.tzinfo is None or at.utcoffset() != dt.timedelta(0):
            raise Held("utc-timestamp-required")
        outcome = persist(args.intent_os, sys.stdin.buffer.read(LIMIT + 1), at, audited_root=args.audited_root)
    except Held as error:
        print(json.dumps({"status": "held", "code": str(error)}))
        return 2
    except (OSError, ValueError):
        # Raw exceptions can contain sensitive input or local paths.
        print(json.dumps({"status": "held", "code": "persistence-unavailable"}))
        return 2
    print(json.dumps(outcome, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
