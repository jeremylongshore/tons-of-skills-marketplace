---
name: serpapi-core-workflow-a
description: 'Build a reproducible Google Search workflow that validates parameters, optional result sections, and bounded pagination. Use when implementing search, SEO monitoring, or evidence collection. Trigger with "build a SerpAPI Google workflow".'
argument-hint: "[query] [location] [page-budget]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, serpapi, google-search, pagination, seo]
model: inherit
effort: high
compatibility: Designed for Claude Code; live searches and multi-page retrieval consume account allowance unless a matching server cache is served
---
# SerpAPI Google Search Workflow

## Overview

Turn a search question into a bounded, reproducible Google Search request and normalize only the result sections the application actually needs.

## Prerequisites

- A business question, permitted query class, geography, language, device, and freshness target
- An authenticated official client behind a server-side gateway
- A search/page budget and fixtures for expected optional sections

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect call sites and result consumers, `WebFetch` to verify current Google parameters and schemas, and `Write` or `Edit` for request builders, normalizers, tests, and redacted receipts.

## Current Contract

Google Search uses `engine=google` and `q`. Locale and device inputs include `location`, `hl`, `gl`, and `device`; pagination commonly uses `start`. JSON sections such as `organic_results`, `answer_box`, `knowledge_graph`, `related_questions`, and local results are query-dependent and optional.

## Authentication

The server-side gateway supplies `SERPAPI_KEY`. Exclude the key and key-bearing URLs from application output, cache keys, logs, telemetry, fixtures, and error reports.

## Instructions

1. Convert the business question into a minimal query and document permitted use, location, language, device, safe-search setting, freshness, and requested fields.
2. Validate parameters against the current Google Search API rather than copying options from another engine.
3. Estimate the maximum searches, check the account budget, and present the live execution boundary.
4. Execute the first page and require a terminal `Success` or `Error` status before parsing sections.
5. Normalize each required section independently and retain provenance fields such as position, source link, and search ID.
6. Follow `serpapi_pagination.next` or a documented `start` offset only while results continue and the page budget remains.
7. Reconcile counts, deduplicate stable links, test empty and missing-section fixtures, and store a redacted receipt.

## Output

Return normalized parameters, result-section schema, requested records with provenance, pages and searches consumed, termination reason, search IDs, and fixture coverage.

## Error Handling

| Condition | Response |
|---|---|
| `Success` without `organic_results` | Inspect documented alternative sections and result-state fields. |
| Location is not resolved as intended | Use a canonical location from the Locations API and record the resolved value. |
| Page has no continuation | Stop successfully; never synthesize the next offset blindly. |
| Schema changes | Quarantine the response, update the narrow adapter and fixture, then replay offline. |

## Example

```python
params = {
    "engine": "google",
    "q": "site:example.com release notes",
    "location": "Austin, Texas, United States",
    "hl": "en",
    "gl": "us",
    "safe": "active",
}
result = client.search(params)
if result["search_metadata"]["status"] != "Success":
    raise RuntimeError(result.get("error", "search did not complete"))
records = [
    {"position": row.get("position"), "title": row.get("title"), "link": row.get("link")}
    for row in result.get("organic_results", [])
]
```

## Resources

- [Google Search API](https://serpapi.com/search-api)
- [Locations API](https://serpapi.com/locations-api)
- [Status and error codes](https://serpapi.com/api-status-and-error-codes)

## Next Steps

Freeze the normalized schema in fixtures and set a page budget appropriate to the product use case.
