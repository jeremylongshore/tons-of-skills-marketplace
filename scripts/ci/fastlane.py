"""Conservative CI routing and exact-result aggregation (stdlib only).

Actions executes classification from the immutable PR base. Any uncertainty
selects the full lane; a failed classifier still fails the aggregate gate.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys

SCHEMA = "1"
SAFE_PATHS = {
    ".github/FUNDING.yml": "funding",
    "CODE_OF_CONDUCT.md": "community",
    "docs/zcf-integration.md": "standalone-doc",
}
SKIPPABLE = frozenset(
    {
        "cli-smoke-tests",
        "shellcheck-skills",
        "skill-codeblock-syntax",
        "typescript-coverage-audit",
        "eslint-check",
        "ruff-check",
        "ruff-format-check",
    }
)
REQUIRED = (
    frozenset(
        {
            "classify-changes",
            "validate",
            "marketplace-compliance-ratchet",
            "verify",
            "test",
            "check-package-manager",
            "marketplace-validation",
            "format-check",
            "markdownlint",
            "scan-synced-content",
            "promote-curated-check",
            "check-submission-docs",
            "commit-scope-check",
            "codeowners-drift",
            "generated-content-drift",
            "doc-governance",
            "secret-diff-scan",
        }
    )
    | SKIPPABLE
)
SHA = re.compile(r"[0-9a-f]{40}\Z")
RAW_HEADER = re.compile(rb":([0-7]{6}) ([0-7]{6}) ([0-9a-f]{40}) ([0-9a-f]{40}) ([A-Z])\Z")


def git(*args: str) -> bytes:
    """No shell, replacement objects, external diff drivers or partial output."""
    return subprocess.run(
        ["git", "--no-replace-objects", *args],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=60,
        env={**os.environ, "GIT_NO_REPLACE_OBJECTS": "1", "GIT_OPTIONAL_LOCKS": "0"},
    ).stdout


def commit(value: object) -> str:
    if not isinstance(value, str) or not SHA.fullmatch(value):
        raise ValueError("invalid commit identity")
    if git("cat-file", "-t", value) != b"commit\n":
        raise ValueError("not a commit")
    return value


def parse_diff(raw: bytes) -> list[dict[str, str]]:
    if not raw:
        return []
    fields = raw.split(b"\0")
    if fields.pop() != b"" or len(fields) % 2:
        raise ValueError("incomplete raw diff")
    records = []
    for offset in range(0, len(fields), 2):
        header = RAW_HEADER.fullmatch(fields[offset])
        if header is None or not fields[offset + 1]:
            raise ValueError("malformed raw diff")
        old_mode, new_mode, old_oid, new_oid, status = header.groups()
        path = fields[offset + 1].decode("utf-8", errors="strict")
        records.append(
            {
                "path": path,
                "status": status.decode(),
                "old_mode": old_mode.decode(),
                "new_mode": new_mode.decode(),
                "old_oid": old_oid.decode(),
                "new_oid": new_oid.decode(),
            }
        )
    if len({item["path"] for item in records}) != len(records):
        raise ValueError("duplicate diff path")
    return records


def diff(before: str, after: str) -> list[dict[str, str]]:
    return parse_diff(
        git(
            "diff",
            "--raw",
            "-z",
            "--no-abbrev",
            "--no-renames",
            "--no-ext-diff",
            "--no-textconv",
            "--ignore-submodules=none",
            before,
            after,
            "--",
        )
    )


def safe(records: list[dict[str, str]]) -> bool:
    return bool(records) and all(
        item["path"] in SAFE_PATHS
        and item["status"] == "M"
        and item["old_mode"] == item["new_mode"] == "100644"
        and item["old_oid"] != "0" * 40
        and item["new_oid"] != "0" * 40
        for item in records
    )


def classify(event: object, event_name: str, checkout: str) -> dict:
    receipt = {
        "schema": SCHEMA,
        "lane": "full",
        "reason": "non-pr-event",
        "base": None,
        "head": None,
        "checkout": checkout,
        "merge_base": None,
        "authored": [],
        "integrated": [],
    }
    if event_name != "pull_request":
        return receipt
    try:
        if git("rev-parse", "--is-shallow-repository") != b"false\n":
            raise ValueError("incomplete history")
        pr = event["pull_request"]
        base, head = commit(pr["base"]["sha"]), commit(pr["head"]["sha"])
        checkout = commit(checkout)
        receipt.update(base=base, head=head, checkout=checkout)
        if git("rev-parse", "HEAD").decode().strip() != checkout:
            raise ValueError("checkout mismatch")
        parents = git("rev-list", "--parents", "-n", "1", checkout).decode().split()
        if parents != [checkout, base, head]:
            raise ValueError("unexpected integration parents")
        merge_bases = git("merge-base", "--all", base, head).decode().split()
        if len(merge_bases) != 1:
            raise ValueError("ambiguous history")
        receipt["merge_base"] = commit(merge_bases[0])
        receipt["authored"] = diff(merge_bases[0], head)
        receipt["integrated"] = diff(base, checkout)
        if safe(receipt["authored"]) and safe(receipt["integrated"]):
            receipt.update(lane="lightweight", reason="reviewed-paths-only")
        else:
            receipt["reason"] = "non-allowlisted-change-or-empty-diff"
    except (KeyError, TypeError, ValueError, OSError, subprocess.SubprocessError):
        receipt["reason"] = "unproven-comparison"
    return receipt


def gate(needs: object) -> list[str]:
    """Accept only a complete known job set and the lane's expected results."""
    if not isinstance(needs, dict) or set(needs) != REQUIRED:
        return ["dependency set is missing or unknown"]
    classification = needs["classify-changes"]
    if not isinstance(classification, dict) or classification.get("result") != "success":
        return ["classification did not succeed"]
    outputs = classification.get("outputs")
    if not isinstance(outputs, dict) or outputs.get("schema") != SCHEMA:
        return ["classification schema is missing or unsupported"]
    lane = outputs.get("lane")
    if not isinstance(lane, str) or lane not in {"full", "lightweight"}:
        return ["classification lane is missing or unknown"]
    errors = []
    for name, value in needs.items():
        allowed = {"success"}
        if lane == "lightweight" and name in SKIPPABLE:
            allowed.add("skipped")
        if not isinstance(value, dict) or not isinstance(value.get("result"), str) or value["result"] not in allowed:
            errors.append(f"{name}: required result absent or unsuccessful")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    route = commands.add_parser("classify")
    route.add_argument("--event-file", required=True, type=Path)
    route.add_argument("--event-name", required=True)
    route.add_argument("--checkout", required=True)
    route.add_argument("--receipt", required=True, type=Path)
    route.add_argument("--github-output", required=True, type=Path)
    commands.add_parser("gate")
    args = parser.parse_args()
    if args.command == "gate":
        try:
            errors = gate(json.loads(os.environ["NEEDS_JSON"]))
        except (KeyError, ValueError):
            errors = ["invalid dependency JSON"]
        for error in errors:
            print(f"ci-required: {error}", file=sys.stderr)
        if not errors:
            print("ci-required: all expected results verified")
        return int(bool(errors))
    try:
        event = json.loads(args.event_file.read_text())
    except (OSError, ValueError):
        event = None
    receipt = classify(event, args.event_name, args.checkout)
    serialized = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    args.receipt.write_text(serialized)
    print(serialized, end="")
    # Only two fixed-vocabulary values enter Actions' line-based output protocol.
    with args.github_output.open("a") as output:
        output.write(f"schema={SCHEMA}\nlane={receipt['lane']}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
