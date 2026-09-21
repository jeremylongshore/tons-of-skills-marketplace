# Official Flexport sources

Consulted: 2026-09-13

## Scope

These first-party sources ground **Measured Flexport Pagination and Concurrency**. Re-check them before relying on version-sensitive fields, permissions, or behavior.

## Sources

- [MCP tools](https://apidocs.flexport.com/v3/tag/MCP-Tools/)
- [Freight invoices tutorial](https://developers.flexport.com/tutorials/freight-invoices-api-tutorial/)
- [Shipment API tutorial](https://developers.flexport.com/tutorials/shipment-api-tutorial/)

## Provider boundaries

- REST v3 uses the documented API base and account/default request-version model.
- OAuth client credentials are endpoint-resource scoped; API keys are broad.
- MCP tool documentation uses synthetic paths, while the real transport is JSON-RPC at `https://mcp.flexport.com/mcp`.
- Do not invent undocumented global quotas, retry schedules, event names, retention rules, or mutation guarantees.
