---
name: serpapi-rate-limits
description: 'Discover SerpAPI account throughput and allowance dynamically, then enforce admission, concurrency, and retry budgets. Use when preventing 429s or coordinating search workers. Trigger with "configure SerpAPI rate limits".'
argument-hint: "[environment] [worker-count]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit, Bash(python3:*)
version: 1.5.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, serpapi, rate-limits, quotas, reliability]
model: inherit
effort: high
compatibility: Designed for Claude Code; capacity checks require account authorization and production concurrency changes require operator approval
---
# SerpAPI Capacity and Rate-Limit Control

## Overview

Use the account's live contract as the source of truth instead of embedding plan names or numeric limits in code.

## Prerequisites

- Workload arrival rate, burst size, latency objective, search budget, and job priority
- Access to the Account API and ownership of all workers sharing the key
- Metrics for attempts, successes, cached results, 429s, latency, and searches left

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inventory producers and retry loops, `WebFetch` to verify current Account API and status semantics, `Write` or `Edit` for admission controls and observability, and `Bash(python3:*)` for an approved capacity check or load simulation.

## Current Contract

Account API returns fields including `plan_searches_left`, `total_searches_left`, `this_hour_searches`, and `account_rate_limit_per_hour`. HTTP 429 can mean the hourly throughput limit was exceeded or the account ran out of searches, so the response alone does not identify the remedy.

## Authentication

Use a server-side `SERPAPI_KEY` for Account API and search calls. Centralize capacity across every workload sharing that credential; do not expose account fields or the key through a public health endpoint.

## Instructions

1. Enumerate every producer, schedule, priority, concurrency setting, retry policy, and credential-sharing boundary.
2. Read current account capacity and renewal facts from Account API; treat configured limits as refreshable state.
3. Reserve headroom for interactive and incident traffic and translate the remaining capacity into per-worker admission budgets.
4. Apply a shared concurrency limiter and queue; reject or defer low-priority work before sending excess requests.
5. On 429, pause new admissions, refresh Account API, then classify throughput exhaustion versus search exhaustion.
6. Retry only when the classification and reset policy justify it; cap attempts and add jitter to avoid synchronized bursts.
7. Load-test with a fake client, canary below the account ceiling, and alert on capacity burn rate and sustained 429s.

## Output

Return the producer inventory, live capacity snapshot, admission and concurrency budgets, 429 decision tree, retry policy, test evidence, alerts, and rollback owner.

## Error Handling

| Condition | Response |
|---|---|
| Account API unavailable | Fail closed to a conservative cached budget with an expiry. |
| Throughput exhausted | Pause and drain; do not amplify with immediate retries. |
| Searches exhausted | Stop allowance-consuming work and route to the account owner. |
| Multiple uncoordinated workers | Introduce a shared limiter before increasing parallelism. |

## Example

```python
account = client.account()
hourly_limit = int(account["account_rate_limit_per_hour"])
used_this_hour = int(account["this_hour_searches"])
headroom = max(0, hourly_limit - used_this_hour)
admission_budget = max(0, int(headroom * 0.8))  # reserve 20% for priority traffic
```

## Resources

- [Account API](https://serpapi.com/account-api)
- [Status and error codes](https://serpapi.com/api-status-and-error-codes)
- [Plans and pricing](https://serpapi.com/pricing)

## Next Steps

Review the live capacity at renewal and whenever a new worker or search product begins sharing the account.
