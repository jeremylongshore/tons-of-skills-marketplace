# GA4 pack: retain the capability, replace the tutorial portfolio

**Date:** 2026-10-24

**Bead:** claude-l99e.10

**Status:** implementation direction; release remains subject to normal review and gates

## Decision

Keep a GA4 pack, but rebuild around operational investigations. Do not spend a
release merely adding headings or raising static grades on the five tutorials.
GA4 property reporting, event-delivery evidence and BigQuery export diagnostics
are distinct from the cross-site narrative and delivery work in `web-analytics`.
The useful capability merits investment; the current five-slot taxonomy does not.

This is a product judgment based on capability and defects, not demonstrated
adoption. No install telemetry, customer interviews or usage study was collected.
Do not describe the judgment as proof of market demand.

## Evidence boundary

Freshie is the grade authority. The authoritative runtime's run 138 records:

| Existing skill | Score | Grade | Errors | Warnings |
| --- | ---: | --- | ---: | ---: |
| `ga4-bigquery-export` | 77 | C | 0 | 8 |
| `ga4-common-reports` | 78 | C | 0 | 9 |
| `ga4-data-api-query` | 80 | B | 0 | 11 |
| `ga4-realtime-api` | 80 | B | 0 | 14 |
| `ga4-auth-setup` | 86 | B | 0 | 9 |

These are five non-stub source skills. The run's discovery source is `bc17de522`;
the compliance records were refreshed on 2026-10-23. The GA4 source tree is
unchanged between that source and marketplace main
`dd9cf1c487edb19fe504463b9aadf73afb6c05a4`. Grades identify a review queue;
they do not establish correctness, demand or the value of preserving each slot.

Read all five skills, the pack README and the `web-analytics` operating contract.
The Databricks comparison is its tracked `007-AT-ADEC-databricks-v2-cto-decision.md`,
current README, and `databricks-cost-leak-hunter` workflow and evaluation spec.
Its useful pattern is a distinct operator problem, actual evidence, deterministic
computation and an actionable report with explicit limits. Its historical live
execution claims are not inherited by GA4.

## Post-rebuild Freshie receipt

The baseline table above describes the retired v1 skills. The replacement
portfolio was discovered and graded in run **139** from source commit
`a338bab4ea70729b98f937f04eba5267adb266c5`, then published at Dolt commit
`mf70vsi6nk1tt23alrbujmq4jungnk7a`, tag `run-139`.

| Replacement | Freshie score | Grade | Errors |
| --- | ---: | --- | ---: |
| `ga4-report-forensics` | 92 | A | 0 |
| `ga4-measurement-verifier` | 95 | A | 0 |
| `ga4-export-guardian` | 97 | A | 0 |

These are published Freshie compliance grades, not behavioral model-evaluation
or live-provider certification. The [validation record](002-RA-AUDT-v2-validation-evidence.md)
separates native publication, local execution evidence and remaining limits.
Run 138 and its five GA4 records remain in historical inventory; run 139 carries
three successors. No prior score or history was rewritten.

## Per-skill disposition

| Existing slot | Disposition | Coverage to preserve |
| --- | --- | --- |
| `ga4-auth-setup` | Retire the standalone tutorial after migration | Property identity, access checks and credential guidance become prerequisites and a referenced access diagnostic. No automatic key creation. |
| `ga4-data-api-query` | Replace with reporting investigation | Request/response receipts, row coverage, dimensions/scopes, timezone, metadata, and comparison limits. |
| `ga4-common-reports` | Consolidate into reporting references | Correct report recipes, exact windows, non-additive users, denominators, cohort and funnel definitions. Generic recipes do not earn a separate slot. |
| `ga4-realtime-api` | Replace with measurement-signal verification | Check observed events against an expected event contract, freshness and collection coverage. Absence of a row is not proof of an outage. |
| `ga4-bigquery-export` | Replace with export investigation | Missing/late partitions, daily/intraday selection, supported identity and session semantics, and bounded query-cost evidence. |

## Three candidate operator outcomes

1. **Reporting forensics:** explain why two GA4 numbers differ. Produce a
   finding ledger tied to request/response fields, classify observed mismatches
   separately from hypotheses, and identify the next discriminating check.
2. **Measurement verification:** evaluate supplied or explicitly collected
   realtime observations against named expected events and windows. Produce
   observed, not observed and inconclusive results with evidence coverage.
3. **Export guardian:** inspect export/table and query-plan evidence. Produce a
   freshness/coverage ledger and bounded scan-cost assessment, separating
   configured export behavior, observed table state and missing evidence.

Each needs a deterministic analyzer, meaningful offline fixtures, primary-source
references, a named output artifact and realistic evaluation cases. A skill that
cannot meet those requirements is dropped or folded into another workflow.
Three is a bounded candidate portfolio, not a quota to fill.

Collection uses existing approved SDK/CLI access when available. Supplied-data
mode must be labeled and must not pretend to have inspected a property. No new
custom MCP server is justified by this decision. Building the pack does not
authorize live analytics queries, export changes, IAM changes or paid execution.

## Demonstrated content defects

- `dataLossFromOtherRow` identifies high-cardinality aggregation loss; it is not
  the sampling indicator. Inspect `samplingMetadatas` separately. The current
  query and common-report skills conflate them.
- The Data API supports cohort reports. The current recipes incorrectly make
  BigQuery a universal prerequisite for cohort retention. Counting weekly users
  is not a cohort-return calculation, and independent event totals are not an
  ordered funnel.
- Realtime quota guidance must follow token and concurrency limits, not the
  current arbitrary requests-per-day list. Realtime dimensions and metric
  availability need the current schema, not an asserted exhaustive table.
- Key-first authentication and the suggestion to rename a plaintext key to a
  `.sops` filename are not an acceptable credential workflow. Prefer supported
  keyless credentials; file renaming is not encryption.
- Export billing, late updates, permissions and daily/intraday selection need
  explicit evidence. A row limit does not bound bytes scanned. A bounded
  first-observed window does not prove lifetime acquisition or complete retention.
- Report windows, zero denominators and first-page processing require executable
  checks. A successful API request is not proof of complete or comparable data.

## Release and retirement requirements

Keep the `ga4-pack` install identity. Before replacing any installed skill, ship
the reviewed successor, a complete README migration map, permanent public skill
URL redirects, an appropriate breaking-change version, and an exact Git restore
receipt. Do not leave dead installable tombstones to inflate counts. Regenerate
curated/catalog projections from source; do not edit generated copies directly.
No retirement or v2 runtime is shipped by this decision document alone.

## Primary references

- [Reporting data expectations](https://developers.google.com/analytics/devguides/reporting/data/v1/reporting-data-expectations): sampling, aggregation loss and thresholds.
- [Advanced Data API use cases](https://developers.google.com/analytics/devguides/reporting/data/v1/advanced): cohort reports and custom definitions.
- [Realtime schema](https://developers.google.com/analytics/devguides/reporting/data/v1/realtime-api-schema): supported realtime fields.
- [Data API quotas](https://developers.google.com/analytics/devguides/reporting/data/v1/quotas): quota categories and consumption.
- [BigQuery Export](https://support.google.com/analytics/answer/9358801): export limits and cost boundaries.
- [Service-account key practices](https://docs.cloud.google.com/iam/docs/best-practices-for-managing-service-account-keys): avoid user-managed keys where supported alternatives exist.
