# SpecStream MCP, Auth, and A2A Reference

## Remote MCP Server

- Endpoint: `https://api.specstream.ai/mcp` (Streamable HTTP).
- Authentication: OAuth (client signs user in) or `Authorization: Bearer <key>`.
- Discovery: `tools/list` exposes `search_web`, `read_pages`, `compile`, `quote_capacity_work`, `authorize_capacity_work`, `get_find_decisions`, `replay_find_decisions`, `list_web_searches`, `get_web_search`, `search_workspace`, `research_price`, `start_research`, and `get_research`.
- Client guides: `https://specstream.ai/docs/mcp/claude` (and `/clients`).

## Key Scopes and Privacy Controls

- `POST /v1/account/keys` / `PATCH /v1/account/keys/{id}`:
  - Default scopes when omitted: `account:read`, `specs:read`, `finds:read`, `projects:read` (read-only, cannot spend).
  - Spending requires `finds:spend` and `spend_cap_cents` > 0 (max `100000000`).
  - `zero_retention: true`: stores no request text or answer in history/logs.
  - `eu_egress_only: true`: routes outbound searches directly from Madrid, EU.
  - `engine_rule: {"deny": ["CN"]}`: excludes engines run from denied jurisdictions.

## Agent Signup and A2A

- Agent signup: `POST https://api.specstream.ai/v1/agent/signup` (email) followed by `POST /v1/agent/signup/verify` (6-digit code).
- A2A Agent Card: `https://api.specstream.ai/.well-known/agent-card.json`.
- A2A JSON-RPC: `https://api.specstream.ai/a2a` (`SendMessage`, `GetTask`, `CancelTask`, and 0.3 aliases `message/send`, `tasks/get`, `tasks/cancel`).
