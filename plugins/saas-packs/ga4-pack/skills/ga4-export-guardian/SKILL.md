---
name: ga4-export-guardian
description: |
  Investigate GA4 BigQuery export gaps, daily/intraday overlap and query scan risk
  from table-inventory and dry-run receipts. Use when exported days appear missing
  or a GA4 query may scan too much. Trigger with "missing GA4 BigQuery tables",
  "GA4 export delayed" or "check this GA4 query's scan budget".
allowed-tools: Read, Bash(python3:*)
version: 2.0.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [ga4, bigquery, export, data-quality, cost]
compatibility: Python 3.10+ and IANA timezone data; optional collection requires google-cloud-bigquery and existing approved ADC.
argument-hint: '[export-receipt.json]'
---

# GA4 Export Guardian

## Overview

Build a date-by-date ledger of observed GA4 export tables and inspect a
query-bound BigQuery dry-run estimate. Separate missing evidence, provisional
intraday data and operator assumptions from confirmed observations.

This is an investigation workflow, not an export installer or an autonomous query
runner. It does not create links, grant IAM, modify tables or execute paid queries.

## Prerequisites

- The numeric GA4 property ID, export dataset, property timezone and evidence for
  when the relevant export began.
- A dated table metadata snapshot covering the requested dates. Establish its
  listing scope, pagination and access limits before marking it complete.
- Optionally, a completed successful BigQuery dry-run Job resource and the exact
  SHA-256 of the SQL being assessed. Retain the configured `maximumBytesBilled`.
- Python 3.10+ and IANA timezone data. The analyzer uses only the standard library;
  optional SDK collection is described in the [collection guide](references/collection-guide.md).

Use existing authorized metadata access when available. Dataset-level access may
be sufficient; do not grant project-wide roles or generate keys to make an
inspection succeed. If evidence is supplied, label supplied-data mode rather
than pretending to have inspected a cloud project.

## Instructions

### Step 1: Bound the disputed period

Record the target property/dataset, requested dates and collection time. Resolve
the snapshot's current date in the property's timezone, not the analyst's laptop
timezone. A date before the declared export start or after the snapshot cannot be
treated as an ordinary missing historical export.

An operator may supply a daily settlement bound in days. It is a local
investigation assumption, not a Google SLA. Use `null` when no bound has been
established. Presence of an old daily table still does not prove it is complete
or immutable: late arrivals and reprocessing can change historical data.

### Step 2: Preserve an inventory receipt

Use Read to inspect the original table-list/dry-run artifacts and their collection
receipt before normalizing them. A supplied completeness flag is not independent
evidence that the underlying listing covered the requested dataset and dates.

Map existing metadata into the [receipt contract](references/receipt-contract.md).
The standard export dataset is `analytics_<property_id>`. If the data was copied
or transformed elsewhere, document that lineage and investigate the copy through
its own contract rather than relabeling it as the native export.

Keep `snapshot_complete` false when permissions, listing filters or pagination
leave coverage uncertain. Optional row counts and modification times are metadata
observations; they do not prove event delivery. Never query all event rows merely
to construct an inventory when existing metadata can answer the question.

### Step 3: Run the local inspection

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/inspect-export.py" export-receipt.json > ga4-export-investigation.json
```

The helper accepts up to 2 MiB and a requested window of at most 366 days. It
checks dataset/property binding, dates, duplicate table IDs and optional dry-run
structure. It emits a timeline, explicit unknowns and query-estimate findings;
it performs no provider operation. Select a new or approved local output path.

### Step 4: Interpret table evidence without double counting

`events_YYYYMMDD` and `events_intraday_YYYYMMDD` can coexist. The ledger selects one
source per day, preferring daily when present, and never adds their row counts.
That policy avoids an obvious overlap; it is not a deduplication or completeness
certificate. Review the [export diagnosis guide](references/diagnosis-guide.md)
before designing a query that combines daily and intraday data.

Missing days beyond an operator bound deserve investigation, not an invented
data-loss verdict. Check export-link/configuration evidence, listing scope,
permissions, applicable limits and provider processing status. A visible table
before the declared start or in the future is a context inconsistency to resolve.

### Step 5: Inspect query risk using the actual dry run

For query assessment, retain the raw Job resource and hash the exact intended
SQL. The helper requires matching SQL, `dryRun: true`, Standard SQL, a SELECT
statement and successful available job status. It refuses a persistent destination
table or a mutating statement. It does not parse SQL with a regex and claim to
have proved a bounded scan.

`totalBytesProcessed` is an estimate. A missing cap or weak estimate bound remains
inconclusive. An estimate above the configured byte cap is an explicit risk.
Even a smaller estimate does not certify billable bytes: on-demand minimums and
rounding can matter, while capacity pricing and other charges follow different
rules. The helper therefore returns `billing-verification-required`, never an
automatic permission to execute.

Keep an approved `maximumBytesBilled` in any separately authorized execution.
Do not replace it with a SQL row `LIMIT`; limiting output rows does not generally
bound scanned bytes. Do not quote a universal per-TB price or assume the free
allowance is available. Use current pricing and the project's actual billing
model when monetary analysis is explicitly requested.

## Output

Return `ga4-export-investigation.json` and a short diagnosis containing:

1. Property/dataset identity, dates, timezone, capture time and inventory coverage.
2. Observed daily/intraday sources, provisional days, missing observations and
   any export-start or snapshot inconsistencies.
3. The exact query fingerprint, estimated processed bytes, accuracy, configured
   cap and remaining billing-verification requirements, when supplied.
4. Evidence-linked next checks and explicit hypotheses. Never describe an
   observed table as proof of complete tracking or a dry run as a paid query.

Treat the artifacts as business analytics. The helper emits metadata and counts,
not event payloads or SQL text, but the result can still be sensitive.

## Examples

- Daily and intraday tables exist for one date: select one source for reporting;
  do not add counts and call the sum daily traffic.
- A day is absent from a partial metadata listing: return inconclusive inventory
  coverage; do not diagnose export failure.
- A dry run estimates 1000 processed bytes against a 2000-byte cap: preserve the
  estimate and require billing verification. Minimum billing can exceed that cap;
  this is not a green execution verdict.

## Error Handling

Malformed receipts, contradictory dataset identity, failed/incomplete dry runs,
SQL fingerprint mismatches and unsupported mutation plans exit 2 with a
content-free `held` code. Preserve the original evidence. Correct the receipt
mapping or recollect an authorized snapshot instead of editing observations.
If optional query evidence is invalid, an explicitly inventory-only rerun may
still be useful; retain and disclose the unresolved query failure.

## Resources

- [Receipt contract](references/receipt-contract.md): field mapping and runnable inventory/query fixture.
- [Diagnosis guide](references/diagnosis-guide.md): export gaps, billing boundaries and primary sources.
- [Evaluation specification](eval-spec.yaml): expected investigation behavior; no model evaluation run is implied.
