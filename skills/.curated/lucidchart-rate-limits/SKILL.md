---
name: lucidchart-rate-limits
description: 'Design endpoint-specific Lucid request pacing, 429 handling, backpressure, and safe retry behavior. Use when hardening REST or connector traffic. Trigger with "handle Lucid rate limits".'
argument-hint: "[project-path] [operation-family]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, lucidchart, rate-limits, retries, reliability]
model: inherit
effort: medium
compatibility: Designed for Claude Code; production concurrency, replay, and load-test changes require service and resource-owner approval
---
# Lucid Rate-Limit and Backpressure Design

## Overview

Ground request control in the exact Lucid endpoint contract and observed responses. There is no justified pack-wide fixed requests-per-minute value.

## Prerequisites

- Inventory of operations, mutation semantics, concurrency, callers, and service objectives
- Current endpoint documentation and sanitized response headers/bodies
- Stable idempotency or reconciliation strategy for mutations

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect clients and tests, `WebFetch` for current endpoint/limit documentation, and `Write` or `Edit` only for local policy, code, tests, and receipts.

## Current Contract

Treat limits as endpoint/API-specific and time-sensitive. A legacy or Data API limit must not be generalized to document, export, import, Extension API, or connector operations. Server responses and current endpoint pages control.

## Authentication

Rate limiting does not justify credential pooling or scope expansion. Partition traffic by approved principal and tenant while keeping tokens out of metrics and logs.

## Instructions

1. Enumerate each operation's method, read/write effect, caller, principal, concurrency, and retry safety.
2. Re-fetch the exact operation and rate-limit documentation; record only explicitly documented values.
3. Instrument requests, success/error counts, latency, queue age, and safe server rate-limit/retry metadata.
4. Use bounded queues, per-operation concurrency, jitter, and backpressure before retries.
5. Retry only documented transient failures. For writes, require idempotency support or reconciliation before replay.
6. Honor documented `Retry-After` or equivalent server guidance when present; otherwise use conservative capped backoff based on observed behavior.
7. Test synthetic 429, timeout-before-response, partial batch, queue saturation, cancellation, and recovery.
8. Present any production concurrency or replay-policy change for approval and deploy as a monitored canary.

## Approval Boundaries

Do not increase production load, pool credentials, bypass queues, or replay ambiguous mutations without approval and reconciliation.

## Output

Return operation matrix, documented/unknown limits, observed response evidence, queue/retry policy, tests, approval, canary result, and remaining risks.

## Error Handling

| Condition | Response |
|---|---|
| Limit is undocumented | Mark unknown and design adaptive backpressure; do not invent a number. |
| Mutation timed out ambiguously | Reconcile before retrying. |
| Sustained 429s continue | Stop adding load, drain safely, and escalate with redacted evidence. |

## Example

```text
operation=document-create; published-limit=unknown; concurrency=2; 429-test=pass; ambiguous-write=reconcile
```

## Resources

- [Official documentation map](references/official-docs.md)

## Next Steps

Review observed traffic after the canary and tune only against verified endpoint evidence.
