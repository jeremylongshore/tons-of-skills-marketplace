# PRD: specstream-pack

**Author:** Tarek Etman (tarek@specstream.ai)
**Date:** 2026-11-16
**Status:** Active

## Problem

Developers building search, extraction, and structured web-data workflows in Claude Code frequently misconfigure endpoints, exceed batch limits, omit idempotency headers, or authorize open-ended Deep Search runs without confirming a maximum spend ceiling (`confirm_max_cents`). Existing search adapters written for Tavily, Exa, Brave, Serper, or SearXNG also often get rewritten from scratch instead of switching base URLs on SpecStream's drop-in routes.

## Target users

| User | Context | Primary need |
| --- | --- | --- |
| Application engineer | Replacing or integrating web search and page extraction (`GET /v1/web-search`, `POST /v1/extract`, or drop-in routes) | Correct endpoints, pricing tiers (`speed=fast` vs default), and offline request validation before live calls |
| Data / research operator | Building structured multi-row tables and recurring monitors with Deep Search | Clear quote-before-spend workflow (`compile`, `quote_capacity_work`, `authorize_capacity_work`) with source URL provenance |
| Claude Code / MCP user | Connecting the remote SpecStream MCP server (`https://api.specstream.ai/mcp`) | Working Streamable HTTP config, OAuth/Bearer auth setup, key scoping, and optional pay-per-request (MPP/x402) flow |

## Success criteria

1. All 5 skills pass `python3 scripts/validate-skills-schema.py --marketplace --verbose plugins/saas-packs/specstream-pack/` with zero errors and A-grade scores.
2. `python3 scripts/validate_specstream_payload.py` validates Search, Extract, Deep Search table, Schedule, and MCP config JSON payloads offline with zero network calls and zero `SPECSTREAM_API_KEY` set.
3. All pack contract unit tests in `tests/test_specstream_pack_contract.py` pass locally without paid API calls.

## Functional requirements

- **FR-1:** Document and validate SpecStream Search API (`GET /v1/web-search`, `POST /v1/web-search`) and drop-in routes (Tavily, Exa, Brave, Serper, SearXNG, Google CSE, Bing v7, Firecrawl v2).
- **FR-2:** Document and validate Extract API (`POST /v1/extract`) batch limits (1 to 20 URLs/pages, 20 MB ceiling), `format`/`include` options, and per-URL status handling (`ok`, `blocked`, `not_found`, `empty`, `unsupported`, `invalid_url`, `failed`).
- **FR-3:** Document and validate Deep Search table workflows (`POST /v1/agent/lists`, `POST /v1/parse`, MCP `compile`/`quote_capacity_work`/`authorize_capacity_work`/`get_find_decisions`) with `confirm_max_cents` approval boundaries and `source_url`/`seen_at` provenance.
- **FR-4:** Document and validate recurring Deep Search schedules, refresh billing rules, `spend_cap_cents` limits, and webhook/Slack/email/CRM/sheet delivery.
- **FR-5:** Document and validate remote Streamable HTTP MCP configuration (`https://api.specstream.ai/mcp`), key scoping (`finds:spend`, `zero_retention`, `eu_egress_only`), and agent signup.

## Out of scope

- Making live paid SpecStream API calls automatically on skill load or during CI/unit tests.
- Storing, logging, or hardcoding `SPECSTREAM_API_KEY` values in repository files.
- Bundling local MCP server binaries (SpecStream serves MCP remotely over Streamable HTTP at `https://api.specstream.ai/mcp`).
