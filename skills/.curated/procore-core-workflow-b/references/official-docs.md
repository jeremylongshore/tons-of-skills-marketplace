# Official Procore sources

Consulted: 2026-09-13

## Scope

These first-party sources ground **Procore Version-Aware Submittal Workflow**. Confirm the live version selector and changelog before implementing any operation.

## Sources

- [Submittals API reference](https://developers.procore.com/reference/rest/submittals?version=latest)
- [API lifecycle](https://developers.procore.com/documentation/rest-api-lifecycle)
- [REST API overview](https://developers.procore.com/documentation/rest-api-overview)
- [Error code reference](https://developers.procore.com/documentation/error-reference)

## Provider boundaries

- Submittal routes exist in multiple versions and some newer surfaces may be beta.
- Company headers, path parameters, and notification controls are endpoint-specific.
- Workflow data must be read from Procore rather than projected from generic statuses.
- Pagination and required fields come from the selected endpoint contract.
- Source snapshot: `procore/documentation@fd31bc4b6c3d46b72b2b570c920ae5ccb2aa4318`.
