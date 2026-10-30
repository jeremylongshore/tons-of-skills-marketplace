---
name: tracing-transitive-vulnerabilities
description: |
  Build a dependency-tree map of a project (npm or Python) and trace
  the path from each known-vulnerable transitive package back to one
  or more direct dependencies. Identifies which direct-dep bump would
  clear the most findings at once (highest-leverage upgrade), which
  vulnerabilities are unreachable through any version bump and
  require overrides or vendor-patch, and which CVEs sit at deep
  transitive depth (3+ levels from a direct dep) where blast-radius
  triage is hardest.
  Use when: a multi-finding audit produces noise and you need to
  prioritize, when planning a major dependency refresh, after an
  upstream package compromise hits your tree (e.g. event-stream
  flatmap-stream), or when an audit shows findings that automated
  fix commands cannot auto-resolve.
  Threshold: any HIGH or CRITICAL CVE reachable only through
  transitive paths that no single direct-dep bump can clear.
  Trigger with: "trace transitive vulns", "find dep paths", "SBOM
  vuln trace", "which direct dep pulls this CVE".
allowed-tools:
  - Read
  - Bash(npm:*)
  - Bash(pip:*)
  - Bash(pip-audit:*)
  - Bash(python3:*)
  - Bash(pipdeptree:*)
  - Glob
disallowed-tools:
  - Bash(rm:*)
  - Bash(curl:*)
  - Bash(wget:*)
  - Write(.env)
  - Edit(.env)
  - Bash(npm install:*)
  - Bash(pip install:*)
version: 3.33.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Designed for Claude Code
tags:
  - security
  - sbom
  - transitive-dependency
  - dependency-graph
  - pentest
---

# Tracing Transitive Vulnerabilities

## Overview

The auditing-npm-dependencies and auditing-python-dependencies skills
each surface CVEs, but they don't answer the question that actually
decides remediation order: **which of these findings can I clear by
bumping ONE direct dep, and which require deeper intervention?**

That question is the core of supply-chain triage. A high-CVSS CVE
in `lodash@4.17.4` is alarming on first read. If it's pulled in by
five different direct deps, the right fix may not be to bump any of
them — it may be a single root-level `overrides` entry pinning
`lodash@^4.17.21`. The triage discussion goes very differently when
you can quote: "this CVE is reachable via 5 paths, all of which
flow through `webpack`, which has a fixed version available." That
shifts a project-wide panic to a one-line PR.

This skill walks the project's dependency graph (via `npm ls`,
`pipdeptree`, or equivalent), intersects it with the CVE findings
already produced by the per-language audit skills, and emits a
trace report that includes:

- For each CVE: the full path(s) from direct dep → ... → vulnerable package
- For each direct dep: the count of CVEs reachable through it
- "Highest-leverage upgrade" recommendation — the single direct-dep
  bump that clears the most findings at once
- "Unreachable" findings — CVEs whose vulnerable version range is
  forced by EVERY parent in the path, requiring overrides or
  vendor-patch
- "Deep transitive" findings (≥3 levels from a direct dep) — these
  are highest-risk for hidden surprises because the relationship to
  your code is most opaque

## When the skill produces findings

| Finding | Severity | Threshold | Affected control |
|---|---|---|---|
| Critical CVE at deep transitive depth (≥3) | **HIGH** | Depth ≥3 + severity CRITICAL — blast radius unclear | CWE-1395 |
| High CVE reachable only via overrides | **HIGH** | No direct-dep version clears the finding | CWE-1395 |
| Multi-CVE direct-dep hotspot | **MEDIUM** | Single direct dep is ancestor for ≥3 separate CVEs | (informational) |
| Direct-dep bump clears N findings | **INFO** | Reports the recommended bump | (operational) |
| Unreachable CVE (no fix in any reachable version) | **HIGH** | Finding has no fix-available across the whole graph | CWE-1395 |
| Circular dep with CVE | **MEDIUM** | Cycle in the dep graph involves a vulnerable package | (operational) |

## Prerequisites

- Python 3.9+
- npm or pip available (depending on project type)
- `pipdeptree` (optional but recommended for Python; falls back to
  `pip show` chains if absent — slower but works)
- An existing audit JSON file from auditing-npm-dependencies or
  auditing-python-dependencies, OR the willingness to let this
  skill run those audits itself

## Instructions

### Step 1 — Identify the scan target

The skill auto-detects whether the project is npm-flavored
(`package.json` + `node_modules`) or Python-flavored
(`pyproject.toml` / `requirements.txt` / installed venv).

### Step 2 — Acquire audit data

The skill can run the per-language audit itself, or consume a
pre-produced audit JSON:

```bash
# Self-running mode
python3 ./scripts/trace_vulns.py /path/to/project

# Pre-produced mode (faster on re-runs)
python3 plugins/security/penetration-tester/skills/auditing-npm-dependencies/scripts/audit_npm.py \
    /path/to/project --format json --output /tmp/audit.json
python3 ./scripts/trace_vulns.py /path/to/project --audit-input /tmp/audit.json
```

### Step 3 — Walk the graph

For npm, the skill calls `npm ls --json --all` to enumerate the
full installed tree. For Python, it calls `pipdeptree --json-tree`
or falls back to recursive `pip show`.

The resulting graph is intersected with the per-package CVE
findings, producing a path list for each vulnerability.

### Step 4 — Triage by leverage

The report ranks findings by:

1. Severity (CRITICAL → HIGH → MEDIUM → LOW)
2. Depth in the graph (deeper = more uncertain blast radius)
3. Number of reachable paths (more paths = harder to clear with a
   single bump)

For each direct dep, the report aggregates:

- Total reachable CVE count
- Severity breakdown
- Suggested bump version (if available)

### Step 5 — Plan the upgrades

Use the "highest-leverage upgrade" recommendation as the first PR.
Then re-run this skill against the post-upgrade state to confirm
how many findings dropped. Iterate until the residual is overrides /
vendor work only.

## Examples

### Example 1 — Triage a noisy audit

```bash
# Run base audit
python3 plugins/security/penetration-tester/skills/auditing-npm-dependencies/scripts/audit_npm.py \
    . --format json --output /tmp/npm-audit.json

# Trace
python3 ./scripts/trace_vulns.py . --audit-input /tmp/npm-audit.json \
    --format markdown --output /tmp/trace.md
```

`/tmp/trace.md` is human-readable: per-CVE path lists + recommended
bumps + leverage analysis.

### Example 2 — Highest-leverage upgrade discovery

```bash
python3 ./scripts/trace_vulns.py . --format json --leverage-only \
    | jq '.[] | select(.cve_count >= 3)'
```

Surfaces direct deps that, if bumped, would clear ≥3 CVEs at once.

### Example 3 — Deep-transitive risk report

```bash
python3 ./scripts/trace_vulns.py . --min-depth 3 --format markdown \
    --output deep-trace.md
```

Limits output to findings at depth ≥3 from a direct dep — the
hardest-to-triage class.

## Output

JSON / JSONL / Markdown per `lib/report.py`. Exit codes: 0 clean,
1 high/critical, 2 error.

Each Finding includes:

- `id` — `trace::<cve-id>::<vulnerable-package>`
- `severity` — re-derived based on depth + reachability
- `category` — `transitive-trace`
- `summary` — short description of the path situation
- `evidence` — original CVE, dep path(s), depth, parent direct-deps,
  recommended bump
- `references` — link back to the source audit finding

A "leverage report" section in markdown output lists the
top-N direct-dep bumps ranked by aggregate CVE-clearance count.

## Error Handling

- **npm ls fails to produce a complete tree** (lockfile out of sync)
  → emits an INFO Finding flagging the desync and proceeds with
  partial data.
- **pipdeptree not installed** → falls back to `pip show` recursion;
  emits INFO finding recommending pipdeptree install for accuracy.
- **No audit findings input AND no audit tool available** → exits
  2 with operational error advising the operator to provide an
  audit JSON via --audit-input.
- **Graph contains cycles** → cycles are detected and broken; each
  package in the cycle is reported once at its shallowest depth.

## Resources

- `references/THEORY.md` — Why deep transitive deps are
  disproportionately risky, dependency-graph traversal theory,
  SBOM (Software Bill of Materials) standards (CycloneDX, SPDX
  3.0), reachability theory for vulnerability analysis,
  exploit-prediction-scoring-system (EPSS) integration plans
- `references/PLAYBOOK.md` — Per-runtime trace patterns, SBOM
  generation patterns (cyclonedx-cli, syft, anchore), graph-based
  upgrade planning, when to override vs vendor-patch, integration
  with the per-language audit skills
