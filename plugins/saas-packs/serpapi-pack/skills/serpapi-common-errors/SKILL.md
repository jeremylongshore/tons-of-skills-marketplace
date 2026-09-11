---
name: serpapi-common-errors
description: 'Classify SerpAPI HTTP failures, search-status failures, and valid empty results before choosing a retry or repair. Use when searches fail, stall, or return unexpected shapes. Trigger with "diagnose a SerpAPI error".'
argument-hint: "[status-code|search-id] [engine]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit, Bash(python3:*)
version: 1.5.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, serpapi, troubleshooting, errors, reliability]
model: inherit
effort: high
compatibility: Designed for Claude Code; live reproduction and archive access require an authorized key and may affect allowance
---
# SerpAPI Error Classification and Recovery

## Overview

Diagnose the transport, account, search, engine, and application layers separately so retries do not hide configuration or quota failures.

## Prerequisites

- HTTP status, safe error text, engine, normalized parameters, client version, and timestamp
- Search ID and `search_metadata.status` when a response was created
- Account owner approval before any live reproduction

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to trace request construction and parsing, `WebFetch` to verify current error semantics, `Write` or `Edit` for fixes and redacted evidence, and `Bash(python3:*)` only for an approved diagnostic using the official client.

## Current Contract

SerpAPI uses conventional statuses: 400 for invalid requests, 401 for invalid authentication, 403 for forbidden accounts, 404 for missing resources, 410 for expired archive searches, 429 for either hourly throughput or exhausted searches, and 500/503 for server failures. Search status can be `Queued`, `Processing`, `Success`, or `Error`; `Success` can contain empty results.

## Authentication

Keep `SERPAPI_KEY` out of exceptions and captured request URLs. Use the Account API to classify 429 responses, and share only redacted request metadata or search IDs with support.

## Instructions

1. Capture the HTTP status, response `error`, search status, search ID, engine, safe parameter names, and client timeout.
2. Determine whether failure occurred before search creation, during queued/processing work, after a terminal error, or in local parsing.
3. For 400, compare parameters with the selected engine documentation and fix locally without retrying unchanged.
4. For 401/403, stop and repair account access; for 429, query Account API to separate throughput from allowance.
5. Retry timeouts and 500/503 only with a small attempt budget, exponential backoff, jitter, and idempotent processing.
6. Treat terminal `Success` with empty sections as data, then inspect documented engine-specific `_state` fields.
7. Add a sanitized regression fixture and record the classification, fix, retry count, and final state.

## Output

Return the failure layer, status and search ID, retryability decision, evidence, corrective change, regression fixture, final state, and support escalation data.

## Error Handling

| Signal | Action |
|---|---|
| 400 | Correct parameters; no unchanged retry. |
| 401/403 | Stop; repair authorization or account state. |
| 410 | Re-run only with approval because the archive record expired. |
| 429 | Inspect account throughput and searches left before waiting or changing plan. |
| 500/503 or timeout | Retry within budget; escalate persistent failures with search IDs. |

## Example

```python
try:
    result = client.search(params)
except serpapi.HTTPError as exc:
    if exc.status_code in {400, 401, 403}:
        raise PermanentSearchError(exc.status_code) from exc
    if exc.status_code == 429:
        raise CapacityDecisionRequired() from exc
    raise TransientSearchError(exc.status_code) from exc
```

## Resources

- [Status and error codes](https://serpapi.com/api-status-and-error-codes)
- [Account API](https://serpapi.com/account-api)
- [SerpAPI status](https://status.serpapi.com/)

## Next Steps

Keep the new fixture in the offline suite and review retry metrics after the next production window.
