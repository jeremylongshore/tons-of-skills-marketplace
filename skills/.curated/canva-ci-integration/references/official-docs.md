# Official Canva sources

Consulted: 2026-09-13

## Scope

These first-party sources establish fork-safe contract and protected integration testing.

## Sources

- [Connect API security](https://www.canva.dev/docs/connect/guidelines/security/)
- [Authentication](https://www.canva.dev/docs/connect/authentication/)
- [Latest OpenAPI contract](https://www.canva.dev/sources/connect/api/latest/api.yml)

## Boundary

CI must use mocks for untrusted changes and a separately protected synthetic-user lane for live checks.
