# Official Procore sources

Consulted: 2026-09-13

## Scope

These first-party sources ground **Procore Webhook and Reconciliation Boundary**. Confirm resource support and route versions in the live Hooks, Triggers, and Deliveries references.

## Sources

- [How webhooks work](https://developers.procore.com/documentation/webhooks)
- [Set up webhooks](https://developers.procore.com/documentation/webhooks-api)
- [Hooks API reference](https://developers.procore.com/reference/rest/hooks?version=latest)
- [Triggers API reference](https://developers.procore.com/reference/rest/triggers?version=latest)
- [Deliveries API reference](https://developers.procore.com/reference/rest/deliveries?version=latest)

## Provider boundaries

- Notifications are best-effort signals; REST data is authoritative.
- Receivers must acknowledge within the documented timeout and process asynchronously.
- Duplicate deliveries require idempotency.
- New integrations should use the provider's current recommended payload format.
- Source snapshot: `procore/documentation@fd31bc4b6c3d46b72b2b570c920ae5ccb2aa4318`.
