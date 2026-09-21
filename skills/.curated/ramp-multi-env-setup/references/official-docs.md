# Ramp Sandbox and Production Isolation sources

Reviewed: 2026-09-12

## First-party sources

- [Sandbox](https://docs.ramp.com/developer-api/v1/sandbox)
- [Authorization](https://docs.ramp.com/developer-api/v1/authorization)
- [Virtual cards](https://docs.ramp.com/developer-api/v1/virtual-cards)
- [Webhooks](https://docs.ramp.com/developer-api/v1/webhooks)

## Contract notes

Environment is part of credential identity. Never implement silent host fallback or copy a sandbox application configuration into production.

The live Ramp guides, machine-readable guide exports, and OpenAPI schema are authoritative when they change after this review date. Re-verify endpoint shapes, scopes, limits, data units, environment behavior, feature availability, and support status immediately before a live change.
