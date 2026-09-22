# Official Canva sources

Consulted: 2026-09-13

## Scope

These first-party sources establish measured caching, pagination, and async-job polling.

## Sources

- [API requests and responses](https://www.canva.dev/docs/connect/api-requests-responses/)
- [Design export APIs](https://www.canva.dev/docs/connect/api-reference/exports/)
- [Latest OpenAPI contract](https://www.canva.dev/sources/connect/api/latest/api.yml)

## Boundary

Derive cache lifetime from the response contract and data policy rather than a fixed universal TTL.
