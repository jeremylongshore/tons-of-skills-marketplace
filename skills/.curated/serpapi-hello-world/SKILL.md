---
name: serpapi-hello-world
description: 'Run a controlled first Google search through an official SerpAPI client and validate metadata before consuming result sections. Use when proving a new integration end to end. Trigger with "run a SerpAPI smoke test".'
argument-hint: "[query] [python|javascript]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit, Bash(python3:*), Bash(npm:*)
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, serpapi, google-search, smoke-test, sdk]
model: inherit
effort: medium
compatibility: Designed for Claude Code; a live smoke test requires a valid server-side key and may consume search allowance
---
# SerpAPI Controlled First Search

## Overview

Prove authentication, transport, search status, and schema handling with one bounded query and a redacted receipt.

## Prerequisites

- An official SerpAPI client already installed
- `SERPAPI_KEY` loaded from an approved server-side secret store
- A harmless query, expected locale, allowance owner, and live-call approval

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect local setup, `WebFetch` to verify current Google Search parameters, `Write` or `Edit` for the smoke-test code and redacted receipt, and `Bash(python3:*)` or `Bash(npm:*)` only to run the approved check.

## Current Contract

Google Search uses `engine=google` and query parameter `q`. JSON responses expose `search_metadata.status`, a search ID, search parameters, and optional result sections. A successful search may legitimately contain no organic results.

## Authentication

Pass the private key from `SERPAPI_KEY` through the official client. Never interpolate it into source, logs, exceptions, fixtures, screenshots, or receipts.

## Instructions

1. Confirm the query is non-sensitive and set explicit `location`, `hl`, and `gl` values when geographic reproducibility matters.
2. Check Account API for available searches and hourly throughput without spending allowance.
3. Preview one request with `engine=google`, `q`, and the minimum necessary parameters.
4. After approval, execute exactly one search with a finite client timeout.
5. Require `search_metadata.status == "Success"`; treat missing result sections as optional schema branches.
6. Extract only the fields required by the caller and preserve the search ID for support correlation.
7. Record client version, normalized parameters, status, elapsed time, result counts, and search ID with the key and sensitive query data redacted.

## Output

Return the approved request shape, search status, result-section counts, search ID, redacted receipt location, and any schema assumptions that need fixtures.

## Error Handling

| Condition | Response |
|---|---|
| HTTP 400 | Correct the engine-specific parameters; do not retry unchanged. |
| HTTP 401 or 403 | Stop and repair authorization without printing the key. |
| HTTP 429 | Inspect Account API before deciding whether to wait or increase allowance. |
| HTTP 5xx or timeout | Retry a bounded number of times with jitter and preserve the search ID if present. |
| `Success` with no organic results | Inspect other documented sections and the engine-specific `_state`; do not label it an API failure. |

## Example

```python
import os
import serpapi

client = serpapi.Client(api_key=os.environ["SERPAPI_KEY"], timeout=15)
result = client.search({
    "engine": "google",
    "q": "coffee",
    "location": "Austin, Texas, United States",
    "hl": "en",
    "gl": "us",
})
assert result["search_metadata"]["status"] == "Success"
print({
    "search_id": result["search_metadata"]["id"],
    "organic_count": len(result.get("organic_results", [])),
})
```

## Resources

- [Google Search API](https://serpapi.com/search-api)
- [Status and error codes](https://serpapi.com/api-status-and-error-codes)
- [Official Python client](https://github.com/serpapi/serpapi-python)

## Next Steps

Capture a sanitized response fixture and move subsequent parser work into the local-development workflow.
