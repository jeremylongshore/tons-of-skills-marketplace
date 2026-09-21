# Official Procore sources

Consulted: 2026-09-13

## Scope

These first-party sources ground **Procore Measured Sync Performance**. Validate all page sizes and supported sync operations against the selected endpoint.

## Sources

- [API call sequencing](https://developers.procore.com/documentation/api-call-sequencing)
- [Pagination](https://developers.procore.com/documentation/pagination)
- [API usage guidelines](https://developers.procore.com/documentation/api-usage-guidelines)
- [Using Sync Actions](https://developers.procore.com/documentation/using-sync-actions)
- [Rate limiting](https://developers.procore.com/documentation/rate-limiting)

## Provider boundaries

- Page limits and pagination support vary by endpoint.
- Link relations provide navigation when pagination is supported.
- Webhooks improve freshness but reconciliation preserves completeness.
- Sync actions are available only for documented resources.
- Source snapshot: `procore/documentation@fd31bc4b6c3d46b72b2b570c920ae5ccb2aa4318`.
