# Export and scan-risk investigation

| Evidence | Discriminating next check | Do not infer |
| --- | --- | --- |
| Table absent from an incomplete listing | Verify listing scope, access and pagination | The export failed. |
| Table absent beyond the operator's bound | Inspect export link, frequency, limits, processing and source collection evidence | Events are permanently lost. |
| Intraday exists without daily | Check configured export mode, date and current export status | Intraday is a finalized replacement with identical completeness. |
| Both sources exist | Select an explicit daily/intraday policy and inspect their actual coverage | Their row counts can be added. |
| Table predates declared export start | Check copied/backfilled data, source lineage and configuration history | The supplied start date or table is automatically authoritative. |
| Old daily data changes | Inspect late arrivals or reprocessing evidence | Historical daily tables become universally immutable after 72 hours. |
| Dry-run estimate is large | Check date/table selection, columns, joins and scan plan; retain a byte cap | A row LIMIT makes the scan cheap. |
| Processed estimate is below the cap | Check billable-byte rules and the actual billing model | The query is approved or will cost that exact number of bytes. |

## Query and identity limits

GA4 event exports contain event rows. A `user_pseudo_id` is not an authenticated
person or a universal cross-device identity. A first-observed date in a bounded
query is not automatically the user's lifetime acquisition date. Missing IDs and
consent-dependent collection can change session and cohort populations.

For custom cohort SQL, record the acquisition lookback, observation horizon,
property timezone, identity, eligible population and right-censoring policy.
Session keys must include the relevant user identity with `ga_session_id`; the
session number alone is not globally unique. Keep such analysis separate from
this metadata ledger rather than claiming the ledger validates arbitrary SQL.

Wildcard suffix ranges that include only eight-digit dates do not automatically
include `intraday_YYYYMMDD` suffixes. Design daily/intraday selection explicitly.
Do not blindly UNION both and assume the provider deduplicates the result.

## Billing boundary

On-demand query charges include per-table/per-query minimums and rounding. A dry
run's `totalBytesProcessed` therefore cannot be treated as an exact future bill.
Capacity pricing, storage, streaming, external services, regional pricing and
allowances introduce other boundaries. This helper intentionally does not quote
a dollar rate or produce an execution approval.

For a suspected expensive query, retain the intended SQL hash, actual dry-run
configuration, estimate accuracy and the proposed `maximumBytesBilled`. Diagnose
the scan, then obtain any missing execution scope before running a real query.

## Primary references

- [GA4 export schema](https://support.google.com/analytics/answer/7029846): daily/intraday tables, event fields and updates.
- [GA4 BigQuery Export](https://support.google.com/analytics/answer/9358801): export modes, limits and differences from reporting.
- [BigQuery versus GA4 UI](https://developers.google.com/analytics/blog/2023/bigquery-vs-ui): identity, processing and aggregation differences.
- [Dry runs](https://docs.cloud.google.com/bigquery/docs/running-queries): query estimation without execution.
- [Job resource](https://docs.cloud.google.com/bigquery/docs/reference/rest/v2/Job): configuration, statement type, statistics and estimate accuracy.
- [Cost controls](https://docs.cloud.google.com/bigquery/docs/best-practices-costs): scan reduction and maximum billed bytes.
- [BigQuery pricing](https://cloud.google.com/bigquery/pricing): current billing model, minimums and rounding; check the actual project/region before monetary analysis.
