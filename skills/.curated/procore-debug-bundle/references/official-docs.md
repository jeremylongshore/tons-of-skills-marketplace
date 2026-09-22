# Official Procore sources

Consulted: 2026-09-13

## Scope

These first-party sources ground **Redacted Procore Diagnostic Manifest**. Organization security and retention policy may impose stricter exclusions.

## Sources

- [Procore troubleshooting](https://developers.procore.com/documentation/troubleshooting)
- [API Call Activity Report](https://developers.procore.com/documentation/api-activity-export)
- [API security overview](https://developers.procore.com/documentation/api-security-overview)
- [OAuth authentication endpoints](https://developers.procore.com/documentation/oauth-endpoints)

## Provider boundaries

- Support diagnostics need method, URL, sanitized headers and body, status, and occurrence time.
- OAuth credentials, tokens, and signed URLs are sensitive and excluded.
- The API activity report provides normalized production call evidence without requiring raw payload dumps.
- Collection remains bounded by the incident and approved audience.
- Source snapshot: `procore/documentation@fd31bc4b6c3d46b72b2b570c920ae5ccb2aa4318`.
