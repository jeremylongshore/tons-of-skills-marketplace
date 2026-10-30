---
name: ga4-report-forensics
description: |
  Investigate conflicting GA4 report numbers using request and response receipts.
  Compare windows, identities, filters and row coverage; distinguish sampling,
  thresholding and high-cardinality loss. Use when GA4 API and UI reports disagree
  or exported rows are missing. Trigger with "GA4 user counts differ", "missing
  GA4 rows" or "is this report sampled?".
allowed-tools: Read, Bash(python3:*)
version: 2.0.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [ga4, analytics, reporting, forensics, data-quality]
compatibility: Python 3.10+ and IANA timezone data; optional collection requires google-analytics-data and existing approved ADC.
argument-hint: '[receipt-pair.json]'
---

# GA4 Report Forensics

## Overview

Explain what two GA4 report receipts establish, why they may differ and which
next check would distinguish competing explanations. Produce a finding ledger
and reproducible row-level comparison. A valid request or matching total alone
does not prove correct collection.

This skill analyzes report evidence and can collect a bounded report using
existing approved access. It does not configure tracking, change a property or
create credentials. For a portfolio-wide
business narrative, use `web-analytics`; this workflow diagnoses the underlying
report evidence instead.

## Prerequisites

Read [access diagnostics](references/access-diagnostics.md) when property access
is uncertain, and [report definitions](references/report-definitions.md) when
translating DAU/MAU, page, source, cohort or funnel questions into evidence.

- The exact question and two reports that are claimed to disagree, with the
  property, absolute date window, timezone, metric/dimension definitions and
  filters recorded for each.
- Complete Data API pages, or a documented normalization of a UI export into the
  [receipt contract](references/receipt-contract.md). Record the collection time
  and original source alongside the receipt. Never invent missing settings.
- Python 3.10+ with IANA timezone data. The analyzer uses only the standard
  library and makes no network requests.
- Permission to inspect the supplied analytics. Keep credentials, user IDs,
  sensitive URLs and raw event payloads out of the diagnostic report.

If a report is missing and collection is authorized, follow the
[bounded collection guide](references/collection-guide.md). Otherwise inspect the
available evidence qualitatively and identify the missing receipt. Do not
fabricate a comparison report to make the analyzer run.

## Instructions

### 1. Establish the disputed claim

Write one precise question, such as: "Does the API's 30-day active-user count
match the UI report for the same property and identity?" Identify which values
are observations and which are expectations. Preserve the original artifacts;
normalize copies only, with a short field-mapping receipt.

Resolve relative dates into absolute dates in the property's timezone. Check
inclusive endpoints: a window from `29daysAgo` through `yesterday` contains 29
days, not 30. Do not sum daily active users to manufacture a monthly unique count.

### 2. Check comparability before arithmetic

Read the [receipt contract](references/receipt-contract.md) and map both reports.
Keep filters as structured objects; `{}` means explicitly unfiltered, not unknown.
Use `null` for an unknown reporting identity or currency. If filter state is
unknown, stop normalization and obtain it rather than substituting `{}`.

Compare property, dates, timezone, filters, reporting identity, currency, ordered
dimensions, ordered metrics and metric types. Different scopes or attribution
settings can invalidate a comparison even when the metric labels look similar.
Record those settings separately; the analyzer does not discover them for you.

UI/BigQuery/Data API results can use different identities, modeling and metric
definitions. Do not treat their disagreement as proof that any backend is wrong.
Consult the [investigation guide](references/investigation-guide.md) when the
comparison crosses those boundaries.

### 3. Run the deterministic comparison

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/analyze.py" receipt-pair.json > ga4-report-forensics.json
```

The input is bounded to 2 MiB. Analyze larger exports in an approved local data
workflow; do not truncate them and call the shortened result complete. The helper
requires explicit offsets and row counts, detects pagination gaps, changing
headers/counts and repeated dimension keys, and refuses invalid numeric values.

Dimension values are hashed in the emitted comparison rather than printed.
Metric names and numeric values remain present, so the output still needs the
same handling as the underlying business analytics. File redirection writes the
named output; select a new or approved destination to avoid overwriting a report.

### 4. Interpret the quality evidence

Keep these signals separate:

- `samplingMetadatas`: compare sampled events with the sampling space. Sampling
  metadata with equal counts does not indicate a sampled subset.
- `dataLossFromOtherRow`: high-cardinality aggregation into `(other)`. This is
  not the sampling flag and can apply even when filters hide the other row.
- `subjectToThresholding`: threshold-sensitive reporting applies; it does not
  alone establish that this particular result lost rows.
- Missing pages or metadata: incomplete evidence. Empty rows do not establish
  zero traffic, and a row limit is not proof of complete coverage.

The analyzer's `comparable` state means the supplied context and row coverage
permit arithmetic. It does not certify freshness, source authenticity, collection
coverage, consent settings or causal attribution. Check collection timestamps and
Google's current reporting expectations before deciding that data has settled.

### 5. Produce the finding ledger

For each material finding include its JSON evidence pointer, observed value or
hashed row key, impact, confidence and next discriminating check. Keep:

1. Confirmed context/coverage defects.
2. Observed numeric differences on comparable rows.
3. Unresolved hypotheses requiring more evidence.

Do not add row-level unique-user values or ratios into a grand total. Percentage
change from a zero baseline is undefined; report absolute movement instead. Rows
present on only one side are a coverage discrepancy, not automatically zero on
the other side. Prefer the smallest additional query or setting check that can
  resolve uncertainty. Additional collection must stay within the already-authorized
  property, window and read scope; ask when that scope is missing or unclear.

## Output

Return `ga4-report-forensics.json` and a short explanation containing the disputed
claim, evidence sources and collection times, comparability verdict, ranked
findings, unknowns and next checks. Name supplied-data mode explicitly. A result
such as "timezone mismatch confirmed; corrected-window comparison still needed"
is useful without inventing a root cause.

## Examples

- **API users differ from UI:** identity is unknown on one receipt. Return
  inconclusive with a request for the UI identity setting; do not compute a
  percentage on assumed-equivalent users.
- **API export has 10,000 of 26,000 rows:** report incomplete coverage and collect
  the remaining pages with stable ordering. Do not explain the missing 16,000 as
  sampled data without sampling evidence.
- **Other-row loss is true, sampling counts are equal:** report cardinality loss
  independently; avoid the old inference that the report is sampled.

## Error Handling

The helper exits 2 with a content-free `held` code for malformed input. Correct
the receipt or collect the missing evidence; do not edit observed values until
the code passes. A successful helper exit can still contain `inconclusive` or
`context-mismatch`; preserve that result in the report. It is not permission to
publish a clean bill of health.

Use [current primary guidance](references/investigation-guide.md) for unsupported
fields, changing metric definitions and report freshness. No universal 48-hour
settlement guarantee or quota-increase promise is part of this workflow.

## Resources

- [Receipt contract](references/receipt-contract.md): input mapping and a complete runnable example.
- [Investigation guide](references/investigation-guide.md): reporting semantics, source checks and primary documentation.
- [Evaluation specification](eval-spec.yaml): realistic success, failure and non-trigger cases; no evaluation run is implied by its presence.
