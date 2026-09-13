# Official Procore sources

Consulted: 2026-09-13

## Scope

These first-party sources ground **Procore API Call Budget Recovery**. They do not establish a universal provider per-call price.

## Sources

- [API Call Activity Report](https://developers.procore.com/documentation/api-activity-export)
- [Rate limiting](https://developers.procore.com/documentation/rate-limiting)
- [API usage guidelines](https://developers.procore.com/documentation/api-usage-guidelines)
- [Webhook reliability](https://developers.procore.com/documentation/webhooks)

## Provider boundaries

- Failed calls count against the request limit.
- The activity report exposes normalized route, method, status, date, and count.
- Webhooks are best-effort notifications and need reconciliation.
- Monetary savings require operator telemetry or an authoritative commercial agreement.
- Source snapshot: `procore/documentation@fd31bc4b6c3d46b72b2b570c920ae5ccb2aa4318`.
