# Ramp API Throughput and Sync Performance sources

Reviewed: 2026-09-12

## First-party sources

- [Rate limits and timeouts](https://docs.ramp.com/developer-api/v1/rate-limiting)
- [Pagination](https://docs.ramp.com/developer-api/v1/pagination)
- [Webhooks](https://docs.ramp.com/developer-api/v1/webhooks)
- [Deferred tasks](https://docs.ramp.com/developer-api/v1/deferred-tasks)

## Contract notes

The documented default limit is shared per source IP and can change. Centralize throttling across workers and re-check it before tuning.

The live Ramp guides, machine-readable guide exports, and OpenAPI schema are authoritative when they change after this review date. Re-verify endpoint shapes, scopes, limits, data units, environment behavior, feature availability, and support status immediately before a live change.
