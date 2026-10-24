# Report receipt contract

The analyzer accepts one JSON object with exactly `left` and `right`. Each side
has a `context` object and a nonempty `pages` array. This is a supplied-evidence
contract, not proof of a successful provider call.

## Context mapping

| Field | Meaning |
| --- | --- |
| `property_id` | Numeric GA4 property ID as a string; never a `G-...` measurement ID. |
| `start_date`, `end_date` | Inclusive absolute ISO dates, resolved in the property timezone. One date window per receipt. |
| `time_zone` | IANA name such as `America/Chicago`. If response metadata supplies a timezone, it must agree. |
| `filters` | Complete normalized filter contract, including dimension/metric filters, comparisons and relevant report segments. Use `{}` only when verified absent and `null` when unknown. Unknown filters prevent numeric comparison. Keep the same normalization on both sides. |
| `reporting_identity` | The recorded identity/mode relevant to the source report, or `null` when unknown. Do not infer a UI setting from the API response. |
| `currency` | Recorded currency, or `null` when unavailable. Monetary comparisons require a known currency. |

Record attribution settings, collection timestamps, normalization changes and
source/version outside the JSON if the source does not expose them as API fields.
The analyzer does not test those aspects. A human/assistant must withhold a claim
of full equivalence when they remain unknown.

## Page mapping

Each page has the request's `offset` and its `response`. Start at offset zero;
retain every page in order. The response uses the Data API's JSON field names:

- `dimensionHeaders`: ordered objects with `name`; empty for aggregate-only reports.
- `metricHeaders`: ordered objects with `name` and `type`.
- `rowCount`: total matching rows, not the current page's length.
- `rows`: ordered `dimensionValues` and `metricValues`, each holding string `value` fields.
- `metadata`: original response metadata, including quality fields, timezone and currency when present.

One full page is sufficient when its row count equals the total. The analyzer
compares matching dimension tuples across reports, never their incidental row
order. A duplicate tuple, gap, stalled page, changed row count or changed headers
prevents a complete comparison. A changing report can still evade those tests;
retain deterministic request ordering and collection times as additional evidence.

For a UI export, normalize only fields you can identify in its export and settings.
Do not manufacture API metadata. Missing quality metadata becomes an explicit
finding. Preserve a mapping from the normalized receipt to the original export.
The full input digest binds the normalized payload; it does not authenticate it.

## Complete example

This fixture describes two supplied aggregate reports. It makes no live-property
claim. Save it as `receipt-pair.json` and run the command in the skill.

```json
{
  "left": {
    "context": {
      "property_id": "123456789",
      "start_date": "2026-10-01",
      "end_date": "2026-10-07",
      "time_zone": "UTC",
      "filters": {},
      "reporting_identity": "device-based",
      "currency": "USD"
    },
    "pages": [{
      "offset": 0,
      "response": {
        "dimensionHeaders": [],
        "metricHeaders": [{"name": "activeUsers", "type": "TYPE_INTEGER"}],
        "rowCount": 1,
        "rows": [{"dimensionValues": [], "metricValues": [{"value": "100"}]}],
        "metadata": {"timeZone": "UTC", "currencyCode": "USD"}
      }
    }]
  },
  "right": {
    "context": {
      "property_id": "123456789",
      "start_date": "2026-10-01",
      "end_date": "2026-10-07",
      "time_zone": "UTC",
      "filters": {},
      "reporting_identity": "device-based",
      "currency": "USD"
    },
    "pages": [{
      "offset": 0,
      "response": {
        "dimensionHeaders": [],
        "metricHeaders": [{"name": "activeUsers", "type": "TYPE_INTEGER"}],
        "rowCount": 1,
        "rows": [{"dimensionValues": [], "metricValues": [{"value": "110"}]}],
        "metadata": {"timeZone": "UTC", "currencyCode": "USD"}
      }
    }]
  }
}
```

Expected: `comparison: comparable`, one `activeUsers` difference of `10`, and a
`10.0` percentage change. These observations do not establish why values differ.

## Data handling

The script reads at most 2 MiB and emits JSON to stdout. It does not contact a
provider, read credential stores or save a file itself. Its result omits raw
dimension values but includes metric names/values and a hash of the full input.
Business metrics can still be sensitive. Keep both original and normalized
receipts in an approved location; no upload or external delivery is authorized.
