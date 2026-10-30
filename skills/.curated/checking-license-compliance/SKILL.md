---
name: checking-license-compliance
description: |
  Audit a project's dependency licenses against an explicit policy
  (allow-list / deny-list / review-required) and flag incompatibilities
  before they ship to production. Reads SPDX license identifiers from
  npm package manifests, Python METADATA / PKG-INFO files, and
  pyproject.toml; classifies each license by family (permissive,
  weak-copyleft, strong-copyleft, proprietary, unknown); detects
  copyleft contamination and SPDX-incompatible license combinations.
  Use when: pre-release legal review, M&A code-audit due diligence,
  preparing an OSS attribution NOTICE file, or switching a project's
  own license.
  Threshold: any GPL-family license in a project declaring MIT or
  Apache-2.0; any UNKNOWN-license package; any metadata-vs-source
  license mismatch.
  Trigger with: "check licenses", "license compliance audit",
  "SPDX scan", "GPL contamination check".
allowed-tools:
  - Read
  - Bash(python3:*)
  - Bash(pip:*)
  - Bash(npm:*)
  - Glob
disallowed-tools:
  - Bash(rm:*)
  - Bash(curl:*)
  - Bash(wget:*)
  - Write(.env)
  - Edit(.env)
version: 3.33.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Designed for Claude Code
tags:
  - security
  - licensing
  - spdx
  - compliance
  - pentest
---

# Checking License Compliance

## Overview

License compliance is a security concern only in the indirect sense
that an unintended license obligation can force you to release
proprietary source code, retroactively invalidate a customer
contract, or render an M&A transaction infeasible. The cost is
legal and contractual rather than exploitative — but the
consequence ladder is real.

The most-stepped-on landmine is **copyleft contamination**:
unintentionally including a GPL or AGPL-licensed package in a
codebase the rest of which is permissively licensed (MIT, Apache-2.0,
BSD). The terms of the GPL family say that any project distributing
GPL code MUST itself release source under a GPL-compatible license.
If your `package.json` says MIT and one of your transitive deps is
GPL-2.0, you may be obligated to either re-license your code or
remove the dep.

This skill audits the resolved dependency tree against an explicit
policy file and emits findings for:

- Direct deps with deny-listed licenses
- Transitive deps with deny-listed licenses
- Packages with UNKNOWN license metadata (no SPDX identifier)
- License conflicts between metadata and source headers
- Combinations of licenses that are mutually incompatible (e.g.
  GPL-2.0 + Apache-2.0 without a patent grant)

## When the skill produces findings

| Finding | Severity | Threshold | Affected control |
|---|---|---|---|
| Strong-copyleft in permissive project | **CRITICAL** | GPL-2.0/3.0, AGPL-3.0, or similar in a project declaring MIT/Apache-2.0/BSD | (legal) |
| Weak-copyleft requiring source disclosure | **HIGH** | LGPL family in a project where the obligation isn't being met (no source-availability commitment) | (legal) |
| Custom / non-SPDX license | **HIGH** | License field doesn't match SPDX expression syntax; requires legal review | (legal) |
| Unknown license | **MEDIUM** | Package has no `license` field, no LICENSE file detected | (legal) |
| Deny-listed license (per policy) | **HIGH** | Package license is in the explicit deny-list in the policy file | (legal) |
| Review-required license (per policy) | **MEDIUM** | Package license is in the review-list (e.g. MPL-2.0) | (legal) |
| Incompatible license combination | **HIGH** | Detected pair of licenses known to conflict (e.g. GPL-2.0-only + Apache-2.0) | (legal) |
| License declared differently in metadata vs source headers | **MEDIUM** | LICENSE file says one license; per-file SPDX-License-Identifier headers say another | (legal) |
| Permissive license requiring attribution | **INFO** | MIT/BSD/Apache-2.0 — emit reminder that NOTICE / attribution file should list the package | (informational) |

## Prerequisites

- Python 3.9+
- Target project with EITHER a `package.json` + `node_modules/`
  OR a Python project (`pyproject.toml`/`requirements.txt`/
  installed venv)
- Policy file at `./.license-policy.json` (auto-detected) or
  passed via `--policy`. If absent, the skill uses a built-in
  default policy that flags strong copyleft for permissive parent
  projects.

## Instructions

### Step 1 — Identify the project's own declared license

The skill reads the project's top-level license from:

- npm: `package.json`'s `license` field
- Python: `pyproject.toml`'s `[project].license` table OR
  `setup.cfg`'s `license` field

If the project's own license isn't declared, the skill emits a
FATAL operational finding — license compliance can't be checked
without a baseline. Add a `license` field before running.

### Step 2 — Identify policy

The policy file is JSON:

```json
{
  "allow": ["MIT", "BSD-3-Clause", "Apache-2.0", "ISC", "BSD-2-Clause"],
  "deny":  ["GPL-2.0-only", "GPL-3.0-only", "AGPL-3.0-only", "AGPL-3.0-or-later"],
  "review": ["MPL-2.0", "EPL-2.0", "CDDL-1.0", "LGPL-3.0-or-later"],
  "project_license": "MIT"
}
```

`allow`: licenses that pass without comment.
`deny`: licenses that produce a finding regardless of project license.
`review`: licenses that produce a MEDIUM-severity finding for legal review.
`project_license`: enforced — if the project declares this but a dep is in `deny`, finding is CRITICAL.

### Step 3 — Run the scanner

```bash
python3 ./scripts/check_licenses.py /path/to/project
```

Options:

```
Usage: check_licenses.py PATH [OPTIONS]

Options:
  --output FILE      Write findings to FILE (default: stdout)
  --format FMT       json | jsonl | markdown (default: markdown)
  --min-severity SEV (default: info)
  --policy FILE      Override default policy
  --emit-attribution  Also emit an attribution file (NOTICE.md) listing
                     every permissive-licensed dep that requires attribution
```

### Step 4 — Interpret findings

CRITICAL findings block release pending legal review. Either remove
the offending dep, replace it with a permissively-licensed
alternative, or escalate to legal for a written exception.

HIGH findings require legal sign-off but don't necessarily block
release if the legal posture (e.g. service-only deployment under
AGPL) makes the obligation moot.

MEDIUM findings should be reviewed quarterly and either resolved
or moved into an explicit exception list.

INFO findings are reminders that an attribution / NOTICE file
should reference these packages.

## Examples

### Example 1 — Pre-release legal gate

```bash
python3 ./scripts/check_licenses.py . --min-severity high --format json --output license-audit.json
jq -e '. == []' license-audit.json || { echo "License finding — legal review required"; exit 1; }
```

### Example 2 — Generate attribution file

```bash
python3 ./scripts/check_licenses.py . --emit-attribution --format markdown --output NOTICE.md
```

### Example 3 — M&A due diligence

```bash
mkdir -p evidence/legal/
python3 ./scripts/check_licenses.py target-acquisition-codebase/ \
    --format json \
    --output evidence/legal/license-audit-$(date +%Y%m%d).json
```

## Output

JSON / JSONL / Markdown per `lib/report.py`. Exit codes: 0 clean,
1 high/critical, 2 error.

Each Finding includes:

- `id` — `license-compliance::<package>::<license-id>`
- `severity` — CRITICAL / HIGH / MEDIUM / LOW / INFO
- `category` — `license-compliance`
- `summary` — what's wrong
- `evidence` — package name, declared license, project license, policy match
- `references` — SPDX URL for the license, package home page

## Error Handling

- **No project license** → emits an INFO/operational finding
  recommending the operator add a `license` field, exits 2.
- **Unparseable policy file** → exits 2 with a parser error message.
- **Package with malformed license field** → treated as UNKNOWN
  license, emits MEDIUM finding.
- **No SPDX identifier in source headers** → emits INFO finding
  reminding that SPDX header convention catches contamination at
  the file level.

## Resources

- `references/THEORY.md` — SPDX license expression syntax, family
  classifications, copyleft propagation theory, common license
  incompatibilities, when LGPL static linking matters, AGPL
  service-distribution clauses, public-domain edge cases (CC0 vs
  unlicense)
- `references/PLAYBOOK.md` — Default policy templates per project
  type (proprietary product, OSS library, internal-only tool, SaaS
  service), attribution file generation, legal-counsel handoff
  templates, replacing copyleft deps with permissive alternatives
