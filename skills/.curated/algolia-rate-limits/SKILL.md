---
name: algolia-rate-limits
description: >-
  Monitor and optimize Algolia request pressure using observed responses and bounded client behavior. Use when requests return 429, queues grow, or search and indexing compete for capacity. Trigger with "Algolia rate limit", "Algolia 429", or "throttle indexing".
argument-hint: "[repository-path] [operation]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- algolia
- reliability
model: inherit
effort: medium
compatibility: Designed for Claude Code
---
# Algolia Rate-Pressure Handling

## Overview

This skill avoids invented universal quotas. It distinguishes key restrictions, current contractual usage, indexing pressure, transient transport failures, and application amplification using actual response evidence.

## Prerequisites

- A named repository, environment, and Algolia application or index in scope
- The local lockfile and installed client types as implementation authority
- A safe read-only query or explicitly disposable test target
- Current first-party documentation for any provider behavior that affects the change

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect local code, configuration names, tests, and dependency versions. Use `WebFetch` only for current official Algolia documentation. Use `Write` or `Edit` only after identifying the target files, constraints, and verification plan.

## Current Contract

- Interpret a 429 from its status, message, operation, request ID, and current account terms.
- Inspect installed client behavior before layering application retries on top of SDK host retry.
- Bound attempts, elapsed time, concurrency, and queue depth; retry only operations whose semantics are safe.
- Protect interactive search from batch indexing through workload scheduling and backpressure.

## Authentication

Use operation-specific, least-privilege keys. Never raise limits by replacing a restricted key with an Admin key or by removing tenant safeguards.

## Instructions

1. Capture the failing operation, response, request ID, client version, concurrency, queue depth, and traffic source.
2. Check key restrictions and current usage or contract evidence without assuming a fixed quota.
3. Identify amplification from duplicate clients, unbounded concurrency, retries, bots, or oversized batches.
4. Define a retry budget with eligible errors, maximum attempts, elapsed timeout, jitter, and cancellation.
5. Apply concurrency limits or scheduling at the producer and test partial failure and shutdown.
6. Verify search health, queue recovery, idempotency, and alerting under controlled pressure.

## Approval Boundaries

Do not load-test production, remove rate restrictions, increase plan limits, or retry non-idempotent work without owner approval.

## Output

Return the observed limit evidence, pressure source, retry and queue policy, test results, residual capacity risk, and any commercial decision requiring an account owner.

## Error Handling

| Condition | Response |
|---|---|
| 429 message ambiguous | Retain request ID and consult current provider support or docs. |
| Retry storm begins | Open the circuit and drain or shed work. |
| Queue exceeds bound | Stop producers and preserve work for controlled replay. |
| Plan change proposed | Separate the commercial approval from the technical fix. |

## Examples

Use this compact input and expected handoff to calibrate scope and evidence quality.

Input:

```text
operation=saveObjects; status=429; concurrency=40; sdk=5.59.0
```

Expected handoff:

```text
cause=producer-amplification; concurrency=4; retry-budget=bounded; recovery=verified
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [API keys](https://www.algolia.com/doc/guides/security/api-keys)
- [JavaScript API client](https://www.algolia.com/doc/libraries/javascript)
- [Usage API](https://www.algolia.com/doc/rest-api/usage)
