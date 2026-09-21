# Ramp Sandbox Contract Tests and CI Gates sources

Reviewed: 2026-09-12

## First-party sources

- [Ramp OpenAPI specification](https://docs.ramp.com/openapi/developer-api.json)
- [Sandbox](https://docs.ramp.com/developer-api/v1/sandbox)
- [Errors](https://docs.ramp.com/developer-api/v1/error-handling)
- [Authorization](https://docs.ramp.com/developer-api/v1/authorization)

## Contract notes

Treat the OpenAPI schema as the endpoint-shape authority and the current guide exports as workflow authority. A sandbox test is supporting evidence, not permission to target production.

The live Ramp guides, machine-readable guide exports, and OpenAPI schema are authoritative when they change after this review date. Re-verify endpoint shapes, scopes, limits, data units, environment behavior, feature availability, and support status immediately before a live change.
