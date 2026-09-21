# Official Canva sources

Consulted: 2026-09-13

## Scope

These first-party sources establish OAuth Authorization Code with SHA-256 PKCE.

## Sources

- [Authentication](https://www.canva.dev/docs/connect/authentication/)
- [Connect API security](https://www.canva.dev/docs/connect/guidelines/security/)
- [OAuth scopes](https://www.canva.dev/docs/connect/appendix/scopes/)

## Boundary

Keep the verifier, client secret, access token, and rotating refresh token out of browser-visible state and logs.
