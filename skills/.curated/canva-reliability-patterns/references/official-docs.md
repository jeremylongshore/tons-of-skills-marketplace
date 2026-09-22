# Official Canva sources

Consulted: 2026-09-13

## Scope

These first-party sources establish retriable transport, async jobs, token rotation, and dead letters.

## Sources

- [API requests and responses](https://www.canva.dev/docs/connect/api-requests-responses/)
- [Authentication](https://www.canva.dev/docs/connect/authentication/)
- [Error responses](https://www.canva.dev/docs/connect/error-responses/)

## Boundary

Do not blindly replay mutating operations; reconcile the existing job and serialize single-use refresh-token exchange.
