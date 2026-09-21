# Ramp Integration Security Baseline sources

Reviewed: 2026-09-12

## First-party sources

- [Authorization](https://docs.ramp.com/developer-api/v1/authorization)
- [Webhooks](https://docs.ramp.com/developer-api/v1/webhooks)
- [Virtual cards](https://docs.ramp.com/developer-api/v1/virtual-cards)
- [Error handling](https://docs.ramp.com/developer-api/v1/error-handling)

## Contract notes

Verify `X-Ramp-Signature` as HMAC-SHA256 over the exact raw body. Never reserialize parsed JSON for signature verification.

The live Ramp guides, machine-readable guide exports, and OpenAPI schema are authoritative when they change after this review date. Re-verify endpoint shapes, scopes, limits, data units, environment behavior, feature availability, and support status immediately before a live change.
