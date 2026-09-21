# Official Canva sources

Consulted: 2026-09-13

## Scope

These first-party sources establish low-cardinality, privacy-safe service telemetry.

## Sources

- [API requests and responses](https://www.canva.dev/docs/connect/api-requests-responses/)
- [Error responses](https://www.canva.dev/docs/connect/error-responses/)
- [Connect API security](https://www.canva.dev/docs/connect/guidelines/security/)

## Boundary

Do not assume undocumented rate-limit headers; instrument known application budget and observed status instead.
