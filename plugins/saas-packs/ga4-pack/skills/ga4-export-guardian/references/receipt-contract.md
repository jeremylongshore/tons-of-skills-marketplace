# Export receipt contract

The input combines normalized table metadata with an optional raw BigQuery Job.
Keep original artifacts and a field-mapping receipt. The analyzer does not
authenticate the snapshot, its coverage, an export-start declaration or a SQL hash.

## Inventory fields

| Field | Contract |
| --- | --- |
| `property_id` | Numeric property ID as a string. |
| `dataset_id` | Native export dataset `analytics_<property_id>`. |
| `property_time_zone` | IANA reporting timezone. |
| `captured_at` | Timezone-aware ISO timestamp for the metadata collection. |
| `requested_window` | Inclusive `start_date` / `end_date`, at most 366 days. |
| `export_started_on` | Earliest relevant export date supported by configuration/history evidence. Not an inferred lifetime acquisition date. |
| `daily_settlement_days` | Operator investigation bound, integer 0–30 or `null`. Not a provider guarantee. |
| `snapshot_complete` | Explicit boolean. True requires evidence that the listing covers the relevant dataset/date scope without permission or pagination gaps. |
| `tables` | Metadata rows with `table_id`; optional `row_count` as a nonnegative int64 string and `last_modified_at` as an aware ISO timestamp. |

Recognized export names are `events_YYYYMMDD` and `events_intraday_YYYYMMDD`.
Other table names are counted as ignored, not interpreted as native export data.
Duplicate IDs and invalid date suffixes are held. Optional metadata may be `null`;
do not fabricate a row count or modification time to make the receipt complete.

## Optional query evidence

`dry_run_job` is the Job JSON for the exact intended SQL. The expected hash is
`expected_query_sha256`, computed from the exact UTF-8 SQL bytes without trimming
or normalizing. Whitespace changes therefore require a fresh binding.

The helper reads `configuration.dryRun`, `configuration.query` and
`statistics.query`, plus available `status`. It requires explicit Standard SQL,
a SELECT `statementType`, a successful completed status when present, no
persistent destination table, and `totalBytesProcessed` as a nonnegative int64
string. The optional configured `maximumBytesBilled` must be a positive int64
string. Estimate accuracy can be `PRECISE`, `UPPER_BOUND`, `LOWER_BOUND` or `UNKNOWN`.

The query hash ties this receipt to the supplied SQL; it does not prove dataset
affinity, exhaustive referenced-table coverage or a benign result payload.
Processed-byte estimates are not billable-byte estimates. Even a precise value
below the cap leaves minimum billing and rounding unverified.

## Runnable fixture

This synthetic fixture is not a real cloud collection. It intentionally uses a
small cap to demonstrate why a low processed-byte estimate is not billing approval.

```json
{
  "property_id": "123456789",
  "dataset_id": "analytics_123456789",
  "property_time_zone": "UTC",
  "captured_at": "2026-10-24T12:00:00Z",
  "export_started_on": "2026-10-01",
  "requested_window": {"start_date": "2026-10-20", "end_date": "2026-10-24"},
  "daily_settlement_days": 2,
  "snapshot_complete": true,
  "tables": [
    {"table_id": "events_20261020", "row_count": "120"},
    {"table_id": "events_intraday_20261024", "row_count": "80"}
  ],
  "expected_query_sha256": "eefb8187a0c4db5cf7ada09790c949de4a4dfabe215a95d40dbb048e852f0781",
  "dry_run_job": {
    "configuration": {
      "dryRun": true,
      "query": {
        "query": "SELECT COUNT(*) FROM `fixture.analytics_123456789.events_20261020`",
        "useLegacySql": false,
        "maximumBytesBilled": "2000"
      }
    },
    "statistics": {
      "query": {
        "statementType": "SELECT",
        "totalBytesProcessed": "1000",
        "totalBytesProcessedAccuracy": "PRECISE"
      }
    },
    "status": {"state": "DONE"}
  }
}
```

Expected observations: a daily table on October 20, an absent October 21 beyond
the operator's two-day bound, recent unobserved dates on October 22–23, provisional
intraday data on October 24, and `billing-verification-required` for the query.
No result claims confirmed data loss, successful export setup or a monetary charge.
