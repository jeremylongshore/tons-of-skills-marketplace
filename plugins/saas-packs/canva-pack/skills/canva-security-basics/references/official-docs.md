# Official Canva sources

Consulted: 2026-09-13

## Scope

These first-party sources establish backend credentials, least privilege, and webhook authenticity.

## Sources

- [Connect API security](https://www.canva.dev/docs/connect/guidelines/security/)
- [Authentication](https://www.canva.dev/docs/connect/authentication/)
- [Webhook keys](https://www.canva.dev/docs/connect/api-reference/webhooks/keys/)

## Boundary

Cache rotating JWKs and refetch only for an unknown kid; the preview keys endpoint is public and unauthenticated.
