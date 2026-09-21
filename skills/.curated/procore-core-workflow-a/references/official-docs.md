# Official Procore sources

Consulted: 2026-09-13

## Scope

These first-party sources ground **Procore Governed RFI Lifecycle**. Use the live endpoint reference for the target operation because fields and changelog entries evolve.

## Sources

- [RFI API reference](https://developers.procore.com/reference/rest/rfis?version=latest)
- [REST request and response concepts](https://developers.procore.com/documentation/restful-api-concepts)
- [Error code reference](https://developers.procore.com/documentation/error-reference)
- [File attachments and image uploads](https://developers.procore.com/documentation/tutorial-attachments)

## Provider boundaries

- RFI operations are project-scoped and permissioned.
- Required mutation fields and workflow behavior come from the selected endpoint.
- A 404 may conceal a resource the principal cannot read.
- Attachments use their documented upload or reference flow, not arbitrary inline data.
- Source snapshot: `procore/documentation@fd31bc4b6c3d46b72b2b570c920ae5ccb2aa4318`.
