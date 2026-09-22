---
name: castai-rate-limits
description: 'Build a CAST AI REST client that respects endpoint-specific throttling, bounded retries, and an explicit request budget. Use when a job receives 429 responses, polls CAST AI, or fans out across clusters and organizations. Trigger with: "handle CAST AI rate limits", "stop CAST AI 429s", "make CAST AI polling safe".'
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[client-or-job-path]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - kubernetes
  - cast-ai
  - rate-limits
  - reliability
compatibility: 'Requires the current CAST AI API specification and observability for the client; limits vary by endpoint and upstream edge controls'
---

# CAST AI Request-Budget Control

## Overview

Treat rate capacity as an endpoint-specific runtime signal, not a single invented requests-per-second number. Bound concurrency, retries, polling, and total work while preserving correct authentication and organization scope.

## Prerequisites

- Client path, CAST AI region, organization scope, endpoints, and workload volume
- Current API specification and observed response headers
- Idempotency classification and business deadline for every operation

## Instructions

### Step 1: Inventory request producers

Use Read and Grep to identify direct API calls, Terraform operations, polling loops, scheduled jobs, retries, pagination, and per-cluster fan-out. Calculate worst-case attempts, not only successful requests.

### Step 2: Classify operations

Separate reads, idempotent updates, and non-idempotent mutations. Only retry operations whose semantics are proven safe. Keep auth failures, permission denials, malformed requests, and policy rejections outside the retry path.

### Step 3: Define the budget

Use Write or Edit to set per-endpoint concurrency, maximum attempts, maximum elapsed time, request timeout, queue capacity, and global job ceiling. Because CAST AI documents endpoint-dependent limits plus an upstream edge limiter, derive values from current specification and observed behavior.

### Step 4: Handle throttling

On 429, honor a valid server-provided delay signal when present; otherwise use capped exponential backoff with jitter. Coordinate workers through one limiter, stop adding retries after the deadline, and avoid synchronized polling at fixed boundaries.

### Step 5: Reduce demand

Cache stable reads within their acceptable staleness window, collapse duplicate requests, paginate deliberately, query only required organizations and clusters, and replace rapid status polling with a slower bounded schedule or documented notification path when suitable.

### Step 6: Test the failure envelope

Add deterministic tests for 429 with and without delay metadata, repeated 5xx, timeout, cancellation, queue overflow, deadline exhaustion, non-idempotent mutation, and mixed-region credentials. Assert no infinite loop and no duplicate unsafe mutation.

## Tool Discipline

Use Read and Grep for client and specification analysis. Use Write and Edit for limiter logic, tests, and operational documentation. This skill does not send live requests or guess undocumented quota values.

## Output

- Request inventory and idempotency map
- Endpoint-specific concurrency and retry budget
- Deterministic throttling and exhaustion tests
- Metrics for attempts, delay, queue depth, 429s, and dropped work

## Examples

A nightly collector shares one limiter across cluster workers and stops at its batch deadline. A policy mutation returns 429 but is not replayed until its idempotency contract is established.

## Error Handling

| Failure                         | Response                                                   |
| ------------------------------- | ---------------------------------------------------------- |
| No endpoint limit is documented | Start conservatively and calibrate from observed responses |
| Delay metadata exceeds deadline | Fail with a resumable checkpoint                           |
| Queue reaches its bound         | Shed or defer low-priority work                            |
| Mutation outcome is unknown     | Reconcile state before any retry                           |

## Resources

- [Rate-control evidence and source notes](references/official-docs.md)
- [CAST AI API FAQ](https://docs.cast.ai/docs/api)
- [API access](https://docs.cast.ai/docs/api-access)
- [CAST AI API specification](https://api.cast.ai/spec/)
