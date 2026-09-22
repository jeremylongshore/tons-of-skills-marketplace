# Ramp Integration Reference Architecture sources

Reviewed: 2026-09-12

## First-party sources

- [Developer API introduction](https://docs.ramp.com/developer-api/v1/introduction)
- [Webhooks](https://docs.ramp.com/developer-api/v1/webhooks)
- [Authorization](https://docs.ramp.com/developer-api/v1/authorization)
- [ERP integrations](https://docs.ramp.com/developer-api/v1/erp-integrations)

## Contract notes

Use the Developer API for deterministic long-lived integrations. Events trigger work; a durable ledger and current-state reconciliation authorize business effects.

The live Ramp guides, machine-readable guide exports, and OpenAPI schema are authoritative when they change after this review date. Re-verify endpoint shapes, scopes, limits, data units, environment behavior, feature availability, and support status immediately before a live change.
