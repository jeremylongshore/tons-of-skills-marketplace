---
name: generating-executive-summary
description: |
  Compose an exec-readable summary from a unified findings JSONL
  plus the OWASP coverage report. Computes a single engagement
  risk score (0-100, severity-weighted with OWASP-breadth and
  governance terms), rolls up findings into headline counts, names
  the top-3 remediation priorities with effort + impact estimates,
  and produces a 1-2 page markdown document for a C-level or board
  audience. Elides technical detail; the vulnerability report is
  the deep document.
  Use when: closing an engagement, preparing the exec-readout
  meeting, packaging for board review, or producing a one-page
  narrative for auditor / insurer / board.
  Threshold: input findings missing produces CRITICAL operational
  finding; otherwise the deliverable is the document itself.
  Trigger with: "generate exec summary", "executive summary",
  "C-level readout", "board pentest summary".
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
  - executive-summary
  - risk-score
  - pentest
---

# Generating Executive Summary

## Overview

The vulnerability report is comprehensive — every finding, full
detail, every reference. The C-level reader doesn't open it. They
ask their security lead "what should I tell the board?" The
security lead needs a one-page answer.

That one-page answer is the executive summary. It states the
engagement's bottom line:

- A single risk score (0-100)
- Headline counts by severity
- Top-3 remediation priorities, each with rough effort + impact
- OWASP Top 10 coverage (where the work landed)
- Engagement scope and authorization summary (what was tested,
  under what authority, in what window)
- Next steps the customer's organization should take

The summary doesn't omit anything important; it just compresses.
The vulnerability report remains the deep artifact for anyone who
needs the technical detail.

This skill consumes the enriched findings JSONL (after OWASP
mapping) + the OWASP coverage report + the ROE, computes the risk
score, picks the top remediation priorities deterministically,
and renders the document.

## When the skill produces findings

| Finding | Severity | Threshold | Affected control |
|---|---|---|---|
| Input findings file missing | **CRITICAL** | Source JSONL doesn't exist | (operational) |
| OWASP coverage report missing | **HIGH** | Coverage referenced but not present | (operational) |
| ROE missing | **MEDIUM** | Can still generate summary but lacks scope/authz context | (operational) |
| Exec summary written cleanly | **INFO** | Confirmation | (informational) |
| Risk score >75 (high engagement risk) | **HIGH** | Computed risk score elevated | (advisory) |
| Risk score >90 (critical engagement risk) | **CRITICAL** | Engagement exposed material risk; needs urgent action | (advisory) |

## Risk score (0-100) composition

The single risk score is the headline number on the exec summary.
The composition is deterministic and documented:

```
risk = clamp(0, 100,
    20 * count(CRITICAL)
  + 10 * count(HIGH)
  +  3 * count(MEDIUM)
  +  1 * count(LOW)
  +  0 * count(INFO)
  +  5 * (count(distinct OWASP categories touched) - 5 if >5 else 0)
  - 10 * 1 if engagement was authorized cleanly and in-scope (governance bonus)
)
```

The first five terms weight by severity. The OWASP-coverage term
adds 5 points per category beyond 5 (a broader-finding engagement
implies broader risk surface). The governance bonus is a -10
adjustment when ROE was clean — explicit recognition that finding
problems in a well-governed engagement is HEALTHIER than finding
the same problems in a chaotic engagement.

Score interpretation:

| Score | Reading |
|---|---|
| 0-25 | Low risk: clean engagement OR very narrow scope |
| 26-50 | Moderate risk: typical engagement with manageable findings |
| 51-75 | Elevated risk: significant findings, remediation planning required |
| 76-90 | High risk: material findings; executive attention warranted |
| 91-100 | Critical risk: urgent remediation required; consider treating as incident |

## Top-3 remediation priorities

The skill picks top-3 priorities deterministically by:

1. Severity (CRITICAL > HIGH > MEDIUM > LOW)
2. Reachability — findings affecting many targets weight higher
3. Tie-breaker: alphabetical by title for stable output

Each priority gets:

- A one-line headline
- Estimated effort (Hours / Days / Weeks)
- Estimated impact (Limited / Significant / Material)
- Pointer to the corresponding finding section in the
  vulnerability report

Effort + impact are heuristic estimates based on the source
skill's category — operator can override via `--priority-overrides`
for cases where the heuristic is wrong.

## Prerequisites

- Python 3.9+
- Findings JSONL at `engagement/findings/all-with-owasp.jsonl`
  (output of `mapping-findings-to-owasp-top10`) OR an explicit
  `--source FILE`
- OWASP coverage report at `engagement/reports/owasp-coverage.md`
  (referenced; optional)
- ROE at `engagement/roe.yaml` (referenced for scope summary)

## Instructions

### Step 1 — Verify the inputs are present

```bash
ls engagements/acme-2026-q2/findings/all-with-owasp.jsonl
ls engagements/acme-2026-q2/reports/owasp-coverage.md
ls engagements/acme-2026-q2/roe.yaml
```

All three should exist for a complete summary. The skill works
without the coverage report or ROE but the summary is less
complete.

### Step 2 — Generate the summary

```bash
python3 ./scripts/exec_summary.py engagements/acme-2026-q2/
```

Options:

```
Usage: exec_summary.py PATH [OPTIONS]

Options:
  --source FILE              Findings JSONL (default: PATH/findings/all-with-owasp.jsonl)
  --coverage FILE            OWASP coverage report (default: PATH/reports/owasp-coverage.md)
  --roe FILE                 ROE (default: PATH/roe.yaml)
  --summary-output FILE      Output path (default: PATH/reports/executive-summary.md)
  --output FILE              Operational findings output
  --format FMT               json | jsonl | markdown (default: markdown)
  --min-severity SEV         default info
  --priority-overrides FILE  YAML overriding the top-3 priorities
```

### Step 3 — Review the risk score

If the score is in 76-100 range, the operator should sanity-check
before delivering: did the underlying findings actually warrant
the elevated reading, or did a few INFO-tagged findings get
mis-categorized as HIGH?

### Step 4 — Hand off

The exec summary is intended as a standalone artifact. Deliver to
the customer's exec readout meeting, along with the full
vulnerability report.

## Examples

### Example 1 — End-of-engagement summary

```bash
python3 ./scripts/exec_summary.py engagements/acme-2026-q2/
```

### Example 2 — Board-ready summary (force-includes governance section)

```bash
python3 ./scripts/exec_summary.py engagements/acme-2026-q2/ \
    --summary-output engagements/acme-2026-q2/reports/board-summary.md
```

### Example 3 — Override priorities

```yaml
# priorities-override.yaml
- title: "Hardcoded AWS access key in source"
  effort: Hours
  impact: Material
  rationale: This is the single highest-priority remediation regardless of count.
```

```bash
python3 ./scripts/exec_summary.py engagements/acme-2026-q2/ \
    --priority-overrides priorities-override.yaml
```

## Output

JSON / JSONL / Markdown per `lib/report.py` for operational
findings. PRIMARY output: the executive-summary markdown
document.

Operational Finding includes:

- `id` — `exec::<issue>`
- `severity` — varies
- `category` — `executive-summary`
- `summary` — what was generated
- `evidence` — risk score, finding count, top priorities, output path

## Error Handling

- **No findings source** → CRITICAL operational finding, exits 1.
- **Source JSONL unparseable** → HIGH, exits 1.
- **No findings at all** → emits LOW operational finding noting
  the empty engagement; the document is generated but says so.
- **Coverage report missing** → MEDIUM, document is generated
  without the coverage-narrative section.
- **ROE missing** → MEDIUM, document is generated without the
  scope/authorization section.

## Resources

- `references/THEORY.md` — Executive-summary writing as a
  technical-communication discipline, single-number risk
  scoring tradeoffs, why deterministic priority selection beats
  human-curated for reproducibility, how the score interpretation
  bands were chosen, comparison with CVSS / DREAD / STRIDE risk
  models
- `references/PLAYBOOK.md` — Per-audience customizations (board,
  C-suite, security leadership, customer auditor), summary length
  guidelines, common rewrite patterns, integration with the
  composing + mapping skills, post-delivery follow-up cadence
