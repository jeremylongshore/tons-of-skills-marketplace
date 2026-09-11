---
name: serpapi-webhooks-events
description: 'Implement SerpAPI asynchronous searches and scheduled change detection without inventing a webhook callback contract. Use when building long-running searches or SERP monitoring. Trigger with "build SerpAPI async monitoring".'
argument-hint: "[engine] [poll-interval] [deadline]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, serpapi, async, monitoring, archive]
model: inherit
effort: high
compatibility: Designed for Claude Code; live async submission, polling, schedules, and downstream notifications require account and system-owner approval
---
# SerpAPI Async Search and Scheduled Monitoring

## Overview

Use documented async submission plus Searches Archive polling, or scheduled synchronous searches, with explicit state, budgets, and reconciliation.

## Prerequisites

- An engine and use case that justify background processing or repeated monitoring
- Poll deadline, schedule, allowance and throughput budgets, checkpoint store, and downstream owner
- Data classification, retention decision, and sanitized state-machine fixtures

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect jobs and consumers, `WebFetch` to verify async and archive contracts, and `Write` or `Edit` for state machines, schedules, checkpoints, fixtures, and redacted receipts.

## Current Contract

SerpAPI documents `async=true` to submit without holding the connection and the Searches Archive API to retrieve the search by ID. Status can move through queued or processing to success or error. `async` must not be combined with `no_cache` and is not for accounts with Ludicrous Speed. The public contract does not define a generic callback webhook for completed searches.

## Authentication

Use `SERPAPI_KEY` in the server-side submitter and poller. Persist search IDs and safe state, never key-bearing archive URLs. Authenticate and authorize any downstream notification endpoint using its own documented mechanism.

## Instructions

1. Confirm async is supported for the engine/account and that polling improves the use case over a bounded synchronous call.
2. Define states `SUBMITTED`, `QUEUED`, `PROCESSING`, `SUCCEEDED`, `FAILED`, `EXPIRED`, and `TIMED_OUT` with terminal behavior.
3. Submit with a parameter mapping containing `"async": true`; persist the search ID, normalized request hash, owner, deadline, and attempt budget.
4. Poll through the official client's archive method or documented archive endpoint with increasing delay, jitter, and a hard deadline.
5. On success, validate and normalize once; make downstream processing idempotent by search ID and payload version.
6. For scheduled monitoring, store snapshots and compare normalized business fields rather than unstable raw payload order.
7. Reconcile checkpoints, capacity consumption, missing terminal states, duplicates, late results, and notification failures.
8. Test every state transition with fixtures before enabling an approved live schedule.

## Approval Boundaries

Do not create a production schedule, send live searches, expose a notification endpoint, or mutate downstream records without named owners.

## Output

Return the selected sync/async mode, state machine, polling and search budgets, checkpoint schema, idempotency key, fixture results, schedule/canary receipt, and reconciliation outcome.

## Error Handling

| Condition | Response |
|---|---|
| Search remains queued/processing | Stop at the deadline and retain resumable state. |
| Archive returns 410 | Mark expired and require approval before submitting a replacement search. |
| Async is paired with `no_cache` | Reject the request locally. |
| Callback contract is requested | Use polling or obtain a current written vendor-specific contract; do not invent a webhook. |

## Example

```python
submitted = client.search({"engine": "google", "q": "coffee", "async": True})
search_id = submitted["search_metadata"]["id"]

while before_deadline():
    archived = client.search_archive(search_id=search_id)
    status = archived["search_metadata"]["status"]
    if status in {"Success", "Error"}:
        break
    wait_with_jitter()
```

## Resources

- [Google Search async parameter](https://serpapi.com/search-api#serpapi-parameters)
- [Searches Archive API](https://serpapi.com/searches-archive-api)
- [Official Python client](https://github.com/serpapi/serpapi-python)
- [Official JavaScript client](https://github.com/serpapi/serpapi-javascript)

## Next Steps

Canary one bounded async job and verify terminal-state, capacity, and checkpoint reconciliation before scheduling recurrence.
