# Official Procore sources

Consulted: 2026-09-13

## Scope

These first-party sources ground **Procore Integration Incident Command**. The application's own incident policy defines severity, communications, and authority.

## Sources

- [Procore system status](https://status.procore.com/)
- [Troubleshooting](https://developers.procore.com/documentation/troubleshooting)
- [Integration Health](https://developers.procore.com/documentation/integration-health)
- [API Call Activity Report](https://developers.procore.com/documentation/api-activity-export)
- [Webhook reliability](https://developers.procore.com/documentation/webhooks)

## Provider boundaries

- Provider status and application regression are separate hypotheses.
- Webhook notification gaps require REST reconciliation.
- Rate and retry headers constrain recovery traffic.
- Unknown activity under app credentials may require a security investigation.
- Source snapshot: `procore/documentation@fd31bc4b6c3d46b72b2b570c920ae5ccb2aa4318`.
