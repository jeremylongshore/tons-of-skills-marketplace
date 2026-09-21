# Ramp API Error Triage sources

Reviewed: 2026-09-12

## First-party sources

- [Error handling](https://docs.ramp.com/developer-api/v1/error-handling)
- [Authorization](https://docs.ramp.com/developer-api/v1/authorization)
- [Rate limits and timeouts](https://docs.ramp.com/developer-api/v1/rate-limiting)
- [Deferred tasks](https://docs.ramp.com/developer-api/v1/deferred-tasks)

## Contract notes

Use status plus `error_v2` and `x-trace-id`; do not infer retry safety from status alone. Reconcile ambiguous writes before any replay.

The live Ramp guides, machine-readable guide exports, and OpenAPI schema are authoritative when they change after this review date. Re-verify endpoint shapes, scopes, limits, data units, environment behavior, feature availability, and support status immediately before a live change.
