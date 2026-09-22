# Official Procore sources

Consulted: 2026-09-13

## Scope

These first-party sources ground **Procore Integration Health Observability**. Application-specific freshness and latency signals remain the operator's responsibility.

## Sources

- [Integration Health](https://developers.procore.com/documentation/integration-health)
- [API Call Activity Report](https://developers.procore.com/documentation/api-activity-export)
- [Rate limiting](https://developers.procore.com/documentation/rate-limiting)
- [Webhook reliability](https://developers.procore.com/documentation/webhooks)

## Provider boundaries

- Integration Health aggregates provider observations over documented windows.
- The API activity report covers production routes, methods, statuses, dates, and counts.
- Provider health does not replace application queue and reconciliation telemetry.
- Unknown activity can indicate a legacy deployment or credential problem.
- Source snapshot: `procore/documentation@fd31bc4b6c3d46b72b2b570c920ae5ccb2aa4318`.
