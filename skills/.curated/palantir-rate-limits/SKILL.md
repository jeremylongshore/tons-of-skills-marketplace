---
name: palantir-rate-limits
description: >-
  Analyze and design bounded Foundry API concurrency, backoff, pagination, and overload behavior from current documented limits. Use when preventing or handling HTTP 429 or 503 responses. Trigger with "Palantir rate limit".
allowed-tools: Read,Glob,Grep,Write,Edit
version: 2.0.0
argument-hint: "[client-or-endpoint]"
model: inherit
effort: high
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Requires current Palantir Foundry documentation and approved access for any live resource, permission, data, build, application, or deployment change
tags: [saas, palantir, foundry, rate-limits, reliability]
---
# Palantir API Limit and Concurrency Control

## Overview

Protect Foundry and the caller from retry storms. Budget requests across the acting user, bound concurrent work, honor server responses, and distinguish retryable throttling from authorization, validation, or permanent resource errors.

## Prerequisites

- Identify the acting user or service user, applications sharing it, endpoints, workload peaks, page/batch shape, and service objective.
- Capture response status, request identifiers, timestamps, server timing guidance, retry count, and current concurrency.
- Read `references/official-docs.md` immediately before setting numeric budgets because effective and endpoint-specific limits may change.
- Prepare load tests in an approved non-production scope.

## Current Contract

- The current general API documentation lists global per-user rate and concurrency limits across Foundry API endpoints.
- Individual endpoints may impose stricter limits and return `429` or `503`.
- Palantir recommends exponential backoff for throttled requests.
- Limits can vary in practice, and disruptive throttling may require Palantir Support rather than client-side limit evasion.

## Authentication

Attribute the request budget to the actual OAuth principal. Do not distribute calls across extra tokens, users, or service users to evade a limit. Keep token material out of metrics and retry logs.

## Instructions

1. Inventory every worker and application using the same principal and estimate peak request rate plus in-flight concurrency.

2. Set a conservative shared concurrency budget and bounded queue with deadlines and cancellation.

3. Retry only documented transient statuses, honoring server guidance and using capped exponential backoff with jitter.

4. Use pagination, selective properties, batching supported by the endpoint, idempotency controls, and workload coalescing to reduce demand.

5. Load-test below the approved ceiling, simulate `429` and `503`, and verify recovery without duplicate writes or unbounded backlog.

## Tool Discipline

- Use **Glob** to locate candidate repositories, manifests, configurations, and evidence without widening scope.
- Use **Grep** to find relevant identifiers, declarations, permissions, errors, and stale claims.
- Use **Read** to inspect the smallest required files and authoritative evidence.
- Use **Write** only for a new approved local draft, test, manifest, or evidence artifact.
- Use **Edit** only for a bounded approved change whose rollback is known.
- Do not use file tools as a substitute for authenticated Foundry operations or owner approval.

## Approval Boundaries

Application owners approve budgets and degradation; platform owners approve load tests; data owners approve any write retry or batch behavior. Creating principals to bypass limits is prohibited.

## Output

A principal-level request inventory, endpoint budgets, concurrency and queue design, retry matrix, idempotency rules, test evidence, alert thresholds, and support escalation criteria.

## Error Handling

| Condition | Response |
|---|---|
| A non-retryable 4xx is retried | Stop and route it to validation, authentication, authorization, or resource triage. |
| Queue age exceeds the service objective | Reject or degrade work according to policy instead of accumulating unbounded backlog. |
| Retries duplicate a write | Disable automatic retry until idempotency or reconciliation is proven. |
| Throttling persists below the expected budget | Check shared-principal traffic and endpoint limits, preserve request IDs, and contact Palantir Support. |

## Examples

### Example 1

Coordinate several workers under one client-credentials service user with a shared semaphore, bounded queue, capped jittered backoff, and metrics for `429`, `503`, in-flight requests, and queue age.

### Example 2

Make an object reader cheaper and safer by selecting required properties, paging deterministically, cancelling expired work, and lowering concurrency before increasing retries.

## Validation

- Request and concurrency budgets are enforced across all users of the principal.
- Retry attempts and elapsed time have hard bounds.
- Write operations are idempotent or reconciled before retry.
- Load tests recover from throttling without a storm or duplicate side effects.
- Alerts identify principal, endpoint, queue age, and request IDs without exposing tokens.

## Resources

- [Official documentation and contract notes](references/official-docs.md)
- Re-check the dated contract before any live operation.
- Treat unresolved or changed vendor behavior as a stop condition.
