# Notion Error Classification and Recovery: first-party evidence

Reviewed: 2026-09-12

Notion's public documentation establishes the current product and API contract. The selected connection's type, workspace binding, capabilities, explicitly shared content, selected tested API version, and observed responses remain execution evidence for that environment.

- [Status and error codes](https://developers.notion.com/reference/status-codes)
- [Authentication](https://developers.notion.com/reference/authentication)
- [Connection capabilities](https://developers.notion.com/reference/capabilities)
- [Request and payload limits](https://developers.notion.com/reference/request-limits)
- [API versioning](https://developers.notion.com/reference/versioning)

## Current contract notes

- At review time, the current REST contract is `2026-03-11`; send a tested `Notion-Version` on REST calls and use a compatible SDK.
- The modern model separates database containers from data sources. Query and schema operations use a data-source ID; search returns pages and data sources.
- The current contract uses a position object for block placement, `in_trash` for REST trash state, and `meeting_notes` for the renamed block type.
- Request limits can change. Handle HTTP 429, honor `Retry-After`, bound retries, paginate completely, and tolerate additive response fields.
- Skill invocation never grants permission to access credentials or workspace data, expand capabilities or sharing, write content, subscribe webhooks, transfer files, deploy, spend money, or delete resources.

## Evidence rules

- Recheck these pages at execution time and record the selected API version, SDK version, connection alias, workspace alias, source revision, and observation date.
- Keep internal connections, public OAuth connections, personal access tokens, connection webhooks, database-automation webhooks, MCP, Workers, and Admin APIs as distinct contracts.
- When first-party documentation and observed behavior differ, fail closed, preserve redacted request evidence, and resolve the discrepancy before mutation.
