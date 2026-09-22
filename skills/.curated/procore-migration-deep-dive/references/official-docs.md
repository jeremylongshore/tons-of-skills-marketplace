# Official Procore sources

Consulted: 2026-09-13

## Scope

These first-party sources ground **Procore Resumable Data Migration**. Each resource reference determines whether origin identifiers or sync actions are supported.

## Sources

- [Using Sync Actions](https://developers.procore.com/documentation/using-sync-actions)
- [API call sequencing](https://developers.procore.com/documentation/api-call-sequencing)
- [Direct file uploads](https://developers.procore.com/documentation/tutorial-uploads)
- [Data model considerations](https://developers.procore.com/documentation/data-model-considerations)
- [Rate limiting](https://developers.procore.com/documentation/rate-limiting)

## Provider boundaries

- Sync actions and origin identifiers are supported only on documented resources.
- Migration order follows resource dependencies.
- Files use distinct upload and association contracts.
- Checkpoint advancement requires reconciliation rather than request acceptance alone.
- Source snapshot: `procore/documentation@fd31bc4b6c3d46b72b2b570c920ae5ccb2aa4318`.
