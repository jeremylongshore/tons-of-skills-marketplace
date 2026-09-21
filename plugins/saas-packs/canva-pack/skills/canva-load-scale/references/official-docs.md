# Official Canva sources

Consulted: 2026-09-13

## Scope

These first-party sources establish bounded load testing and worker capacity planning.

## Sources

- [API requests and responses](https://www.canva.dev/docs/connect/api-requests-responses/)
- [Latest OpenAPI contract](https://www.canva.dev/sources/connect/api/latest/api.yml)
- [Connect API security](https://www.canva.dev/docs/connect/guidelines/security/)

## Boundary

Never load-test Canva production endpoints without explicit authorization; default to mocks and a local limiter.
