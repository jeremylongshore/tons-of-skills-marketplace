# Official Procore sources

Consulted: 2026-09-13

## Scope

These first-party sources ground **Procore Governed Connector Architecture**. Concrete endpoint and data contracts must still be selected from the live reference.

## Sources

- [Build a data connector app](https://developers.procore.com/documentation/building-data-connection-apps)
- [Developer Managed Service Accounts](https://developers.procore.com/documentation/developer-managed-service-accounts)
- [Webhook reliability](https://developers.procore.com/documentation/webhooks)
- [API usage guidelines](https://developers.procore.com/documentation/api-usage-guidelines)
- [Using Sync Actions](https://developers.procore.com/documentation/using-sync-actions)

## Provider boundaries

- Webhooks are freshness signals and REST is the resource source of truth.
- Tenant routing and permissions must stay explicit through asynchronous processing.
- Sync actions and origin identifiers are resource-specific.
- Endpoint versions and pagination belong in adapters rather than a global constant.
- Source snapshot: `procore/documentation@fd31bc4b6c3d46b72b2b570c920ae5ccb2aa4318`.
