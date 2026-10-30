---
name: langfuse-cost-forensics
description: |
  Audit Langfuse recorded-cost observations for missing usage, unavailable cost,
  cursor gaps and scope mismatches. Separate explicit zero from unknown and
  partial subtotals from complete retrieved sets. Use when reviewing this evidence. Trigger with "Langfuse spend looks
  wrong", "missing generation cost" or "does this first page prove our total?".
allowed-tools: Read, Bash(python3:*)
version: 2.0.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [langfuse, cost, usage, coverage, forensics]
compatibility: Python 3.10+ standard library; supplied native Observations API v2 pages. No credentials, price lookup or provider calls are required.
argument-hint: '[cost-receipt.json]'
---

# Langfuse Cost Forensics

## Overview

Explain the recorded cost supported by a supplied observation set and what
prevents a complete-set subtotal. Missing cost is not zero, a first page is not
a project total, and recorded USD cost is not a verified provider invoice.
This operator diagnoses evidence; it does not route models or promise savings.

## Prerequisites

- The disputed cost claim, reviewed project and exact absolute selection window.
- Native Observations API v2 pages with actual request selectors, usage fields,
  cursor metadata and collection times.
- The [receipt contract](references/receipt-contract.md) and Python 3.10+.
- Permission to inspect the private evidence. Offline analysis needs no
  authentication; separate reads require existing approved project access.

Use Metrics API v2 for project-wide aggregate questions. Do not manufacture an
aggregate by fetching only one observation page or issuing unbounded per-trace
requests. Preserve the source and selection behind any supplied aggregate.

## Instructions

### Step 1: Define the cost question

Identify whether the claim concerns a captured observation set, a project
aggregate, an inferred model price, an ingested cost or a provider invoice.
Record time window, project, filters, fields and capture times. Do not assume
the report and invoice measure the same population or accounting event.

### Step 2: Map native pages and coverage

Read the [contract](references/receipt-contract.md). Retain the initial query,
each opaque cursor and terminal omission. Usage fields must actually have been
requested. Keep missing values missing and preserve explicit numeric zero.

Check inclusive start/exclusive end, exact project binding, compound
trace/observation IDs, query stability and collection completion. The analyzer
does not replay arbitrary advanced filters or authenticate supplied declarations.
An open/future window or a missing page remains incomplete evidence.

### Step 3: Run the deterministic audit

```sh
python3 scripts/inspect-costs.py private-cost-receipt.json
```

Run from this skill's directory. The standard-library analyzer makes no network
requests and echoes no raw prompts, outputs, model names, trace IDs or cursors.
Inspect eligible generation/embedding rows separately from other observations.

Use `totalCost` as recorded; do not sum overlapping `costDetails` entries or
arbitrary token/audio/total usage components. Missing prices or usage do not
justify guessed rates, and negative adjustments need their own interpretation.

### Step 4: Interpret subtotals honestly

`known_rows_recorded_cost_usd` is a subtotal of known rows. The complete retrieved
set subtotal is withheld when evidence has gaps. Neither is a project-wide
invoice or a savings estimate. Model-group output is bounded and ordered by
hashed identity, not a ranking of the most expensive models.

Investigate unavailable costs, omitted usage fields, mismatched scope, cursor
gaps and pricing provenance independently. A stored cost can be ingested or
inferred; matching numbers alone do not establish invoice reconciliation.

### Step 5: Return the cost evidence ledger

For each discrepancy provide the finding code, private receipt pointer,
affected count, arithmetic limit and next check. Separate confirmed receipt
defects, observed recorded costs and hypotheses about provider pricing or
billing. Further collection must stay within approved read scope.

## Output

Return `langfuse-cost-report.json` with eligible/known/zero/missing coverage,
known-row subtotal, complete-set subtotal when supported, bounded model groups,
findings and source limitations. Name supplied-data mode and do not convert
unknown cost into zero or claim that static coverage proves complete tracing.

## Examples

- **One row has null cost and one has zero:** preserve unavailable versus
  explicit-zero categories; withhold a complete-set subtotal.
- **Cursor remains after page one:** report partial coverage rather than a
  monthly project total or a percentage of savings.
- **Usage components include input, output and total:** inspect their coverage
  without adding all three into a fabricated token count.
- **Stored cost differs from an invoice:** identify scope and ingested/inferred
  provenance gaps; do not invent a current model price to explain the difference.

## Error Handling

Exit 0 means reviewable retrieved-set evidence, exit 1 requires investigation,
and exit 2 holds malformed/unreadable/oversized input with a fixed code. Preserve
the result, correct capture defects and retain original evidence. Do not alter
cost observations, credentials or model routing as part of this analysis.

## Resources

- [Native receipt contract, numeric semantics and primary references](references/receipt-contract.md).
- [Metrics API](https://langfuse.com/docs/metrics/features/metrics-api): aggregate questions.
- [Evaluation specification](eval-spec.yaml): no paid or live evaluation is implied.
