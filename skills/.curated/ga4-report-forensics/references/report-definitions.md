# Report definitions retained from the common-report tutorials

Choose the question and denominator before selecting metrics. Keep the property,
inclusive dates, timezone, identity, dimension scopes, filters and attribution
settings with the result. Use the current API schema/metadata for the property;
custom field registration and compatible combinations are not universal.

| Question | Evidence and interpretation |
| --- | --- |
| Daily versus monthly active users | Request `activeUsers` for the intended window. Add `date` only for a daily series. A sum of daily active users is not the window's unique active-user count. Define whether “monthly” means a calendar month or a rolling interval. |
| Top pages | Use a supported page dimension such as `pagePath` with a compatible metric such as `screenPageViews`. A page-view ranking is not a unique-person ranking or a conversion attribution report. Record hostname/query-string handling and paginate before claiming complete coverage. |
| Acquisition sources | State whether the question concerns first-user or session acquisition and choose compatible dimensions accordingly. Do not compare `firstUserSource` with `sessionSource` as though they have the same scope. Record attribution/identity settings independently of a response's metric names. |
| Retention | Define the acquisition cohort, cohort date range, return event/activity, period granularity, denominator and incomplete observation periods. The Data API supports cohort reports; BigQuery is not a universal prerequisite. Independent weekly user totals are not a retention calculation. |
| Funnel | Define identity, ordered steps, timestamps, timeouts and deduplication. Independent event totals or realtime counts do not establish an ordered funnel. Obtain suitable event-level or supported funnel evidence before claiming completion rates. |

## Exact windows

Resolve relative dates in the property's reporting timezone, retain absolute
dates in the receipt and include both endpoints. October 1 through October 30
contains 30 dates. `29daysAgo` through `yesterday` contains 29 dates;
`30daysAgo` through `yesterday` contains 30. Neither automatically means the last
30 complete 24-hour periods across daylight-saving transitions.

For a rolling 30-date active-user total, a named-metric request can omit
dimensions and use `activeUsers`; for the daily series, add `date`. Collect them
as separate questions. Their shapes differ deliberately and should not be
forced into a row-for-row comparison or summed into a unique-person total.

## Ratios and cohort evidence

Keep numerator and denominator with every rate. A zero denominator yields an
undefined rate, not infinity or a fabricated zero. State whether the numerator
is users, sessions or events, whether periods have fully elapsed and whether
the export window can observe the original acquisition date. First appearance
inside a bounded extract is not proof of lifetime acquisition.

For native Data API cohorts, inspect the primary cohort request contract and
retain `cohortSpec` in the normalized filter/segment contract. The bundled
historical collector deliberately holds cohort and calculated-expression
requests; collect those receipts through an existing approved client and label
the mapping. Do not silently convert a cohort request to ordinary weekly users.

## Quality and completeness

Sampling metadata, high-cardinality `dataLossFromOtherRow`, thresholding and
pagination are different evidence. Check them separately. Reconcile UI/API
differences with their actual identity, freshness, attribution and scope before
claiming an implementation defect. A green HTTP response is not a completeness
certificate.

Primary sources: [API schema](https://developers.google.com/analytics/devguides/reporting/data/v1/api-schema),
[advanced reports and cohorts](https://developers.google.com/analytics/devguides/reporting/data/v1/advanced),
[reporting data expectations](https://developers.google.com/analytics/devguides/reporting/data/v1/reporting-data-expectations).
