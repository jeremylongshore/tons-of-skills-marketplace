# Ramp Webhook Verification and Processing sources

Reviewed: 2026-09-12

## First-party sources

- [Webhooks](https://docs.ramp.com/developer-api/v1/webhooks)
- [Authorization](https://docs.ramp.com/developer-api/v1/authorization)
- [Error handling](https://docs.ramp.com/developer-api/v1/error-handling)
- [Transactions API](https://docs.ramp.com/developer-api/v1/api/transactions)

## Contract notes

Always verify the exact raw body. Treat the event ID as the deduplication key and current resource state as the business-state authority.

The live Ramp guides, machine-readable guide exports, and OpenAPI schema are authoritative when they change after this review date. Re-verify endpoint shapes, scopes, limits, data units, environment behavior, feature availability, and support status immediately before a live change.
