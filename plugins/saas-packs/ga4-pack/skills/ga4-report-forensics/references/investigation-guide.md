# Investigating GA4 disagreements

## Choose a discriminating check

| Observation | Check next | Do not conclude |
| --- | --- | --- |
| API and UI user counts differ | Property, inclusive dates, timezone, identity/modeling, filters, attribution and metric definition | The larger number is more accurate. |
| Per-day users sum above a window total | Whether users are deduplicated across the window | The window report lost events. |
| `dataLossFromOtherRow` is true | Dimensional cardinality and `(other)` aggregation | The response was sampled. |
| Sampling counts differ | Sample fraction, query bounds and supported sampling options | A sampled count is an exact count. |
| Thresholding applies | Threshold-sensitive dimensions and the report's quality evidence | This flag proves a particular missing row. |
| Empty or incomplete rows | Access, property, date window, pagination, collection and metadata | No people visited the site. |
| Recent numbers change | Collection time and current freshness/processing guidance | Everything becomes immutable after 48 hours. |
| Weekly active users change | Population, periods, collection and segmentation | A retention rate or cohort return was measured. |

GA4 requests use inclusive date endpoints. Relative dates are resolved in the
reporting timezone. A week ending yesterday starts `7daysAgo`; a 30-day completed
window starts `30daysAgo`. Use absolute resolved dates in comparison receipts.

## Definitions that affect the investigation

`activeUsers`, `totalUsers`, sessions and event counts measure different things.
Do not substitute them because they seem close. User counts are generally not
additive across dates or dimensions. Ratios require their own numerator and
denominator; neither summing nor averaging row percentages generally recreates
the aggregate.

GA4 supports cohort reports through the Data API. Use a supported cohort request
when its definitions fit the question. Querying weekly active users does not
identify returning members of an acquisition cohort. Ordered funnels likewise
need sequence-aware analysis; dividing independent event totals is not a funnel.

BigQuery export gives event-level evidence with its own identity, collection,
late-arrival and export-limit boundaries. It is neither a universal replacement
for reporting semantics nor automatic proof that a UI count is wrong. Escalate to
export investigation when event-level evidence is actually needed.

## Current primary sources

- [Reporting expectations](https://developers.google.com/analytics/devguides/reporting/data/v1/reporting-data-expectations): quality metadata, sampling and `(other)`.
- [RunReport response](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/RunReportResponse): rows, headers, row count and metadata.
- [RunReport request](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport): pagination, ordering, comparisons and request fields.
- [DateRange](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/DateRange): inclusive ranges and property-timezone relative dates.
- [Advanced reports](https://developers.google.com/analytics/devguides/reporting/data/v1/advanced): cohorts, custom dimensions and metrics.
- [API schema](https://developers.google.com/analytics/devguides/reporting/data/v1/api-schema): metric and dimension definitions.
- [Quotas](https://developers.google.com/analytics/devguides/reporting/data/v1/quotas): tokens, concurrent requests and quota response evidence.
- [Data freshness](https://support.google.com/analytics/answer/11198161): processing intervals and reporting limits.

Check these sources when the supplied report uses fields or behavior outside the
contract. Do not copy a stale exhaustive metric list into the skill.
