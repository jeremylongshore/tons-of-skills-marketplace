---
name: attio-rate-limits
description: >-
  Analyze and design an Attio request governor with separate read and write budgets, query-score awareness, bounded retries, and observable backpressure. Use when an Attio integration receives 429 responses or needs safe concurrency controls. Trigger with "Attio rate limits", "Attio 429", or "throttle Attio requests".
argument-hint: "[repository-path] [workload-or-endpoint]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- attio
- reliability
model: inherit
effort: high
compatibility: Designed for Claude Code
---
# Attio Rate-Limit Governor

## Overview

This skill turns Attio's current published limits into a conservative client policy without treating the documented ceilings as reserved capacity.

## Prerequisites

- Request metrics split by workspace, method, and endpoint
- Queue depth, retry count, and 429 response samples
- The endpoint-specific pagination and query contract
- An agreed maximum retry age and failure budget

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect concurrency, queues, retries, and pagination. Use `WebFetch` only to recheck current official Attio limits and response semantics. Use `Write` or `Edit` after the governor policy and rollback threshold are explicit.

## Current Contract

- Attio currently publishes global ceilings of 100 read requests per second and 25 write requests per second.
- Record and entry query endpoints also use a score budget over a 10-second window; complex filters and sorts consume more score.
- A 429 response can include `Retry-After` as an HTTP date, so do not assume an integer delay.
- Limits can change and are shared with other workspace traffic; reverify the official guide before rollout.

## Authentication

Keep the existing least-privilege Bearer token and partition governor state by workspace credential. Never expose tokens in rate-limit telemetry.

## Instructions

1. Inventory calls by read, write, workspace, endpoint, and query shape.
2. Reverify the official limits and endpoint-specific query scoring.
3. Implement separate conservative read and write token buckets below the published ceilings.
4. Add per-workspace queues, bounded concurrency, jitter, and backpressure.
5. On 429, parse `Retry-After` as an HTTP date when present; otherwise use capped exponential backoff.
6. Retry only idempotent or explicitly idempotency-protected work and only for 429 or eligible transient 5xx responses.
7. Load-test below production limits and record throughput, tail latency, queue age, and retry amplification.

## Approval Boundaries

Do not increase concurrency, replay non-idempotent writes, or drop queued work without the service owner's approval and a rollback plan.

## Output

Return verified limits, queue partitions, bucket settings, retry eligibility, maximum retry age, load-test evidence, and rollback thresholds.

## Error Handling

| Condition | Response |
|---|---|
| `Retry-After` is malformed | Use capped jittered backoff and preserve the response evidence. |
| Low request count still gets 429 | Inspect query score and other traffic sharing the workspace. |
| Queue age exceeds its objective | Shed optional work or pause producers; do not burst harder. |
| Write result is ambiguous | Reconcile state before any retry. |

## Examples

Input:

```text
workload=record queries plus writes; symptom=429 bursts; scope=one workspace
```

Expected handoff:

```text
governor=split read/write; retry=http-date aware; load-test=pass; rollback=defined
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Rate limiting](https://docs.attio.com/rest-api/guides/rate-limiting)
- [Pagination](https://docs.attio.com/rest-api/guides/pagination)
