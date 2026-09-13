# Official Procore sources

Consulted: 2026-09-13

## Scope

These first-party sources ground **Procore Integration Security Boundary**. Apply organization policy when it is stricter than provider guidance.

## Sources

- [API security overview](https://developers.procore.com/documentation/api-security-overview)
- [Developer Managed Service Accounts](https://developers.procore.com/documentation/developer-managed-service-accounts)
- [OAuth authentication endpoints](https://developers.procore.com/documentation/oauth-endpoints)
- [Multiple Procore Regions headers](https://developers.procore.com/documentation/mpz-headers)
- [Secure file access](https://developers.procore.com/documentation/secure-file-access-tips)

## Provider boundaries

- OAuth authentication and tool permissions are separate controls.
- DMSA access is constrained through declared permissions and permitted projects.
- Company routing must not be inferred from stale tenant context.
- Secure file retrieval may require the Bearer token and must tolerate URL schema changes.
- Source snapshot: `procore/documentation@fd31bc4b6c3d46b72b2b570c920ae5ccb2aa4318`.
