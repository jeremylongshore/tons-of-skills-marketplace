---
name: analyzing-dependencies
description: Audit selected project dependency reports and review declared license
  metadata. Use when auditing third-party libraries. Trigger with 'check dependencies',
  'scan for vulnerabilities', or 'audit packages'.
version: 1.29.0
allowed-tools: Read, Grep, Glob, Bash(security:*), Bash(scan:*), Bash(audit:*)
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - security
  - audit
  - analyzing-dependencies
compatibility: Designed for Claude Code
---

# Analyzing Dependencies

## Overview

Run the existing dependency checker against a user-selected project root, or
normalize an existing audit report. Preserve known findings, unknown severity,
and incomplete coverage separately. The bundled scanner supports npm, Python
requirements, Composer, Bundler and Cargo. It does not implement Go auditing,
outdated-version research, recursive workspace discovery or automatic fixes.

## Prerequisites

Identify the target project directory before running anything. The current
working directory selects the project; `${CLAUDE_SKILL_DIR}` locates this skill's
bundled resources and is not the target project directory.

Python 3.10+ runs the bundled scripts. Live scanning additionally requires the
selected audit executables already installed and advisory access permitted by
the operator. Audit requests can disclose package names and versions to configured
services. Confirm the intended project, registry/database configuration and
permission to make those requests. Do not install tools, generate locks, resolve
requirements, upgrade dependencies or run repair commands automatically.

## Workflow

1. Use Glob to locate root manifests, Read to inspect them and Grep to find
   relevant configuration keys without printing credentials. Read the selected root manifests and identify supported ecosystems. npm,
   Composer, Bundler and Cargo require an existing lock file. Python requires an
   explicit pinned `requirements.txt`; `pyproject.toml` or Pipfile alone is not
   sufficient. Unsupported or unavailable coverage is unassessed, never clean.
2. Prefer an existing report when live access is unnecessary. Run the bundled
   formatter with `--input`; inspect its complete/status/errors fields and exit
   status. A valid format is not a finding-free result.
3. If live scanning is authorized, invoke `scripts/dependency_check.sh` from the
   project root with `--tool npm|pip|composer|bundler|cargo`, or omit `--tool` to
   select supported root manifests. Preserve the report and process exit status.
   The wrapper executes each selected audit once, without installing or fixing.
4. Read findings and errors together. Native errors, missing tools, invalid JSON,
   timeouts, skipped Python dependencies, unavailable advisory sources and
   contradictory counts produce incomplete coverage. Partial findings remain
   actionable even when another ecosystem fails.
5. Preserve identifiers and severity supplied by the report. Missing severity is
   `UNKNOWN` and remains visible. Do not invent CVEs, installed versions, CVSS
   scores, dependency paths or patched releases. Verify remediation against the
   actual advisory before proposing a change; do not execute upgrades here.
6. When requested, inventory license declarations with the bundled license
   checker. npm uses the installed tree; Python requires an explicit absolute
   executable via `--python`. This describes that environment, not proof of
   requirements closure. Unknown IDs and compound expressions need review.
   Metadata categories and legacy hints do not establish legal compatibility.
7. Report the exact project scope, selected tools, complete/incomplete outcome,
   unfiltered and visible finding counts, unknowns and unresolved review items.
   Keep live audit coverage distinct from report-only formatting and license
   metadata review. No result establishes DoD/STIG compliance.

## Examples

Execute from the selected project directory. These examples use the skill's
resource location; retain the user's normal execution permission boundaries.

```bash
bash "${CLAUDE_SKILL_DIR}/scripts/dependency_check.sh" --tool npm --format json
python3 "${CLAUDE_SKILL_DIR}/scripts/vulnerability_report_parser.py" --input audit.json --format json
python3 "${CLAUDE_SKILL_DIR}/scripts/vulnerability_report_parser.py" --input audit.json --format markdown --severity high --fail-on-findings
python3 "${CLAUDE_SKILL_DIR}/scripts/license_compliance_checker.py" --format json --python /absolute/path/to/project/.venv/bin/python
```

Do not treat the interpreter path in the example as a discovered environment.
Select an existing environment explicitly. Python inventory runs `piplicenses`
from a private empty working directory so project configuration cannot silently
filter packages; it does not install that module.

## Output

| Entry point        | 0                                                             | 1                                                                                | 2                                                       |
| ------------------ | ------------------------------------------------------------- | -------------------------------------------------------------------------------- | ------------------------------------------------------- |
| Dependency scanner | Complete, no known findings or review flags in selected scope | Findings or review flags                                                         | Incomplete scan, output failure or invalid usage        |
| License checker    | Complete metadata inventory, no automated review flags        | Manual review required                                                           | Incomplete enumeration, output failure or invalid usage |
| Report formatter   | Valid complete report, possibly with findings                 | Invalid/incomplete report, output failure, or findings with `--fail-on-findings` | Invalid CLI usage                                       |

Scanner JSON contains one document with `complete`, `status`, `scope`, `tools`,
`errors`, `warnings`, `summary` and `vulnerabilities`. `summary.unfiltered_total`
controls findings regardless of `--severity`; `summary.total` is the displayed
count. Unknown severity is never hidden. A filtered normalized report omits
findings and cannot later prove a complete scan: use the unfiltered report for
reprocessing. CSV is a finding-row export; preserve the process exit status and
JSON report alongside it to retain coverage and errors.

`--output` writes an atomic private file and refuses a symlink destination.
Without it, the report goes to stdout. Do not publish reports containing private
package names. Native error bodies are not echoed; this is not general-purpose
secret redaction or an operating-system sandbox. `--timeout` is a per-tool
limit greater than zero and at most 300 seconds; increasing it is an explicit
operator choice, not a reason to restart an observed live job.

## Error Handling

- Missing tool or lock: report incomplete and identify the missing prerequisite.
  Do not install, generate a lock or silently substitute an unrelated inventory.
- Network/database failure or private package skip: retain partial findings and
  mark coverage incomplete; absence of an advisory is not verified safety.
- No supported root: report unassessed scope. For workspaces, select each intended
  root explicitly and retain separate coverage records.
- Unknown license expression: retain the exact declaration for contextual review;
  do not accept a compound expression merely because it contains `MIT`.

## Resources

See [script contracts](scripts/README.md), [primary references](references/README.md)
and [report template](assets/README.md) for supporting resources.
