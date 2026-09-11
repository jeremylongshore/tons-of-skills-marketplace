---
name: serpapi-sdk-patterns
description: 'Wrap the official SerpAPI Python or JavaScript client behind typed, testable boundaries with safe errors, pagination, and output selection. Use when production code needs a stable search adapter. Trigger with "design a SerpAPI client wrapper".'
argument-hint: "[python|typescript] [engine]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, serpapi, sdk, architecture, typescript]
model: inherit
effort: high
compatibility: Designed for Claude Code; live client verification requires a separately approved key and allowance
---
# SerpAPI Production Client Patterns

## Overview

Create a narrow application-owned gateway instead of spreading vendor parameters, credentials, and variable result schemas through business code.

## Prerequisites

- A selected official client and pinned dependency version
- Supported engines, required output fields, latency objective, and failure policy
- Sanitized fixtures for each supported response shape

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to map current call sites and types, `WebFetch` to verify official client interfaces, and `Write` or `Edit` for the gateway, schemas, fixtures, and tests.

## Current Contract

The Python client returns a `SerpResults` mapping and provides `next_page()` and `yield_pages()`. The JavaScript client exposes promise and callback forms including `getJson`, `getJsonBySearchId`, and `getAccount`, but does not provide built-in pagination. Search output can be JSON, HTML, or Markdown; `json_restrictor` can reduce JSON payload fields.

## Authentication

Inject `SERPAPI_KEY` at the outer server-side composition root. Do not include it in domain types, cache keys, error objects, telemetry, or serialized request parameters.

## Instructions

1. Define a request type that admits only supported engines and application-controlled locale, safety, pagination, and output options.
2. Define a normalized response type with explicit optional sections and vendor metadata isolated from domain data.
3. Inject the official client behind a small interface so fixtures can replace it without network interception.
4. Centralize timeouts, bounded retry for transient failures, 429 classification, redaction, and search-ID logging.
5. For Python, use `yield_pages()` only with a page/search budget; for JavaScript, implement engine-specific manual pagination from documented tokens or offsets.
6. Select JSON for structured parsing, Markdown for token-efficient agent consumption, HTML only for approved debugging, and `json_restrictor` when supported fields are known.
7. Add contract tests for empty-success, optional sections, processing/error states, pagination termination, timeout, and redaction.

## Output

Return request and response types, gateway code, client-version pin, pagination and retry budgets, output-selection rationale, fixture tests, and redaction evidence.

## Error Handling

| Condition | Response |
|---|---|
| Unknown engine or parameter | Reject locally before making a request. |
| Python `HTTPError` or `TimeoutError` | Map to a typed application error and preserve safe status/search metadata. |
| JavaScript rejection | Normalize the status and message without serializing request credentials. |
| Pagination budget reached | Return an explicit partial result and continuation state. |

## Example

```typescript
import { getJson } from "serpapi";

export async function searchGoogle(query: string) {
  const result = await getJson({
    engine: "google",
    q: query,
    api_key: process.env.SERPAPI_KEY,
    json_restrictor: "organic_results[].{position,title,link}",
  });
  return (result.organic_results ?? []).map(({ position, title, link }) => ({
    position, title, link,
  }));
}
```

## Resources

- [Official Python client](https://github.com/serpapi/serpapi-python)
- [Official JavaScript client](https://github.com/serpapi/serpapi-javascript)
- [JSON Restrictor](https://serpapi.com/json-restrictor)

## Next Steps

Exercise the gateway against sanitized fixtures, then canary one approved live request per supported engine.
