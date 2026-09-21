# Official Procore sources

Consulted: 2026-09-13

## Scope

These first-party sources ground **Procore Contract-Preserving REST Client**. Confirm every resource route and version in the live API reference.

## Sources

- [REST API overview](https://developers.procore.com/documentation/rest-api-overview)
- [Request and response formats](https://developers.procore.com/documentation/payload-formats)
- [Pagination](https://developers.procore.com/documentation/pagination)
- [Rate limiting](https://developers.procore.com/documentation/rate-limiting)
- [Error code reference](https://developers.procore.com/documentation/error-reference)

## Provider boundaries

- API versions are endpoint-specific, not one pack-wide constant.
- Pagination support and limits vary by endpoint.
- Rate and retry headers must remain visible to scheduling logic.
- Only routes present in the public API reference are supported.
- Source snapshot: `procore/documentation@fd31bc4b6c3d46b72b2b570c920ae5ccb2aa4318`.
