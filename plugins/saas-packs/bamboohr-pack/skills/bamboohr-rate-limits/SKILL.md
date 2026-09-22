---
name: bamboohr-rate-limits
description: >-
  Design bounded BambooHR retry, backpressure, and queue behavior from observed
  responses without inventing numeric quotas. Use when handling 429 or transient
  gateway failures, or preventing retry storms. Trigger with "BambooHR rate
  limit", "BambooHR 429", "BambooHR retry", or "BambooHR backoff".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<client-or-worker-path> [status-code]"
version: 1.5.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, hr, bamboohr, rate-limits, reliability]
model: inherit
effort: high
compatibility: Designed for Claude Code
---
# BambooHR Rate and Retry Control

## Overview

Protect the tenant, worker pool, and downstream systems with a finite retry
budget. BambooHR does not publish one universal numeric quota in the reviewed
official sources, so do not turn an observed limit into a product guarantee.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The tenant, identity, and data scope only when approved live work is in scope.
- The current evidence register plus customer-specific permissions and agreements.

## Current Contract

The official Python SDK retries HTTP 408, 429, 504, and 598 with exponential
delays beginning at 100 ms. Retry count is configurable from zero through five
and defaults to one. It exposes `RateLimitExceededException` and request IDs.
`503` is represented as service unavailable but is not in that documented
automatic-retry set.

## Authentication

Retries must reuse the same tenant-bound identity without logging or rebuilding
its token. If an OAuth token expires, permit one refresh workflow; do not count
repeated authentication failures as rate-limit retries.

## Instructions

1. Inventory every caller, concurrency source, scheduled sync, webhook replay,
   and manual job that shares the tenant identity.
2. Classify operations as read-only, idempotent with a key, conditionally safe,
   or unsafe to retry. Default mutations to no automatic retry.
3. On `429`, parse and honor a valid `Retry-After` value when present; otherwise
   use capped exponential backoff with jitter. Bound total attempts and elapsed time.
4. For `408`, `504`, or `598`, apply the same budget only to retry-safe work.
   Treat other failures according to explicit application policy, not by widening
   the SDK's documented set accidentally.
5. Centralize per-tenant concurrency and queue limits. Add a circuit breaker for
   sustained failures and spread scheduled full syncs.
6. Emit status class, request ID, attempt, selected delay, queue age, breaker
   state, and terminal disposition—never response bodies or credentials.
7. Test exact attempt counts, jitter bounds, `Retry-After`, elapsed-time cap,
   cancellation, restart persistence, and no-retry mutations.

## Tool Discipline

Use Read, Glob, and Grep to find retry loops and worker concurrency. Use
Write/Edit only for approved policy, instrumentation, and tests. This skill does
not send live requests or tune an account's BambooHR configuration.

## Approval Boundaries

Require approval before changing production concurrency, replaying queued HR
operations, or enabling retries for a mutation. Never retry an ambiguous write
until a read proves its current state.

## Output

Return operation classification, retryable statuses, max attempts and elapsed
budget, delay policy, `Retry-After` handling, concurrency/breaker design,
telemetry, test evidence, and live rollout boundary.

## Error Handling

- Invalid `Retry-After`: ignore the value, use the bounded fallback, and record it.
- Queue age exceeds business SLA: stop accepting work and surface degraded mode.
- Retry budget exhausted: dead-letter with request ID and safe context; do not loop.

## Examples

- "Retry all 503s forever" is rejected as unsupported and unsafe.
- "Handle 429s" produces a finite, tenant-scoped policy without a fabricated quota.

## Resources

Read [official evidence](references/official-docs.md) before changing retry policy.
