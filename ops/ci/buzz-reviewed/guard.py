#!/usr/bin/env python3
"""Root-owned admission guard for separately approved same-repository PR revisions."""

import json
import os
from pathlib import Path
import re
import stat
import sys

REPO = "jeremylongshore/tons-of-skills-marketplace"
POLICY = Path("/etc/ccpi-reviewed/admission.json")
WORKFLOWS = {
    "validate-plugins.yml",
    "skill-conform.yml",
    "secret-scan.yml",
    "check-links.yml",
    "codeql.yml",
    "pr-prescreen.yml",
    "auto-bump-on-pr.yml",
    "kernel-shadow-validation.yml",
}


def admit(env, payload, policy):
    """No actor/branch-only trust: both PR head and actual merge revision are pinned."""
    if env.get("GITHUB_REPOSITORY") != REPO or env.get("GITHUB_EVENT_NAME") != "pull_request":
        raise ValueError("only same-repository pull_request events are admitted")
    pr = payload.get("pull_request", {})
    number = payload.get("number")
    if type(number) is not int or number <= 0:
        raise ValueError("invalid PR identity")
    if payload.get("repository", {}).get("full_name") != REPO:
        raise ValueError("payload repository mismatch")
    if pr.get("head", {}).get("repo", {}).get("full_name") != REPO:
        raise ValueError("fork head refused")
    if pr.get("base", {}).get("repo", {}).get("full_name") != REPO or pr.get("base", {}).get("ref") != "main":
        raise ValueError("wrong base")
    ref = f"refs/pull/{number}/merge"
    if env.get("GITHUB_REF") != ref:
        raise ValueError("wrong PR ref")
    workflow = env.get("GITHUB_WORKFLOW_REF", "")
    if workflow not in {f"{REPO}/.github/workflows/{name}@{ref}" for name in WORKFLOWS}:
        raise ValueError("workflow not admitted")
    head = pr.get("head", {}).get("sha", "")
    merge = env.get("GITHUB_SHA", "")
    if not all(isinstance(v, str) and re.fullmatch(r"[0-9a-f]{40}", v) for v in (head, merge)):
        raise ValueError("invalid immutable revision")
    if policy.get("schema") != 1 or policy.get("repository") != REPO:
        raise ValueError("invalid admission policy")
    if not any(row == {"pr": number, "head": head, "merge": merge} for row in policy.get("approved", [])):
        raise ValueError("revision has not been approved out of band")


def main():
    try:
        info = POLICY.lstat()
        if not stat.S_ISREG(info.st_mode) or info.st_uid != 0 or info.st_mode & 0o022:
            raise ValueError("policy must be a root-owned non-writable regular file")
        payload = Path(os.environ["GITHUB_EVENT_PATH"])
        if payload.stat().st_size > 2_000_000:
            raise ValueError("oversized event")
        admit(os.environ, json.loads(payload.read_text()), json.loads(POLICY.read_text()))
    except (ValueError, KeyError, OSError, TypeError, AttributeError):
        print("::error::Reviewed PR worker refused event or unapproved revision", file=sys.stderr)
        return 1
    print("Reviewed PR worker admitted exact approved head and merge revisions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
