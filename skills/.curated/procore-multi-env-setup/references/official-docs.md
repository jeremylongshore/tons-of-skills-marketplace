# Official Procore sources

Consulted: 2026-09-13

## Scope

These first-party sources ground **Procore Environment Isolation Matrix**. Refresh dates are intentionally omitted because they are time-sensitive.

## Sources

- [Procore sandboxes](https://developers.procore.com/documentation/development-environments)
- [Install a version in Developer Sandbox](https://developers.procore.com/documentation/install-version-sandbox)
- [OAuth endpoints](https://developers.procore.com/documentation/oauth-endpoints)
- [App installation overview](https://developers.procore.com/documentation/building-apps-install-arch)

## Provider boundaries

- Developer Sandbox uses sandbox credentials and sandbox hosts.
- On-Demand Sandbox uses production credentials and endpoints but a distinct company ID.
- Monthly Sandbox uses production credentials with monthly-sandbox hosts and a periodic refresh.
- App version keys used for installation are not interchangeable across every sandbox type.
- Source snapshot: `procore/documentation@fd31bc4b6c3d46b72b2b570c920ae5ccb2aa4318`.
