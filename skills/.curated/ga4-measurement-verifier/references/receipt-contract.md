# Realtime receipt contract

The receipt binds caller-declared context to the raw request/response. It is not
independently authenticated provider evidence. Preserve the original HTTP artifact
or SDK response and the transformation receipt separately.

- `property_id`: numeric property ID as a string.
- `property_tier`: `standard` or `360`, established from account evidence.
- `request_started_at`, `response_received_at`: timezone-aware ISO timestamps.
- `deployment_at`: an ISO timestamp, or `null` when no deployment is being assessed.
- `clock_uncertainty_seconds`: the caller's documented nonnegative bound, or
  `null` when unknown. Zero is an explicit exact-clock assumption, not a default.
- `expected_events`: 1–100 distinct `{name, minimum_count}` objects. Minimums
  must be positive integers supplied for this observation.
- `request`: the HTTP path's `property` plus request-body fields.
- `response`: the original realtime JSON body, with `kind`, headers, rows and total `rowCount`.

The supported request has exactly `eventName` as its dimension and `eventCount` as
its metric. Filters and metric aggregation are unsupported; a filtered response
can hide the very event being investigated. Use one minute range. Omission means
`startMinutesAgo: 29, endMinutesAgo: 0`. Bounds are inclusive; Standard allows
0–29, 360 allows 0–59. A range's start must be at least its end.

Each returned event name must appear once. Row values are numeric strings, not
floating-point JSON numbers. `rowCount` is the total matching row count, so a
shorter `rows` array means incomplete coverage. Missing expected events are
inconclusive in that case. The analyzer never adds duplicate rows to hide a
range/aggregation mistake.

## Runnable fixture

This is synthetic supplied evidence, not a real property's output. Its zero clock
uncertainty is a fixture assumption; a real run must supply its own evidence.

```json
{
  "property_id": "123456789",
  "property_tier": "standard",
  "request_started_at": "2026-10-24T05:10:30Z",
  "response_received_at": "2026-10-24T05:10:31Z",
  "deployment_at": "2026-10-24T05:05:30Z",
  "clock_uncertainty_seconds": 0,
  "expected_events": [
    {"name": "sign_up", "minimum_count": 3},
    {"name": "purchase", "minimum_count": 1}
  ],
  "request": {
    "property": "properties/123456789",
    "dimensions": [{"name": "eventName"}],
    "metrics": [{"name": "eventCount"}],
    "minuteRanges": [{"startMinutesAgo": 4, "endMinutesAgo": 1}]
  },
  "response": {
    "kind": "analyticsData#runRealtimeReport",
    "dimensionHeaders": [{"name": "eventName"}],
    "metricHeaders": [{"name": "eventCount", "type": "TYPE_INTEGER"}],
    "rowCount": 1,
    "rows": [{
      "dimensionValues": [{"value": "sign_up"}],
      "metricValues": [{"value": "4"}]
    }]
  }
}
```

Expected: `sign_up` is observed with count 4; `purchase` is not observed in the
complete receipt, with an unknown count. The range is entirely after deployment
under the fixture's clock assumption. No field declares the deployment successful.

## Timing interpretation

The server executes between client request and response times only to the extent
the supplied clock bound is valid. The script rounds the earliest possible start
down and latest possible end up to server-minute boundaries, using that bound.
With an unknown bound it reports a client-clock frame and withholds deployment
attribution. Processing delay, source authentication and device clocks remain
outside this calculation. Keep collection time visible in any report presented
as current; the analyzer has no independent wall-clock freshness check.
