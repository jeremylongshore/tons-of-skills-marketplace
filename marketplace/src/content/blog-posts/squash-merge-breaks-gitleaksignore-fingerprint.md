---
title: "gitleaks: Allowlist the Squash Commit in .gitleaksignore"
description: ".gitleaksignore fingerprints include the commit SHA, so a squash merge re-reports an allowlisted test token. Allowlist that commit; build fixtures at import."
date: "2026-10-23"
tags: ["ci-cd", "testing", "devops", "python", "claude-code"]
featured: false
canonical: "https://startaitools.com/posts/squash-merge-breaks-gitleaksignore-fingerprint/"
---
Pull requests that never touched a test file started failing the required docs check. Nothing new had leaked. The scanner found a token it had already been told to ignore, under a commit ID the ignore file did not list.

By the end of this post you will know why a `.gitleaksignore` entry stops working after a squash merge, how to add the entry that fixes it, and why a path-wide allowlist is the wrong shortcut.

## What broke

gitleaks is an open-source secret scanner. In this repository a required CI job (the docs job, which also runs Markdown lint) runs gitleaks 8.30.1 over the full git history, not just the latest diff. Every commit in the history it checks out gets scanned.

One earlier pull request had added a synthetic token to a test file. The token is a positive control: a deliberately token-shaped string that proves the repository's own personal-data scanner (a separate in-app check, not gitleaks) catches such strings. gitleaks flagged it on that branch, and an entry was added to `.gitleaksignore` for the finding.

Each entry in that file is a fingerprint in the form `commit:file:rule-id:line`. The commit is part of the key. The entry matched the branch commit and nothing else.

Then the pull request was squash merged. A squash merge collapses a branch into one new commit on main, with its own SHA. That commit added the same token again, this time at line 25 instead of 24. The old fingerprint matched nothing.

Eighty-two seconds after the merge, the docs job on another open pull request reached its gitleaks step and logged `leaks found: 1`. That pull request had never touched the test file. Its CI checkout fetches full history (`fetch-depth: 0`), which includes main, so the squash commit now on main was part of what gitleaks scanned. The fix commit records the blast radius: main and every open pull request failed the required docs check after the merge.

Reproducing it took one fresh clone. The finding looked like this, with the commit replaced by a placeholder:

```
RuleID:    generic-api-key
File:      tests/test_personal_data_scan.py
StartLine: 25
Commit:    <squash-sha>
```

The Commit field named the squash commit, not the branch commit the ignore file listed. That one field explains the whole failure.

## The two-part fix

The fix has two parts.

Part one: add a fingerprint for the squash commit. The old entry stays. It is harmless, and removing it buys nothing.

```
# Squash merge re-committed the same synthetic positive control.
<squash-sha>:tests/test_personal_data_scan.py:generic-api-key:25
```

Part two: stop writing the token as a literal in source. The test now builds the sentinel at import time from plain bytes:

```python
import base64

SENTINELS = {
    # Built at import so no high-entropy literal sits in the source.
    "token": base64.b64encode(b"synthetic-token-bytes").decode().rstrip("="),
}
```

The bytes in the example are a placeholder, not the value the test uses. The test still feeds the same string to the scanner, so it still proves the scanner catches token-shaped input. The file at head no longer contains a literal to match. The squash commit still does, which is why part one stays.

## Why not allowlist the path

The tempting shortcut is to tell gitleaks to skip the whole test file. That silences every finding in the file. A real credential pasted into the same file later would pass without a warning.

The fingerprint approach silences one line, in one commit, with a reason written next to it. The fix commit records that choice and the reason for it.

## How the diagnosis went

Claude Opus 5.5 was orchestrating several parallel implementer agents in Claude Code when the squash merge landed. The session log shows it did not guess at the cause. It cloned the failing branch fresh, ran gitleaks, read the commit in the finding, and recognized it as the squash commit. The fix branch was cut from main at 23:50 UTC, the personal-data scanner tests passed at 23:51, and the pull request opened about fifteen seconds later.

The fix merged at 00:14:16Z. That alone did not clear the other open pull requests: each branch still carried its own copy of `.gitleaksignore` without the new entry, so each needed main merged in before its docs check would pass. The agent sent the other implementers that instruction directly.

Verification: local gitleaks reported no leaks on the changed file, and across the full history of the fix branch. `pytest tests/test_personal_data_scan.py` reported 14 passed, 0 failed, 0 skipped.

## Use this

- When a full-history scan fails on pull requests that never touched the flagged file, read the Commit field first. If it names a squash commit on main, the problem is the fingerprint, not the code.
- Add one fingerprint for that squash commit in the `commit:file:rule-id:line` form defined in the [gitleaks README](https://github.com/gitleaks/gitleaks#gitleaksignore), with a comment that names the merge.
- Build synthetic fixtures at import time, and refuse path-wide allowlists on test files. They hide the next real secret that lands in the same file.

## Related posts

- [Pin CI tool installers, gitleaks included, so gate behaviour changes only by commit](https://startaitools.com/posts/pin-the-installer-and-add-a-renewer/)
- [Grep exit code 2 means it could not search, so CI scans that treat it as clean pass unreadable paths](https://startaitools.com/posts/grep-exit-code-2-ci-scan-reports-clean/)
- [A guard with no reachable red path is not a guard](https://startaitools.com/posts/the-gate-that-could-not-fail/)
