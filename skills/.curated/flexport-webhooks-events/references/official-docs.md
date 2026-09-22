# Official Flexport sources

Consulted: 2026-09-13

## Scope

These first-party sources ground **Flexport Webhook Integrity and Reconciliation**. Re-check them before relying on version-sensitive fields, permissions, or behavior.

## Sources

- [Webhook endpoints](https://apidocs.flexport.com/v3/tag/Webhook-Endpoints/)
- [Events](https://apidocs.flexport.com/v3/tag/Event/)
- [Milestones](https://apidocs.flexport.com/v3/tag/Milestones/)

## Provider boundaries

- REST v3 uses the documented API base and account/default request-version model.
- OAuth client credentials are endpoint-resource scoped; API keys are broad.
- MCP tool documentation uses synthetic paths, while the real transport is JSON-RPC at `https://mcp.flexport.com/mcp`.
- Do not invent undocumented global quotas, retry schedules, event names, retention rules, or mutation guarantees.
