# CAST AI Webhooks and Audit Evidence: Official Sources

Consulted: 2026-09-13

- [Set up webhook notifications](https://docs.cast.ai/docs/setup-notification-webhook) — organization-level callback URL, severity triggers, and custom JSON request template.
- [Audit log](https://docs.cast.ai/docs/audit-log) — timestamps, operation names, initiators, user actions, and policy-driven operations.
- [API access](https://docs.cast.ai/docs/api-access) — region and organization identity boundary for any separate API reconciliation.

## Boundary

The configured request template is the receiver contract. Do not invent a universal CAST AI webhook schema, delivery signature, or retry guarantee when the selected product flow does not document it.
