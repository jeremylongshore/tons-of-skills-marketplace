# specstream-pack

**Operator workflows and offline payload validation for SpecStream Search, drop-in search APIs, Extract, Deep Search tables, schedules, and remote MCP.**

## Problem

Teams integrating live web search, page extraction, structured web tables, and scheduled monitors often hit avoidable integration mistakes: exceeding the 20-URL Extract cap, sending Deep Search runs without a `confirm_max_cents` ceiling, missing `Idempotency-Key` headers on retries, or rewriting existing Tavily/Exa/Brave/Serper/SearXNG clients instead of switching base URLs.

## Solution

`specstream-pack` provides five focused Claude Code skills grounded in SpecStream's API specification (`https://specstream.ai/agents.md`) plus an offline Python standard-library validator (`scripts/validate_specstream_payload.py`) that checks payloads and MCP configs with no API key and no network calls.

## W5

| | |
| --- | --- |
| **Who** | Engineers and researchers building web search, extraction, structured table collection, or scheduled monitoring in Claude Code |
| **What** | Five operator skills covering Search + drop-ins, Extract, Deep Search tables, recurring schedules, and remote MCP setup |
| **When** | Configuring clients, migrating drop-in search providers, scoping spend limits, or validating request payloads before live calls |
| **Where** | Claude Code (`plugins/saas-packs/specstream-pack`) and local CI/pre-flight checks |
| **Why** | Catches payload, batch-limit, idempotency, and spend-approval errors offline while preserving exact SpecStream endpoints and provenance fields |

## Stack

| Layer | Choice |
| --- | --- |
| Skill runtime | Claude Code `SKILL.md` (5 skills, marketplace schema 4.1.0) |
| Offline validator | Python 3 standard library (`scripts/validate_specstream_payload.py`) |
| SpecStream endpoints | `https://api.specstream.ai` (REST, drop-in routes, Streamable HTTP MCP, A2A) |

## Differentiators

1. **Drop-in migration ready:** Covers exact base-URL swaps for Tavily, Exa, Brave, Serper, SearXNG, Google CSE, Bing v7, and Firecrawl v2 on `https://api.specstream.ai`.
2. **Quote-before-spend safety:** Enforces SpecStream's `compile` -> `quote_capacity_work` -> `authorize_capacity_work` (`confirm_max_cents`) boundary and schedule `spend_cap_cents` checks.
3. **Zero-key offline verification:** Works with no `SPECSTREAM_API_KEY` set; all structural validation and unit tests run locally with zero network calls.
