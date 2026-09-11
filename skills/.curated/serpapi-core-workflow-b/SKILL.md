---
name: serpapi-core-workflow-b
description: 'Design a multi-engine SerpAPI workflow with explicit parameter maps, result adapters, budgets, and provenance. Use when combining Google, Bing, YouTube, News, Shopping, or Maps. Trigger with "build a SerpAPI multi-engine search".'
argument-hint: "[engines] [query] [result-limit]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.5.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, serpapi, multi-engine, youtube, maps]
model: inherit
effort: high
compatibility: Designed for Claude Code; every approved live engine request may affect account allowance and throughput
---
# SerpAPI Multi-Engine Search Workflow

## Overview

Model each engine as a distinct contract, then normalize only the fields needed for a cross-engine product.

## Prerequisites

- An explicit engine set, query intent, locale, data-use policy, and per-engine result needs
- Current engine documentation and sanitized fixtures
- A total search, latency, and concurrency budget

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to map engine consumers, `WebFetch` to verify each engine's current parameters and response sections, and `Write` or `Edit` for parameter maps, adapters, tests, and redacted receipts.

## Current Contract

Engine contracts are not interchangeable. Google, Bing, Google News, and Google Shopping accept `q`; YouTube uses `search_query`; Google Maps search uses `q` with `type=search` and can use `ll`. Common result sections include `organic_results`, `video_results`, `news_results`, `shopping_results`, and `local_results`, but their records have different shapes.

## Authentication

Supply `SERPAPI_KEY` only through the server-side gateway. Preserve engine and search ID for provenance, but strip the key and key-bearing URLs from normalized output.

## Instructions

1. List the approved engines and define the exact user value each contributes; remove redundant calls.
2. Re-fetch each engine's first-party API page and record its query, locale, pagination, safety, and result-section contract.
3. Build an allowlisted engine map rather than forwarding arbitrary client parameters.
4. Set per-engine timeouts, maximum records, concurrency, and total searches before execution.
5. Execute independently so one engine failure does not erase successful results from another.
6. Normalize to a tagged union retaining `engine`, `search_id`, source URL, rank, and engine-specific payload where required.
7. Test normal, empty-success, missing-section, partial-failure, and duplicate-source fixtures; report searches consumed by engine.

## Output

Return the engine contract table, request map, normalized tagged-union schema, partial-failure policy, budget, per-engine counts and search IDs, and fixture results.

## Error Handling

| Condition | Response |
|---|---|
| Wrong query parameter | Reject locally using the engine map. |
| One engine fails | Return an explicit partial result if policy allows; keep failure provenance. |
| Cross-engine duplicate | Retain source-engine ranks and apply a documented canonical-link policy. |
| Engine schema drifts | Quarantine only that engine's adapter and replay its fixture suite. |

## Example

```python
ENGINE_MAP = {
    "google": ("q", "organic_results"),
    "bing": ("q", "organic_results"),
    "youtube": ("search_query", "video_results"),
    "google_news": ("q", "news_results"),
    "google_shopping": ("q", "shopping_results"),
    "google_maps": ("q", "local_results"),
}

def build_request(engine, query):
    query_key, _ = ENGINE_MAP[engine]
    request = {"engine": engine, query_key: query}
    if engine == "google_maps":
        request["type"] = "search"
    return request
```

## Resources

- [SerpAPI integrations and engines](https://serpapi.com/integrations)
- [YouTube Search API](https://serpapi.com/youtube-search-api)
- [Google Maps API](https://serpapi.com/google-maps-api)
- [Bing Search API](https://serpapi.com/bing-search-api)

## Next Steps

Canary each engine separately, then enable the combined workflow within the aggregate search budget.
