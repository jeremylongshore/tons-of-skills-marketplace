# Bounded export evidence collection

The optional `scripts/collect.py` uses existing approved Application Default
Credentials. It performs table metadata reads and, only when SQL is explicitly
supplied in the plan, a dry run. It does not execute a query for results, call
`job.result()`, create links, grant IAM or modify tables. The dependency is
`google-cloud-bigquery`, obtained through the approved local environment.
Without `--live`, it holds before importing the SDK or discovering credentials.

Provide this plan on stdin, replacing the fixture target with an authorized one:

```json
{
  "project_id": "fixture-project",
  "property_id": "123456789",
  "dataset_id": "analytics_123456789",
  "property_time_zone": "UTC",
  "requested_window": {"start_date": "2026-10-01", "end_date": "2026-10-02"},
  "export_started_on": "2026-10-01",
  "daily_settlement_days": null
}
```

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/collect.py" --live < export-plan.json > export-receipt.json
python3 "${CLAUDE_SKILL_DIR}/scripts/inspect-export.py" export-receipt.json > export-investigation.json
```

Resolve installed helper paths first. The output contains business metadata and,
when requested, SQL; redirect only to approved local paths. The script writes
only stdout. Read failure/collection states before interpreting the analysis.

Listing is limited to 1,000 table entries in pages of at most 100. Only native
export tables within the requested date window receive detailed metadata reads.
The collector records that scope; `snapshot_complete` does not claim a snapshot
of every table in the project. An additional entry is used solely to detect
listing truncation. Metadata/permission/pagination/deadline gaps set completeness
false and preserve available observations without inventing zero rows.

The collection deadline is 60 seconds, with per-request timeouts no greater than
20 seconds and automatic retries disabled. A listing page is not started when
less than its fixed 20-second timeout remains. Credential setup precedes this
deadline. The output limit is 2 MiB. Cloud changes during collection remain a
source of uncertainty even after a listing completes.

To request a dry run, add exact `sql` text (at most 64 KiB) and a positive integer
`maximum_bytes_billed`. Metadata-only collection requests the BigQuery read-only
OAuth scope. Dry runs request the BigQuery scope and need existing `jobs.create`
authority plus relevant dataset access; no permissions are granted automatically.
Dataset location, permissions or unsupported SQL can cause a held dry run. Keep
that result held and resolve the missing evidence rather than running the query.

The SDK request explicitly sets `dry_run=True`, Standard SQL, no query cache and
the supplied byte cap, with request/job retries disabled. The SQL hash binds the
exact UTF-8 text. The receipt labels its normalization: configuration comes from
`QueryJob.to_api_repr()`, while statistics/status come from public SDK properties
because that serializer omits server result statistics. Estimate accuracy remains
unknown when the SDK does not expose it. Do not invent precision.

A dry-run collection failure remains `held-collection` in the diagnostic output.
A successful dry run still does not approve real execution or a monetary budget:
processed bytes do not establish billed bytes, minimum billing or rounding.

Development checks use synthetic transports and actual SDK model objects. They
do not contact a cloud project, discover ADC or demonstrate live permissions.

Primary sources: [BigQuery dry runs](https://cloud.google.com/bigquery/docs/running-queries#dry-run-query),
[BigQuery Job resource](https://cloud.google.com/bigquery/docs/reference/rest/v2/Job).
