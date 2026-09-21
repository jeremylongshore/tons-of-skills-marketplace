# Official Procore sources

Consulted: 2026-09-13

## Scope

These first-party sources ground **Procore App Version Promotion**. Portal state and the concrete app manifest remain authoritative for a release.

## Sources

- [Promote a version to production](https://developers.procore.com/documentation/building-apps-promote-manifest)
- [App versioning and update notification](https://developers.procore.com/documentation/building-apps-versioning)
- [Install a version in Developer Sandbox](https://developers.procore.com/documentation/install-version-sandbox)
- [Integration Health](https://developers.procore.com/documentation/integration-health)

## Provider boundaries

- Procore app versions carry semantic versions and release notes.
- Permission changes are part of the reviewed app contract.
- Sandbox and production installations use environment-specific credentials and keys.
- Integration Health and API activity provide post-promotion evidence.
- Source snapshot: `procore/documentation@fd31bc4b6c3d46b72b2b570c920ae5ccb2aa4318`.
