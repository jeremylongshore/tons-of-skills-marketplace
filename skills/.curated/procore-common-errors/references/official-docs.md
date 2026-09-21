# Official Procore sources

Consulted: 2026-09-13

## Scope

These first-party sources ground **Procore Error Classification and Recovery**. Endpoint-specific error bodies remain authoritative for a concrete request.

## Sources

- [Troubleshooting](https://developers.procore.com/documentation/troubleshooting)
- [Error code reference](https://developers.procore.com/documentation/error-reference)
- [Integration Health](https://developers.procore.com/documentation/integration-health)
- [API Call Activity Report](https://developers.procore.com/documentation/api-activity-export)

## Provider boundaries

- A 404 can represent a resource the principal cannot read.
- Failed requests also consume rate budget.
- Refresh tokens for Authorization Code flows require careful single-use rotation.
- Private and deprecated endpoint usage are distinct integration-health defects.
- Source snapshot: `procore/documentation@fd31bc4b6c3d46b72b2b570c920ae5ccb2aa4318`.
