# Official Procore sources

Consulted: 2026-09-13

## Scope

These first-party sources ground **Procore Header-Driven Rate Controller**. Runtime response headers remain the source of truth for the active window.

## Sources

- [Rate limiting](https://developers.procore.com/documentation/rate-limiting)
- [API Call Activity Report](https://developers.procore.com/documentation/api-activity-export)
- [Error code reference](https://developers.procore.com/documentation/error-reference)
- [Webhook reliability](https://developers.procore.com/documentation/webhooks)

## Provider boundaries

- Procore applies a spike window and an hourly window.
- Returned rate headers describe the window most likely to be exceeded first.
- Failed requests consume budget.
- A 429 uses the rate reset signal; a heavy-load 503 uses `Retry-After`.
- Source snapshot: `procore/documentation@fd31bc4b6c3d46b72b2b570c920ae5ccb2aa4318`.
