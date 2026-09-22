# Ramp Integration Observability sources

Reviewed: 2026-09-12

## First-party sources

- [Support and trace IDs](https://docs.ramp.com/developer-api/v1/debugging)
- [Webhooks](https://docs.ramp.com/developer-api/v1/webhooks)
- [Deferred tasks](https://docs.ramp.com/developer-api/v1/deferred-tasks)
- [ERP integrations](https://docs.ramp.com/developer-api/v1/erp-integrations)

## Contract notes

Use `x-trace-id` as a safe correlation field, but make reconciled business state the authority for financial completeness.

The live Ramp guides, machine-readable guide exports, and OpenAPI schema are authoritative when they change after this review date. Re-verify endpoint shapes, scopes, limits, data units, environment behavior, feature availability, and support status immediately before a live change.
