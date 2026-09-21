# Official Canva sources

Consulted: 2026-09-13

## Scope

These first-party sources establish backend OAuth, policy, async workers, and reconciliation.

## Sources

- [Authentication](https://www.canva.dev/docs/connect/authentication/)
- [Connect API security](https://www.canva.dev/docs/connect/guidelines/security/)
- [API requests and responses](https://www.canva.dev/docs/connect/api-requests-responses/)

## Boundary

Keep token rotation serialized per user and keep job submission separate from status reconciliation.
