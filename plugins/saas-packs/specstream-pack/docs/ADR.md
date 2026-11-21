# ADR: specstream-pack - Offline-Validated SpecStream Operator Pack

**Author:** Tarek Etman (tarek@specstream.ai)
**Date:** 2026-11-16
**Status:** Accepted

## Context

SpecStream exposes several live web data surfaces: the Search API (`GET /v1/web-search`), drop-in search routes for Tavily/Exa/Brave/Serper/SearXNG, the Extract API (`POST /v1/extract`), Deep Search structured tables and recurring schedules, and a remote Streamable HTTP MCP server (`https://api.specstream.ai/mcp`). Users need accurate guidance and deterministic pre-flight payload checks without bundling third-party runtime dependencies or triggering paid API calls when `SPECSTREAM_API_KEY` is unset.

## Decision

We ship `specstream-pack` as a 5-skill operator pack under `plugins/saas-packs/specstream-pack/` backed by a zero-dependency Python 3 standard-library validator (`scripts/validate_specstream_payload.py`) and per-skill API contract references (`references/api-contract.md`).

## Alternatives considered

| Alternative | Why rejected |
| --- | --- |
| 18-30 generic tutorial skills | Creates boilerplate across generic slots; 5 product-aligned skills keep each workflow directly tied to SpecStream endpoints and parameters. |
| Shipping a bundled `.mcp.json` or live-calling script | Triggers remote-MCP and network-egress scan challenges in CI and fails when `SPECSTREAM_API_KEY` is not configured. |
| Node/npm runtime dependencies in the pack | Requires `npm install` inside the plugin directory; Python 3 stdlib works in any environment with no extra install step. |

## Consequences

**Positive:**

- Every skill operates cleanly when `SPECSTREAM_API_KEY` is unset and makes zero network requests during validation or testing.
- Drop-in routes, quote-before-spend Deep Search approvals (`confirm_max_cents`), and schedule spend caps are verified deterministically before execution.

**Negative / accepted tradeoffs:**

- Users connecting the remote MCP server copy the documented configuration snippet into their client config rather than having a plugin-level `.mcp.json` auto-register a remote URL.

## Tool-permission scope

| Tool | Why it is needed |
| --- | --- |
| `Read` | Inspect user code, request payloads, MCP config files, and `references/api-contract.md`. |
| `Bash(python3:*)` | Run the offline Python standard-library payload validator (`scripts/validate_specstream_payload.py`). |
