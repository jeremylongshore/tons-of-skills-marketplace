---
name: performing-penetration-testing
description: |
  Route approved security work to the pack's 25 narrow operators, with
  authorization/scope gates, retained evidence and compatible report inputs.
  Use when starting a pentest, auditing dependencies or source code, checking
  an approved URL, or preparing engagement deliverables. Familiar requests
  route to the appropriate operator; retained legacy CLIs keep separate
  completion and JSON contracts. Trigger with "pentest", "security scan",
  "audit dependencies", "check headers", "find secrets", or "OWASP coverage".
argument-hint: "[engagement-directory] [approved security job]"
allowed-tools:
  - Read
  - Write
  - Glob
  - Grep
  - Bash(python3:*)
disallowed-tools:
  - Bash(rm:*)
  - Bash(curl:*)
  - Bash(wget:*)
  - Bash(nmap:*)
  - Bash(nikto:*)
  - Bash(sqlmap:*)
  - Write(.env)
  - Edit(.env)
version: 3.33.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Designed for Claude Code
tags:
  - security
  - testing
  - pentest
  - orchestration
---

# Performing Penetration Testing

## Overview

Route an approved engagement across 25 narrow operator skills plus this
orchestrator. Each invoked CLI has its own arguments, evidence requirements
and exit status.

## Prerequisites

Use Read for approved ROE and saved findings, Glob/Grep to select artifacts,
and Write only for requested engagement outputs. These routing instructions
depend on each CLI's own input and evidence checks; reports do not certify
compliance.

Obtain the owner's authorization and approved targets before scanning. The
structural authorization checker validates metadata, scope and time windows;
a successful check does not verify signing identity or establish legal authority.
Keep the approved ROE, target handoffs and requested local repository/environment
paths with the engagement evidence. Do not install missing scanners automatically.

## Instructions

### Step 1 — Select the operator job

Match the requested job in the routing table. Select only the relevant operators;
no full scan, write/proxy experiment, signing or service activation follows merely
from a broad request to inspect a project. The HTTP-method operator defaults to
OPTIONS; each active method has its separate ROE, opt-in and ledger contract.

### Step 2 — Complete authorization and scope gates

Run `confirming-pentest-authorization` and `defining-pentest-scope` before any
cluster 1–4 operator, including ad-hoc work. Require both CLI exit codes to be 0.
A HIGH or CRITICAL governance finding, invalid ROE, unsupported target or any
other nonzero gate stops the dependent scan; severity filtering cannot grant
permission. Verify each network target with the authorization checker's
`--check-target` and use only successfully emitted scope handoffs.

The scope CLI covers supported network identities. Approval of exact local
repository and Python-environment paths must be established separately; do not
claim it validates arbitrary filesystem paths or that changing cwd selects a
Python environment.

### Step 3 — Execute selected checks and retain their status

For narrow v3 operators, persist canonical Finding JSON/JSONL with the skill's
actual `--output`/`--format` arguments. Preserve the unfiltered gate alongside
its report. Exit 1 from a completed scan records security findings; it does not
invalidate the preceding authorization. Exit 2 or missing completion evidence
marks dependent conclusions incomplete. Other approved independent checks may
continue only without hiding that incomplete coverage.

The legacy routes retain separate v2 report shapes, with explicit completion and
error metadata. Keep those reports separate from canonical Finding streams.
Their CLI does not execute this orchestrator's ROE gate. Invoke them only after
the governance steps; use narrow v3 operators when canonical report composition
is required. The mapping table below describes related jobs, not schema parity.

### Step 4 — Compose evidence-backed deliverables

Use verified canonical sources with `mapping-findings-to-owasp-top10`, then
`composing-vulnerability-report`, then `generating-executive-summary`. Inspect
the sources and each operational exit status; a later report writer returning 0
does not erase a source scan's finding or incomplete gate. The aggregate outcome
retains incomplete evidence before a known security-finding outcome before clean.
Label partial deliverables and unknown coverage explicitly.

Run `recording-pentest-engagement` for a checksum manifest. An archive is produced
only when `--tar` is supplied, outside the evidence tree. Signing is optional and
requires separately approved signer/key access; never create keys or infer
signing authorization. A hash manifest or optional signature is not a certified
chain of custody.

## Intent routing

Every scan row requires the authorization and scope gates from Step 2.

| Intent | Required inputs/gates | Operators in order |
| --- | --- | --- |
| Full engagement | Authorization + scope | Relevant cluster 1–4 operators, then evidence-backed reporting |
| Headers / URL | Authorization + scope | checking-http-security-headers, analyzing-tls-config, detecting-ssl-cert-issues |
| CORS | Authorization + scope | auditing-cors-policy |
| TLS / certificate | Authorization + scope | analyzing-tls-config, detecting-ssl-cert-issues |
| npm dependencies | Authorization + scope + approved project path | auditing-npm-dependencies |
| Python dependencies | Authorization + scope + declared requirements/environment | auditing-python-dependencies |
| Vulnerable dependency trace | Authorization + scope + saved advisory input | Dependency audit, then tracing-transitive-vulnerabilities |
| License review | Authorization + scope + approved project path | checking-license-compliance |
| Secret scan | Authorization + scope + approved source path | scanning-for-hardcoded-secrets |
| SQL / command injection | Authorization + scope + approved source path | The matching cluster 3 pattern operator |
| Static code audit | Authorization + scope + approved source path | Relevant cluster 3 operators |
| OWASP coverage | Verified canonical findings and declared tested coverage | mapping-findings-to-owasp-top10; coverage is not proof all risks were tested |
| ROE / scope review | Proposed engagement metadata | confirming-pentest-authorization, defining-pentest-scope |
| Reports / summary | Verified canonical source artifacts | composing-vulnerability-report, generating-executive-summary |
| Evidence archive | Reviewed evidence tree and explicit archive/signing choices | recording-pentest-engagement |

## Skill index: 25 operators plus this orchestrator

### Cluster 0 — Orchestration

- `performing-penetration-testing` — this skill

### Cluster 1 — Network / transport (5)

- `analyzing-tls-config` — TLS protocol versions, cipher suites, HSTS
- `detecting-ssl-cert-issues` — cert validity, expiry, chain integrity
- `auditing-cors-policy` — origin reflection, credential bypass, wildcard
- `checking-http-security-headers` — CSP, HSTS, X-Frame-Options, etc.
- `probing-dangerous-http-methods` — method discovery and approved disposable-fixture experiments

### Cluster 2 — Information disclosure (4)

- `detecting-exposed-secrets-files` — `.env`, `.git`, backup files
- `detecting-debug-endpoints` — `/server-status`, admin panels
- `fingerprinting-server-software` — Server-header version exposure
- `detecting-directory-listing` — Apache/nginx autoindex

### Cluster 3 — Source-code static analysis (6)

- `scanning-for-hardcoded-secrets` — AWS / GitHub / Stripe / Slack / API keys
- `detecting-sql-injection-patterns` — string-concat SQL, unsanitized input
- `detecting-command-injection-patterns` — shell exec with user input
- `detecting-eval-exec-usage` — eval/exec with dynamic content
- `detecting-insecure-deserialization` — pickle/yaml.load/Marshal use
- `detecting-weak-cryptography` — MD5/SHA1/DES, hardcoded IVs, ECB mode

### Cluster 4 — Dependency analysis (4)

- `auditing-npm-dependencies` — `npm audit` wrapper with v1/v2 parsers
- `auditing-python-dependencies` — `pip-audit` wrapper with OSV scoring
- `checking-license-compliance` — SPDX classification + copyleft contamination
- `tracing-transitive-vulnerabilities` — dep-graph leverage analysis

### Cluster 5 — Engagement governance (3, new in v3)

- `confirming-pentest-authorization` — Rules of Engagement validation
- `defining-pentest-scope` — target enumeration + IP allowlist
- `recording-pentest-engagement` — SHA-256 manifest + GPG signing

### Cluster 6 — Reporting (3, new in v3)

- `composing-vulnerability-report` — unified deliverable report
- `mapping-findings-to-owasp-top10` — A0X classification + coverage rollup
- `generating-executive-summary` — 0-100 risk score + top-3 priorities

## End-to-end workflow

For a typical engagement, the orchestrator routes through:

```
                  +----------------------------------+
                  | confirming-pentest-authorization |
                  +-------------+--------------------+
                                | (CRITICAL halts here)
                                v
                  +----------------------------------+
                  | defining-pentest-scope            |
                  +-------------+--------------------+
                                |
                                v
   +-------------+-------------+-------------+-------------+
   | Cluster 1   | Cluster 2   | Cluster 3   | Cluster 4   |
   | (5 skills)  | (4 skills)  | (6 skills)  | (4 skills)  |
   +-------------+-------------+-------------+-------------+
                                |
                                v
                  +----------------------------------+
                  | mapping-findings-to-owasp-top10   |
                  +-------------+--------------------+
                                |
                                v
                  +----------------------------------+
                  | composing-vulnerability-report    |
                  +-------------+--------------------+
                                |
                                v
                  +----------------------------------+
                  | generating-executive-summary      |
                  +-------------+--------------------+
                                |
                                v
                  +----------------------------------+
                  | recording-pentest-engagement      |
                  +----------------------------------+
```

## Backward compatibility and migration

Keep the three legacy paths and their existing flags for compatibility. Corrected
failure behavior is deliberate: an unavailable/invalid selected scanner returns
incomplete exit 2, even if old versions reported clean. Display filters do not
change the unfiltered gate. Code matches are redacted; incomplete web checks have
no numeric risk score. No scanner is installed automatically.

Python legacy auditing requires pinned `requirements.txt`, or an explicit
`--python /approved/project/.venv/bin/python`. Requirements mode disables pip
resolution and audits the supplied pins; it does not claim transitive closure.
Environment mode audits the designated interpreter and runs pip check there,
using isolated Python mode to exclude the project cwd, PYTHONPATH and user-site
module lookup. The auditor must already be installed in that environment.
It does not prove that environment matches a project's lockfile. Preserve the
venv's lexical interpreter path. An advisory without severity remains unknown
and requires triage; it is not assigned a fabricated moderate rating.

| Retained legacy job | Related narrow v3 operators |
| --- | --- |
| security_scanner.py --checks headers | checking-http-security-headers |
| security_scanner.py --checks ssl | analyzing-tls-config, detecting-ssl-cert-issues |
| security_scanner.py --checks cors | auditing-cors-policy |
| security_scanner.py --checks endpoints | detecting-exposed-secrets-files, detecting-debug-endpoints |
| security_scanner.py --checks methods | probing-dangerous-http-methods; advertisement alone is not exploitation |
| dependency_auditor.py --scanners npm | auditing-npm-dependencies |
| dependency_auditor.py --scanners pip | auditing-python-dependencies, with its own input contract |
| code_security_scanner.py | Relevant cluster 3 pattern operators |

## Examples

### Governance before an approved network check

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/confirming-pentest-authorization/scripts/check_authorization.py \
  --roe engagement/roe.yaml --check-target https://fixture.example.test \
  --format json --output engagement/authorization.json
```

Inspect exit 0 and the actual result before running scope validation:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/defining-pentest-scope/scripts/define_scope.py \
  --roe engagement/roe.yaml --emit-allowlist engagement/approved-allowlist.txt \
  --emit-targets engagement/approved-targets.json --format json
```

Run only the approved relevant operator after both gates pass. These are
documentation examples, not authorization to scan that host.

### Legacy Python audit in an explicitly approved environment

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/performing-penetration-testing/scripts/dependency_auditor.py \
  /approved/project --scanners pip --python /approved/project/.venv/bin/python \
  --output engagement/legacy-python.json
```

Keep this v2 JSON report separate from canonical v3 Finding JSONL.

### Canonical reporting from saved findings

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/mapping-findings-to-owasp-top10/scripts/map_owasp.py \
  engagement --source engagement/findings/scan.jsonl \
  --enrich-output engagement/findings/all-with-owasp.jsonl \
  --coverage-output engagement/reports/owasp-coverage.md
```

Then use `compose_report.py engagement --source <canonical findings>
--report-output <file>` and `exec_summary.py engagement --source <canonical
findings> --coverage <coverage file> --summary-output <file>`, through their
respective skill instructions. Verify the source and format expectations before
composition; do not relabel legacy JSON as JSONL.

## Output

A full engagement can produce enriched canonical findings, an OWASP coverage
report, a vulnerability report, an executive summary and a checksum manifest.
Archive/signature artifacts are conditional on explicit options. Preserve source
reports, incomplete outcomes, approval/scope evidence and the provenance of each
included result; report creation alone does not prove a completed assessment.

## Error Handling

- Governance nonzero: stop dependent scanning; repair the authorization/scope input.
- Missing tool or failed transport/parser: incomplete, nonzero; no automatic install.
- Completed HIGH/CRITICAL scan finding: retain the finding and its nonzero gate.
- Unknown advisory severity: show the unknown result and incomplete assessment.
- Missing or incompatible report input: stop dependent composition or clearly label
  an explicitly requested partial deliverable; do not claim full coverage.
- Failed archive/signature operation: preserve original evidence and report the
  failure; do not replace a valid manifest or signature with a claimed success.

## Resources

- [OWASP background](references/OWASP_TOP_10.md)
- [Legacy header-check reference](references/SECURITY_HEADERS.md)
- [Remediation reference](references/REMEDIATION_PLAYBOOK.md)
- [pip-audit input and exit contracts](https://github.com/pypa/pip-audit#usage)

For each narrow operator, read its own SKILL.md and references. This routing
update preserves the 25 narrow jobs and the existing compatibility entry points;
it does not approve a wider skill, MCP, signing or release phase.
