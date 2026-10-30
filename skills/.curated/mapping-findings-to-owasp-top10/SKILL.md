---
name: mapping-findings-to-owasp-top10
description: |
  Annotate every pentest finding with its OWASP Top 10 (2021)
  category by applying a deterministic rule table keyed on source
  skill, finding category, detail keywords, and CWE identifier when
  present. Produces an enriched findings JSONL plus a per-category
  rollup report showing how findings distribute across A01 through
  A10. Required for customer-facing OWASP coverage sections and
  compliance contexts (PCI DSS 6.5, SOC2 CC7, ISO 27001 A.14.2).
  Use when: enriching findings after cluster 1-4 scans, regenerating
  the report with OWASP tags, producing the OWASP coverage section
  for an exec summary, or auditing engagement OWASP coverage.
  Threshold: unclassifiable findings emitted as INFO with UNMAPPED
  category for operator review.
  Trigger with: "map to OWASP", "owasp top 10 mapping",
  "annotate owasp categories", "owasp coverage check".
allowed-tools:
  - Read
  - Write
  - Bash(python3:*)
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
  - reporting
  - owasp
  - top10
  - pentest
---

# Mapping Findings to OWASP Top 10

## Overview

OWASP Top 10 is the canonical taxonomy of web-application risk
categories. Every customer-facing pentest report has an "OWASP
coverage" section because customers, auditors, and insurers
expect to see findings mapped against the Top 10. Without the
mapping, a long list of CVEs and misconfigurations reads as
noise; with the mapping, it reads as a structured assessment.

This skill applies a deterministic rule table to annotate each
finding with its OWASP category. Rules are keyed on:

1. **Source skill ID** (a finding from `auditing-npm-dependencies`
   is almost always A06 — Vulnerable and Outdated Components).
2. **Finding category** (the per-skill category tag, e.g.
   `dependency-vulnerability`, `engagement-scope`).
3. **CWE identifier** if present (CWE → OWASP is a well-trodden
   mapping; OWASP themselves publish the cross-walk).
4. **Detail keywords** as a fallback when the above don't
   determine a category.

Output is an enriched JSONL (each finding gets an `owasp_category`
field) plus a coverage report showing how the engagement's
findings distribute across A01-A10. UNMAPPED findings are
surfaced for human review — extend the rule table or accept the
finding as cross-cutting (some findings genuinely don't fit a
single A0X bucket).

## When the skill produces findings

| Finding | Severity | Threshold | Affected control |
|---|---|---|---|
| Finding unmapped after rule application | **INFO** | No rule matched the finding | (operational) |
| Source JSONL unparseable | **HIGH** | Standard JSONL parse error | (operational) |
| Annotation written back successfully | **INFO** | Confirmation per source file | (informational) |
| Coverage report generated | **INFO** | Coverage report path emitted | (informational) |
| Engagement covers all 10 categories | **INFO** | At least one finding in each A01-A10 bucket | (positive observation) |
| Engagement covers <5 of 10 categories | **MEDIUM** | Suggests scope may have been narrow | (informational) |

## OWASP Top 10 (2021) reference

| Category | Description |
|---|---|
| A01:2021 | Broken Access Control |
| A02:2021 | Cryptographic Failures |
| A03:2021 | Injection |
| A04:2021 | Insecure Design |
| A05:2021 | Security Misconfiguration |
| A06:2021 | Vulnerable and Outdated Components |
| A07:2021 | Identification and Authentication Failures |
| A08:2021 | Software and Data Integrity Failures |
| A09:2021 | Security Logging and Monitoring Failures |
| A10:2021 | Server-Side Request Forgery |

## Prerequisites

- Python 3.9+
- One or more cluster 1-4 findings files
- Optional `.owasp-overrides.yaml` for engagement-specific
  classification rules

## Instructions

### Step 1 — Identify findings sources

Default: every file under `engagement/findings/*.json[l]`.
Override with `--source FILE` (repeatable).

### Step 2 — Run the mapper

```bash
python3 ./scripts/map_owasp.py engagements/acme-2026-q2/
```

Options:

```
Usage: map_owasp.py PATH [OPTIONS]

Options:
  --source FILE           Specific findings file (repeatable)
  --enrich-output FILE    Write annotated findings JSONL here
                          (default: PATH/findings/all-with-owasp.jsonl)
  --coverage-output FILE  Coverage report path
                          (default: PATH/reports/owasp-coverage.md)
  --overrides FILE        Optional rule-overrides YAML
  --output FILE           Operational findings output
  --format FMT            json | jsonl | markdown (default: markdown)
  --min-severity SEV      default info
```

### Step 3 — Review unmapped findings

UNMAPPED findings are surfaced as INFO. For each:

1. Check whether a CWE was present; if so, the canonical CWE →
   OWASP cross-walk should have caught it. Extend the rule table.
2. Check whether the finding's source skill ID is in the rule
   table; if not, add a skill-level default.
3. If the finding genuinely doesn't fit a single A0X bucket,
   accept UNMAPPED and document in the engagement notes.

### Step 4 — Read the coverage report

The coverage report lists each A0X category with:

- Count of findings mapped to that category
- Severity breakdown within the category
- Pointer to specific findings

For an engagement intended as broad-coverage testing, all ten
categories should have at least one entry. Categories with zero
findings either reflect scope ("we didn't test for this") or
clean results ("we tested and found nothing").

## Examples

### Example 1 — End-of-engagement enrichment

```bash
python3 ./scripts/map_owasp.py engagements/acme-2026-q2/
```

Produces `engagements/acme-2026-q2/findings/all-with-owasp.jsonl`
(enriched findings) and `engagements/acme-2026-q2/reports/owasp-coverage.md`
(coverage report).

### Example 2 — Apply engagement-specific overrides

```yaml
# .owasp-overrides.yaml — engagement-specific classifications
- skill_id: auditing-cors-policy
  owasp_category: A05:2021 — Security Misconfiguration
  reason: customer treats CORS as misconfig, not access-control
- skill_id: scanning-for-hardcoded-secrets
  detail_contains: ".env"
  owasp_category: A02:2021 — Cryptographic Failures
  reason: env-file leaks treated as crypto failure for this engagement
```

```bash
python3 ./scripts/map_owasp.py engagements/acme-2026-q2/ \
    --overrides engagements/acme-2026-q2/.owasp-overrides.yaml
```

### Example 3 — Coverage audit (no enrichment write-back)

```bash
python3 ./scripts/map_owasp.py engagements/acme-2026-q2/ \
    --enrich-output /dev/null \
    --coverage-output /tmp/coverage.md
```

Produces the coverage report without modifying findings files.

## Output

JSON / JSONL / Markdown per `lib/report.py` for operational
findings. PRIMARY outputs:

1. **Enriched findings JSONL** at `--enrich-output` — every
   finding from the sources has an `owasp_category` field added.
2. **Coverage report markdown** at `--coverage-output` — per-
   category rollup.

Each operational Finding includes:

- `id` — `owasp::<issue>::<finding-fingerprint>`
- `severity` — INFO mostly; HIGH for parse errors
- `category` — `owasp-mapping`
- `summary` — what happened to the finding
- `evidence` — original finding fingerprint, derived OWASP
  category, rule that matched

## Error Handling

- **PATH missing** → CRITICAL operational finding, exits 1.
- **Source file unparseable** → HIGH op finding, skip file.
- **No sources found** → HIGH op finding, exits 1.
- **Override YAML unparseable** → HIGH op finding, falls back to
  default rules.
- **Enriched output path not writable** → HIGH op finding, exits 1.

## Resources

- `references/THEORY.md` — OWASP Top 10 history and 2021 changes,
  CWE → OWASP cross-walk, rule-table design rationale, when a
  finding genuinely doesn't fit, OWASP A0X precision tradeoffs
  (broad categories vs specific findings)
- `references/PLAYBOOK.md` — Default rule table per cluster 1-4
  skill, override YAML format, coverage-audit interpretation,
  customer-specific category preferences, integration with
  PCI DSS 6.5 / NIST 800-53 control mapping
