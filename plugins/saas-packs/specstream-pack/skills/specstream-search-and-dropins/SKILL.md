---
name: specstream-search-and-dropins
description: |
  Configure and validate SpecStream Search API requests and drop-in routes for Tavily, Exa, Brave, Serper, and SearXNG on https://api.specstream.ai. Use when building web search integrations, switching an existing search client to SpecStream, or checking search request parameters offline. Trigger with "SpecStream search", "switch Tavily to SpecStream", or "validate SpecStream search payload".
argument-hint: "[search-payload.json]"
allowed-tools: Read, Bash(python3:*)
version: 1.0.0
author: Tarek Etman <tarek@specstream.ai>
license: MIT
compatibility: Designed for Claude Code
tags: [saas, specstream, web-search, drop-in, search-api]
---
# SpecStream Search API and Drop-In Routes

## Overview

Build and validate live web search requests against SpecStream's Search API (`GET` or `POST https://api.specstream.ai/v1/web-search`) and its drop-in endpoints. Default search costs $5 per 1,000 calls of up to 10 results, while the fast tier (`speed=fast`, the default on drop-in routes) costs $1 per 1,000 calls.

## Prerequisites

- An optional `SPECSTREAM_API_KEY` environment variable (Bearer token with `finds:spend` scope and positive `spend_cap_cents`), or x402 per-call payment when running live queries without an account.
- Zero credentials are required for offline payload validation or for reading `GET https://api.specstream.ai/v1/search-dialects` and `GET https://api.specstream.ai/v1/search-engines`.
- Python 3.10+ to run the offline validator and [API contract](references/api-contract.md).

## Instructions

1. Use `Read` to inspect the target search client or JSON payload and review [the Search API contract](references/api-contract.md).
2. Choose native `GET /v1/web-search` (or `POST /v1/web-search` to keep query strings out of URL logs), or select the matching drop-in base URL (`https://api.specstream.ai/tavily`, `/exa`, `/serper`, `/searxng/<key>`, `/res/v1/web/search` for Brave, `/customsearch/v1` for Google CSE, `/v7.0/search` for Bing v7, or `/firecrawl` for Firecrawl v2).
3. Verify query bounds (`q` 1 to 2,000 characters), pagination (`num` 1 to 100 or 1 to 200 with `images=true`, `page` 1 to 10), `passages=true` vs `images=true` exclusivity, and `Idempotency-Key` length (at most 128 characters).
4. Run the offline payload validator before executing any live search:

```bash
python3 scripts/validate_specstream_payload.py --kind search --file search-payload.json
```

5. For drop-in migrations, change only the base URL and API key configuration (`SPECSTREAM_API_KEY`), keeping existing response parsing intact (`speed=fast` by default, or add `specstream_speed=default` when full default search is needed).

## Output

Return the validated request JSON, selected endpoint or drop-in base address, expected response root (`data.answer`, `data.rows`, `data.sources`, or the drop-in API shape), and the offline validator exit status. Never echo `SPECSTREAM_API_KEY` values in output.

## Error Handling

| Condition | Response |
| --- | --- |
| `401` (`missing_api_key` or `invalid_token`) | Confirm `SPECSTREAM_API_KEY` is supplied via `Authorization: Bearer` (or the drop-in header), or use x402 per-call payment. |
| `402` (`insufficient_balance`) | Balance or monthly limit reached; direct the owner to top up at `https://specstream.ai/workspace`. |
| `403` (`scopes` or `spend_cap_cents`) | Key lacks `finds:spend` or hit `spend_cap_cents`; update or rotate the key in the workspace. |
| `409` or `422` | Generate a fresh `Idempotency-Key` (<= 128 chars) on `409`, or trim `q` to 1-2,000 chars on `422`. |
| `503` (or `429` on drop-in routes) with `Retry-After` | Wait the header duration before retrying; nothing is charged. |

## Examples

**Example 1: Validate a native fast search with passages offline**

```bash
# pages_wait_ms=1500 waits up to 1.5s for page text on the first five sources
python3 scripts/validate_specstream_payload.py --kind search --stdin <<'EOF'
{"q": "\"EU AI Act\" compliance timeline", "speed": "fast", "num": 10, "passages": true, "pages_wait_ms": 1500}
EOF
```

**Example 2: Switch Tavily and Exa Python clients to SpecStream drop-in URLs**

```python
import os
from tavily import TavilyClient
from exa_py import Exa

key = os.environ["SPECSTREAM_API_KEY"]
tavily = TavilyClient(api_key=key, api_base_url="https://api.specstream.ai/tavily")
exa = Exa(api_key=key, base_url="https://api.specstream.ai/exa")
```

## Resources

- [Search API and drop-in contract](references/api-contract.md)
- [SpecStream Agent Reference](https://specstream.ai/agents.md)
- [SpecStream Search Dialects JSON](https://api.specstream.ai/v1/search-dialects)
