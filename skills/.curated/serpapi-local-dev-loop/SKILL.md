---
name: serpapi-local-dev-loop
description: 'Build and test SerpAPI integrations locally with sanitized fixtures, injected clients, and an explicit live-recording boundary. Use when developing parsers without repeatedly spending allowance. Trigger with "set up SerpAPI local development".'
argument-hint: "[python|typescript] [parser-path]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit, Bash(python3:*), Bash(npm:*)
version: 1.5.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, serpapi, local-development, fixtures, testing]
model: inherit
effort: medium
compatibility: Designed for Claude Code; recording a fresh fixture is a live search and requires approval
---
# SerpAPI Fixture-First Local Development

## Overview

Separate deterministic parsing from live search acquisition so everyday development is fast, private, and allowance-free.

## Prerequisites

- A target engine, parameter contract, parser behavior, and repository test framework
- One approved sanitized response per important schema variant
- A policy for fixture review, retention, refresh, and sensitive-field removal

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to locate clients, parsers, fixtures, and tests, `WebFetch` to re-check engine schemas, `Write` or `Edit` for adapters and fixtures, and `Bash(python3:*)` or `Bash(npm:*)` for local tests or an explicitly approved recorder.

## Current Contract

SerpAPI response sections vary by engine, query, geography, device, and upstream search layout. The official Python result is a `SerpResults` mapping; application code should depend on a narrow local adapter rather than a captured response being universal.

## Authentication

Offline tests must not require `SERPAPI_KEY`. Load the key only inside a separately invoked recorder, refuse sentinel or missing values, and never serialize request URLs or metadata fields that reveal it.

## Instructions

1. Inventory every consumed field and classify it as required, optional, engine-specific, or derived.
2. Create a client interface whose search method can be replaced by a fixture-backed fake.
3. Sanitize fixtures by removing key-bearing URLs, raw HTML links, account identifiers, sensitive queries, and unrelated result content.
4. Add fixtures for normal, empty-success, processing, error, missing optional section, and changed-type cases.
5. Write parser tests against the fixtures and assert normalized application output rather than the entire vendor payload.
6. Put live recording behind a separate command, explicit environment flag, allowance check, and operator approval.
7. When refreshing, review semantic diffs, update the retrieval date and source engine, and rerun all offline tests.

## Output

Return the client seam, fixture inventory and sanitization record, offline test results, live-recording command and guard, consumed-field contract, and refresh owner.

## Error Handling

| Condition | Response |
|---|---|
| Fixture contains a key-bearing URL | Remove it, rotate the exposed key if necessary, and inspect history. |
| Parser fails on a missing section | Make the branch explicit or prove the section is contractually required. |
| Live call occurs in an offline test | Fail the test and replace the client at the network boundary. |
| Fixture is stale | Refresh once under approval and review the schema delta. |

## Example

```python
class SearchGateway:
    def __init__(self, client):
        self.client = client

    def titles(self, params):
        response = self.client.search(params)
        return [item["title"] for item in response.get("organic_results", [])]

class FixtureClient:
    def __init__(self, response):
        self.response = response

    def search(self, _params):
        return self.response
```

## Resources

- [Official Python client](https://github.com/serpapi/serpapi-python)
- [Google Search JSON results](https://serpapi.com/search-api#api-examples)
- [Status and error codes](https://serpapi.com/api-status-and-error-codes)

## Next Steps

Wire the same fixture suite into CI and reserve live validation for a protected workflow.
