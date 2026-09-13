# Official Procore sources

Consulted: 2026-09-13

## Scope

These first-party sources ground **Procore Permission and Project-Scope Governance**. Endpoint references and Procore's permission builder define operation-specific requirements.

## Sources

- [Developer Managed Service Accounts](https://developers.procore.com/documentation/developer-managed-service-accounts)
- [Working with user permissions](https://developers.procore.com/documentation/tutorial-user-permissions)
- [Troubleshooting permissions](https://developers.procore.com/documentation/troubleshooting)
- [Build a data connector app](https://developers.procore.com/documentation/building-data-connection-apps)

## Provider boundaries

- DMSA permissions are declared in the app manifest and applied through installation.
- Company administrators select permitted projects.
- App updates or reinstalls can require permitted-project reconfiguration.
- Authorization Code access follows the logged-in user's permissions instead.
- Source snapshot: `procore/documentation@fd31bc4b6c3d46b72b2b570c920ae5ccb2aa4318`.
