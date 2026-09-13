---
name: procore-rate-limits
description: >-
  Implement adaptive Procore throttling from response headers across spike, hourly, and heavy-load conditions. Use when handling 429 or 503 responses, sizing concurrency, or protecting webhook backlogs. Trigger with: "handle Procore rate limits", "fix Procore 429", "throttle Procore workers".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[worker-and-request-class]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - procore
  - rate-limits
  - resilience
compatibility: 'Requires access to Procore response headers and a queue or scheduler capable of pausing and bounding concurrency.'
---

# Procore Header-Driven Rate Controller

## Overview

Control throughput from the headers on each response instead of a hard-coded request count. Procore exposes whichever spike or hourly window is most likely to bind, and failed requests consume the same budget as successful calls.

## Prerequisites

- Central request dispatcher with observable worker concurrency
- Durable queue and a clock synchronized well enough to interpret reset timestamps
- Metrics for status, route, remaining budget, reset time, retries, and backlog age

## Instructions

### Step 1: Capture every budget signal

Record `X-Rate-Limit-Limit`, `X-Rate-Limit-Remaining`, and `X-Rate-Limit-Reset` from each response. Preserve `Retry-After` for heavy-load responses.

### Step 2: Pace before exhaustion

Reduce dispatch concurrency as remaining budget falls and pause when it reaches zero. Treat the current headers as authoritative for either the spike or hourly window.

### Step 3: Handle throttling

On 429, wait until after the reported reset and add jitter before resuming. On 503, obey `Retry-After`; never substitute an assumed delay.

### Step 4: Bound retries

Retry safe reads within a capped policy. For writes, reconcile outcome or require an operation-specific idempotency design before another attempt.

### Step 5: Protect event backlogs

Acknowledge webhook notifications quickly, enqueue downstream reads, and let the controller drain them. Monitor oldest-event age as well as queue depth.

### Step 6: Prove recovery

Test low-budget, exhausted-budget, 429, and 503 fixtures. Verify one worker cannot bypass the shared controller and that recovery does not release a synchronized surge.

## Authentication

Requests retain their existing OAuth 2.0 Bearer token and company routing. Throttling must not acquire alternate credentials to evade a rate boundary or log tokens alongside rate metadata.

## Tool Discipline

Use Read and Grep to inspect dispatcher code, metrics, and provider headers. Use Write or Edit only for the approved limiter, queue policy, tests, or receipt; do not generate live load as a rate-limit test.

## Output

- Header-driven pacing and retry policy
- Deterministic limit and recovery tests
- Route-level budget, backlog, and failure metrics

Return the observed headers, controller decision, retry eligibility, next dispatch time, and verification outcome.

## Examples

When remaining budget reaches zero, all workers stop until the reported reset plus jitter. A 503 follows its Retry-After value, while an ambiguous write is reconciled rather than replayed with the safe-read policy.

## Error Handling

| Failure | Response |
| --- | --- |
| Rate headers missing | Reduce concurrency conservatively and surface telemetry loss; do not invent a limit. |
| 429 repeats after reset | Increase jitter, lower concurrency, and inspect failed-call volume. |
| Queue age breaches objective | Shed optional work and prioritize reconciliation without bypassing the limit. |
| Write retry safety is unknown | Stop automatic retries and reconcile provider state. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Rate limiting](https://developers.procore.com/documentation/rate-limiting)
- [API Call Activity Report](https://developers.procore.com/documentation/api-activity-export)
- [Error code reference](https://developers.procore.com/documentation/error-reference)
