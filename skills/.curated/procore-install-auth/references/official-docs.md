# Official Procore sources

Consulted: 2026-09-13

## Scope

These first-party sources ground **Procore OAuth and DMSA Boundary**. Re-check them before changing grant, token, permission, or environment behavior.

## Sources

- [Choose an authentication method](https://developers.procore.com/documentation/oauth-choose-grant-type)
- [OAuth authentication endpoints](https://developers.procore.com/documentation/oauth-endpoints)
- [Client Credentials grant](https://developers.procore.com/documentation/oauth-client-credentials)
- [Developer Managed Service Accounts](https://developers.procore.com/documentation/developer-managed-service-accounts)

## Provider boundaries

- Client Credentials relies on a DMSA for modern data connector applications.
- Authorization Code acts with the authenticated user's permissions.
- Production and Developer Sandbox credentials and tokens are separate.
- DMSA access is bounded by manifest tool permissions and administrator-selected permitted projects.
- Source snapshot: `procore/documentation@fd31bc4b6c3d46b72b2b570c920ae5ccb2aa4318`.
