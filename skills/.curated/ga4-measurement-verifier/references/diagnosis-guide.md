# Measurement diagnosis

| Evidence | Next check | Unsupported inference |
| --- | --- | --- |
| Expected event absent from complete receipt | Confirm property/stream, deployment window, collection request, consent and processing evidence | The application or GA4 is down. |
| Expected event absent from truncated receipt | Recollect a bounded complete report | The event count is zero. |
| Event observed before and after deployment | Isolate the post-deployment window and a controlled test where authorized | The new build caused the reported events. |
| Event name observed, parameters questioned | Inspect an approved redacted collection capture or DebugView | Every required parameter arrived with the correct value. |
| Purchase events observed | Reconcile transaction/revenue evidence through an appropriate reporting workflow | Event count multiplied by assumed average order value is measured revenue. |
| Data API historical and realtime numbers differ | Align the window and definitions; realtime has a different schema and coverage | One report is necessarily corrupt. |

## Collection and privacy

GA4 realtime reports are aggregates, not a complete event firehose. Avoid
collecting user identifiers, raw URLs or payloads when a name/count receipt is
sufficient. DebugView or browser collection evidence may contain personal data;
use the operator's approved handling and redact before sharing. Never submit
synthetic events to a real property merely to make a verification pass.

A successful collection call does not establish complete instrumentation.
Consent, filters, stream selection, blocked requests and delayed processing are
separate hypotheses. State the evidence needed to distinguish them instead of
guessing the most convenient explanation.

## Primary references

- [Realtime method and minute ranges](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runRealtimeReport): Standard/360 windows, overlap behavior, request/response contract and row coverage.
- [Realtime schema](https://developers.google.com/analytics/devguides/reporting/data/v1/realtime-api-schema): supported metrics and dimensions; user-scoped custom dimensions differ from arbitrary event parameters.
- [Create a realtime report](https://developers.google.com/analytics/devguides/reporting/data/v1/realtime-basics): request construction and response use.
- [Data API quotas](https://developers.google.com/analytics/devguides/reporting/data/v1/quotas): token/concurrency/server-error limits; no invented requests-per-day schedule.
- [Data freshness](https://support.google.com/analytics/answer/11198161?hl=en): typical processing intervals are not an SLA.
- [Verify collection setup](https://developers.google.com/analytics/devguides/collection/ga4/troubleshoot): collection and tagging diagnostics.
