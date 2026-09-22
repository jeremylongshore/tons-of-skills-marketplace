# Ramp-to-ERP Accounting Sync sources

Reviewed: 2026-09-12

## First-party sources

- [ERP integrations](https://docs.ramp.com/developer-api/v1/erp-integrations)
- [Accounting API](https://docs.ramp.com/developer-api/v1/api/accounting)
- [Data relationships](https://docs.ramp.com/developer-api/v1/data-relationships)
- [Monetary values](https://docs.ramp.com/developer-api/v1/monetary-values)

## Contract notes

The ERP receipt is the commit point. Mark Ramp objects synced only after durable downstream success and retain both Ramp IDs and ERP remote IDs.

The live Ramp guides, machine-readable guide exports, and OpenAPI schema are authoritative when they change after this review date. Re-verify endpoint shapes, scopes, limits, data units, environment behavior, feature availability, and support status immediately before a live change.
