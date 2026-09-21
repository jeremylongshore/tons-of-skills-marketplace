# Ramp Integration Deployment and Rollout sources

Reviewed: 2026-09-12

## First-party sources

- [Sandbox](https://docs.ramp.com/developer-api/v1/sandbox)
- [Authorization](https://docs.ramp.com/developer-api/v1/authorization)
- [Webhooks](https://docs.ramp.com/developer-api/v1/webhooks)
- [OpenAPI specification](https://docs.ramp.com/openapi/developer-api.json)

## Contract notes

Environment proof and exact artifact identity are release gates. Never infer production authority from working sandbox credentials.

The live Ramp guides, machine-readable guide exports, and OpenAPI schema are authoritative when they change after this review date. Re-verify endpoint shapes, scopes, limits, data units, environment behavior, feature availability, and support status immediately before a live change.
