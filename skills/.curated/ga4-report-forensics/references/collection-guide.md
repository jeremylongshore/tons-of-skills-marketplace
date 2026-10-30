# Bounded Data API collection

Use `scripts/collect.py` only for an approved target property and observation.
It reads existing Application Default Credentials with the Analytics read-only
scope. It does not create credentials, modify IAM, configure tracking or change
the property. The optional dependency is `google-analytics-data`; use an approved
local environment. Without `--live`, it holds before SDK import or ADC lookup.

Save an observation plan with the numeric property ID, inclusive absolute dates
(at most 366 days), timezone, known identity/currency or explicit nulls, and a
named-dimension/metric request. For example:

```json
{
  "context": {
    "property_id": "123456789",
    "start_date": "2026-10-01",
    "end_date": "2026-10-07",
    "time_zone": "UTC",
    "reporting_identity": null,
    "currency": null
  },
  "request": {
    "dimensions": [{"name": "country"}],
    "metrics": [{"name": "activeUsers"}]
  }
}
```

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/collect.py" --live < report-plan.json > collected-report.json
```

Resolve the installed helper path before execution. Choose an approved output
path: receipts contain raw dimension values and business metrics. The collector
prints JSON only and never writes a file itself. It does not upload the result.

The request accepts named dimensions/metrics, `dimensionFilter`, `metricFilter`
and `keepEmptyRows`. Property, dates, currency, paging and stable dimension
ordering are derived from the plan. Cohorts, pivots, comparisons, multiple date
ranges and calculated field expressions are outside this collector's contract;
obtain their receipts separately rather than silently removing those clauses.

Each request has a maximum 20-second RPC timeout with automatic retries disabled.
The collection loop stops after 60 seconds, 10 pages or 10,000 rows. Credential
setup occurs before that collection deadline and can take additional time.
The byte limit can hold an oversized receipt. Provider failures hold collection
with a content-free error; no successful receipt is claimed. The client transport
is closed on completion or failure.

Page offsets, raw response fields, collection times, a request digest and any
protobuf row-count default normalization are recorded. Metric types serialize
as enum names. A page/time limit returns an explicitly partial receipt when at
least one valid page exists; running the analyzer still checks row coverage,
header/count drift and duplicate tuples. Even `row-count-reached` is not proof
that the source stayed unchanged while paginating.

The output is one side of a comparison. Combine two genuine observations as
`{"left": <first receipt>, "right": <second receipt>}` for `analyze.py`. The
collector derives `context.filters.data_api_report` from effective request
semantics, including dimension and metric definitions. A UI export must have an
evidenced equivalent mapping before claiming matching filter contracts. Unknown
identity remains unknown; a successful SDK call does not expose UI settings or
prove report equivalence. Review attribution and freshness separately.

Offline tests exercise pagination, budget exhaustion, deadline handling and
actual SDK request parsing with synthetic responses. They do not prove live
account access or successful collection from any property.

Primary contract: [Google Data API runReport](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport).
