# Official Procore sources

Consulted: 2026-09-13

## Scope

These first-party sources ground **Procore Adapter CI Contract**. CI fixtures are repository-owned artifacts and must be reviewed when provider contracts change.

## Sources

- [Procore sandboxes](https://developers.procore.com/documentation/development-environments)
- [Error code reference](https://developers.procore.com/documentation/error-reference)
- [Pagination](https://developers.procore.com/documentation/pagination)
- [Rate limiting](https://developers.procore.com/documentation/rate-limiting)
- [API lifecycle](https://developers.procore.com/documentation/rest-api-lifecycle)

## Provider boundaries

- Developer Sandbox and production credentials and hosts remain separate.
- Endpoint versions, page limits, and error shapes are resource-specific.
- Rate reset and retry headers drive retry timing.
- Provider tests require cleanup because Developer Sandboxes do not provide a routine reset.
- Source snapshot: `procore/documentation@fd31bc4b6c3d46b72b2b570c920ae5ccb2aa4318`.
