---
name: auditing-npm-dependencies
description: |
  Audit a Node.js project's installed npm dependency tree for known
  CVEs by wrapping the npm audit JSON output and emitting findings in
  the canonical penetration-tester schema. Detects direct AND transitive
  vulnerabilities, normalizes npm's severity scale (info/low/moderate/
  high/critical) to the shared Severity enum, and parses both v1 and
  v2 audit output formats so the skill works against npm 6 and npm
  7+ lockfiles.
  Use when: pre-merge gate on a Node project, post-incident sweep
  after a transitive package compromise (e.g. event-stream, ua-parser,
  node-ipc, color.js), SOC2 vendor-management evidence collection,
  or auditing an inherited or acquired Node codebase.
  Threshold: any HIGH or CRITICAL CVE in the resolved dependency
  tree. MODERATE / LOW reported informationally.
  Trigger with: "audit npm deps", "npm vulnerability scan", "check
  node packages for CVEs", "npm audit".
allowed-tools:
  - Read
  - Bash(npm:*)
  - Bash(python3:*)
  - Glob
disallowed-tools:
  - Bash(rm:*)
  - Bash(curl:*)
  - Bash(wget:*)
  - Write(.env)
  - Edit(.env)
  - Bash(npm publish:*)
  - Bash(npm install:*)
version: 3.33.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Designed for Claude Code
tags:
  - security
  - dependency-audit
  - npm
  - cve
  - pentest
---

# Auditing npm Dependencies

## Overview

Modern Node.js applications pull in hundreds of transitive packages
through a single `npm install`. The ratio of direct-to-transitive
dependencies on a typical app is around 1:50 — install 30 packages,
end up with 1,500. Every one of those packages can ship a CVE, get
maintainer-takeover-attacked, or contain a typosquatted near-name
package that someone slipped into your lockfile.

The published-CVE feed for npm is among the busiest in the ecosystem
because the registry is shared, public, and trivially installable.
`npm audit` queries the same advisory database GitHub's Dependabot
uses, returning per-package vulnerability records with CVE ID,
severity, affected version range, and fix-available version. Running
it is free and fast; the friction is interpreting the output and
deciding which findings actually block your release.

This skill standardizes that interpretation. It wraps `npm audit
--json`, parses both the v1 (npm 6) and v2 (npm 7+) output shapes,
maps npm's severity vocabulary to the shared Severity enum, and
emits Findings in the canonical penetration-tester JSON shape so
downstream tooling (CI gates, security dashboards, SOC2 evidence
collection) gets uniform records regardless of which package
manager surfaced them.

## When the skill produces findings

| Finding | Severity | Threshold | Affected control |
|---|---|---|---|
| Critical CVE in direct dep | **CRITICAL** | npm `severity: critical` AND package in `dependencies` of root `package.json` | CWE-1104 |
| Critical CVE in transitive dep | **CRITICAL** | npm `severity: critical` AND package NOT in root `dependencies` | CWE-1104 |
| High CVE in direct dep | **HIGH** | npm `severity: high` AND direct | CWE-1104 |
| High CVE in transitive dep | **HIGH** | npm `severity: high` AND transitive | CWE-1104 |
| Moderate CVE | **MEDIUM** | npm `severity: moderate` | CWE-1104 |
| Low CVE | **LOW** | npm `severity: low` | CWE-1104 |
| Info advisory | **INFO** | npm `severity: info` | CWE-1104 |
| Vulnerable package with no patch | **HIGH** | finding has no `fix.available` and severity ≥ moderate | CWE-1395 |
| Audit registry unreachable | **INFO** | npm exits non-zero with network error | (operational) |
| Audit returns malformed output | **INFO** | JSON parse fails on `npm audit --json` stdout | (operational) |

Direct vs transitive matters: a CVE in `lodash` you require directly
is fixable by upgrading your `package.json`. A CVE in `lodash` pulled
in transitively through `aws-sdk` requires either upgrading `aws-sdk`
to a version with a newer `lodash` floor, or pinning via `overrides`
in your root `package.json`.

## Prerequisites

- Node.js + npm installed on the host running the scan (npm 6+
  supported; npm 7+ recommended for richer output)
- Target project directory containing `package.json` and at minimum
  one of `package-lock.json`, `npm-shrinkwrap.json`
- Network access to the npm registry (`registry.npmjs.org` by default)

## Instructions

### Step 1 — Identify the scan target

Locate the project directory. The scanner expects `package.json` at
the directory root. Monorepos with multiple `package.json` files
should be scanned per package; the scanner does not auto-traverse
workspaces (use `npm audit --workspaces` separately for that case).

### Step 2 — Run the audit

```bash
python3 ./scripts/audit_npm.py /path/to/node-project
```

Options:

```
Usage: audit_npm.py PATH [OPTIONS]

Options:
  --output FILE      Write findings to FILE (default: stdout)
  --format FMT       json | jsonl | markdown (default: markdown)
  --min-severity SEV (default: info)
  --include-dev      Audit `devDependencies` too (default: prod only)
  --no-cache         Pass --no-audit-cache to npm (slower; fresh data)
  --json-only        Print raw `npm audit --json` and exit (debug)
```

The scanner shells out to `npm audit --json` in the target directory,
parses the output, deduplicates per-CVE across direct and transitive
paths, and emits one Finding per CVE.

### Step 3 — Interpret findings

CRITICAL / HIGH = block the release. Either bump the vulnerable
package to the fix version (most common), or apply an npm `overrides`
entry if the transitive dep can't be reached through a parent bump.

MEDIUM / LOW = file a remediation ticket but don't block. These often
require waiting for the upstream maintainer to ship a fix.

INFO = log only. Informational advisories sometimes flag deprecated
packages without an active vulnerability.

### Step 4 — Remediation

For a CVE in a DIRECT dep:

1. Run `npm audit fix` — npm attempts a non-breaking upgrade.
2. If `npm audit fix` says "requires manual review" (semver-major
   bump), evaluate the breaking changes and decide whether to upgrade
   or accept the risk. Document the decision.
3. Pin the resolved version in `package-lock.json`; commit the diff.

For a CVE in a TRANSITIVE dep:

1. Identify the path: `npm ls <vulnerable-package>` shows which
   parent(s) pull it in.
2. Check whether bumping the parent picks up the fix: `npm view
   <parent> dependencies` lists the parent's declared range.
3. If parent has a newer version that floors the vulnerable dep above
   the fix-version, upgrade the parent.
4. Otherwise add an `overrides` block in your root `package.json`:

   ```json
   "overrides": {
     "<vulnerable-package>": "<fix-version>"
   }
   ```

   This requires npm 8.3+ and forces the resolution. Document why
   you're overriding — overrides are easy to forget about.

For a CVE with NO fix available:

1. Subscribe to the GitHub Security Advisory for that CVE.
2. If exploitable in your usage context, replace the package or
   vendor it with a private patch.
3. Document the exception with a date for re-evaluation.

## Examples

### Example 1 — Pre-merge gate

```bash
python3 ./scripts/audit_npm.py . --min-severity high --format json --output npm-audit.json
jq -e '. == []' npm-audit.json || { echo "High/critical npm CVE — fix before merge"; exit 1; }
```

### Example 2 — CI scan on every push

```yaml
- name: npm dependency audit
  run: |
    python3 plugins/security/penetration-tester/skills/auditing-npm-dependencies/scripts/audit_npm.py \
        . --min-severity high --format markdown --output npm-audit.md
- name: Upload audit
  uses: actions/upload-artifact@v4
  with:
    name: npm-audit
    path: npm-audit.md
```

### Example 3 — SOC2 evidence collection

```bash
python3 ./scripts/audit_npm.py . --include-dev --no-cache --format json \
    --output evidence/CC7-npm-audit-$(date +%Y%m%d).json
```

`--include-dev` is important for SOC2 evidence: auditors want the
full picture, not just production deps. `--no-cache` ensures the
evidence reflects current advisory data, not yesterday's cache.

## Output

JSON / JSONL / Markdown per `lib/report.py`. Exit codes: 0 clean, 1
high/critical, 2 error.

Each Finding includes:

- `id` — synthesized as `npm-audit::<cve-id>` (or `npm-audit::<advisory-id>` when no CVE assigned)
- `severity` — CRITICAL / HIGH / MEDIUM / LOW / INFO
- `category` — `dependency-vulnerability`
- `summary` — short CVE title
- `evidence` — affected package, affected version range, fix version (if any), dependency path
- `references` — GHSA URL, CVE URL, npm advisory URL

## Error Handling

- **npm not installed** → exits 2 with operational error advising
  the operator to install Node.js.
- **No `package.json`** → exits 2 with "target is not a Node project"
  error.
- **npm registry unreachable** → emits an INFO Finding documenting
  the outage and exits 0 (no actionable security finding).
- **npm audit returns non-JSON garbage** → emits an INFO Finding and
  exits 2. Sometimes happens with corrupt npm cache; advise the
  operator to run `npm cache clean --force` and retry.
- **Lockfile out of sync with `package.json`** → npm warns and
  may produce partial results; the scanner emits an INFO Finding
  flagging the desync and proceeds with whatever data npm returns.

## Resources

- `references/THEORY.md` — Why npm's dependency graph is the largest
  CVE surface in modern software, history of npm supply-chain attacks
  (event-stream, ua-parser-js, color.js, node-ipc), direct-vs-transitive
  remediation theory, when `overrides` are safe, npm audit v1 vs v2
  output schema diff
- `references/PLAYBOOK.md` — Per-runtime remediation patterns
  (frontend webpack/vite, Node server, Electron desktop, Lambda),
  parent-bump decision matrix, override-block templates, GitHub
  Dependabot integration, SOC2 evidence retention policy
