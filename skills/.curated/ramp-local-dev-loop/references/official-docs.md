# Ramp Sandbox Development Loop sources

Reviewed: 2026-09-12

## First-party sources

- [Sandbox](https://docs.ramp.com/developer-api/v1/sandbox)
- [OpenAPI specification](https://docs.ramp.com/openapi/developer-api.json)
- [Webhooks](https://docs.ramp.com/developer-api/v1/webhooks)
- [Error handling](https://docs.ramp.com/developer-api/v1/error-handling)

## Contract notes

Sandbox is for vendor behavior, not the primary unit-test dependency. Local defaults must make accidental production access impossible.

The live Ramp guides, machine-readable guide exports, and OpenAPI schema are authoritative when they change after this review date. Re-verify endpoint shapes, scopes, limits, data units, environment behavior, feature availability, and support status immediately before a live change.
