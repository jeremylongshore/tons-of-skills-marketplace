# Official Flexport sources

Consulted: 2026-09-13

## Scope

These first-party sources ground **Flexport Integration Deployment Canary**. Re-check them before relying on version-sensitive fields, permissions, or behavior.

## Sources

- [Versioning](https://apidocs.flexport.com/v3/tag/Versioning/)
- [Webhook endpoints](https://apidocs.flexport.com/v3/tag/Webhook-Endpoints/)
- [MCP tools](https://apidocs.flexport.com/v3/tag/MCP-Tools/)

## Provider boundaries

- REST v3 uses the documented API base and account/default request-version model.
- OAuth client credentials are endpoint-resource scoped; API keys are broad.
- MCP tool documentation uses synthetic paths, while the real transport is JSON-RPC at `https://mcp.flexport.com/mcp`.
- Do not invent undocumented global quotas, retry schedules, event names, retention rules, or mutation guarantees.
