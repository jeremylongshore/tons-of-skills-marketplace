# Official Procore sources

Consulted: 2026-09-13

## Scope

These first-party sources ground **Procore Endpoint Contract Cutover**. The affected endpoint's live reference and changelog entry define the actual migration.

## Sources

- [API lifecycle](https://developers.procore.com/documentation/rest-api-lifecycle)
- [API changelog](https://developers.procore.com/documentation/changelog)
- [Integration Health](https://developers.procore.com/documentation/integration-health)
- [API Call Activity Report](https://developers.procore.com/documentation/api-activity-export)

## Provider boundaries

- Lifecycle status and replacement are endpoint-specific.
- Deprecated and private endpoint usage are observable integration-health defects.
- Production activity evidence identifies callers that static search can miss.
- The old path is removed only after traffic and compatibility evidence support removal.
- Source snapshot: `procore/documentation@fd31bc4b6c3d46b72b2b570c920ae5ccb2aa4318`.
