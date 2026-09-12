---
name: firecrawl-reliability-patterns
description: >-
  Implement bounded retries, durable async state, pagination, idempotency, reconciliation, circuit breaking, cancellation, and degraded modes for Firecrawl v2. Use when hardening a production integration. Trigger with "Firecrawl reliability", "Firecrawl retries", or "resilient Firecrawl".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<repository-path> <operation>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, firecrawl, reliability, resilience]
model: inherit
effort: high
compatibility: "Designed for Claude Code; Firecrawl Cloud work requires network access"
---
# Firecrawl Reliability Controls

## Overview

Make every unit of work recoverable without duplicate collection or downstream writes. Provider retry, client retry, queue replay, webhook redelivery, and operator replay must share one idempotency model.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The source authorization, data classification, and environment policy.
- Current Firecrawl documentation, credentials only when needed, and an owner for approvals.

## Current Contract

Only errors classified retryable by Firecrawl's current error catalog should enter automatic backoff. Async crawl, batch, agent, and related jobs require durable IDs and terminal-state handling; crawl and batch results may paginate. Webhooks retry delivery on their schedule, while status reconciliation remains necessary after missed or exhausted delivery.

## Authentication

For authenticated Cloud operations, inject FIRECRAWL_API_KEY from an approved
secret manager. REST requests use Authorization: Bearer with the key. Never print,
commit, transmit, or place a key in a URL. Keyless access is suitable only where
the current documentation explicitly allows it and the workload accepts its
limits; production workflows should make identity and team ownership explicit.

## Instructions

1. Define a stable work identity from tenant, approved source, operation, policy version, and requested version; store attempts and downstream state durably.
2. Separate submission from completion. Persist the provider job ID before acknowledging work and resume status/pagination from durable state.
3. Classify validation, authentication, credits, restrictions, origin responses, rate/concurrency, timeouts, server failures, and downstream errors independently.
4. Retry only documented retryable classes with jitter, Retry-After, maximum attempts, total deadline, and a circuit breaker. Never rotate keys to evade limits.
5. Make page acceptance, storage, indexing, webhook handling, and tombstones idempotent. Deduplicate webhook deliveries by webhookId plus event context.
6. Reconcile provider job state, all result pages, accepted/rejected totals, downstream receipts, and spend on a schedule; cancel abandoned work where safe.
7. Exercise crash-after-submit, crash-after-write, duplicate webhook, partial pagination, provider outage, stale cache, and rollback in tests.

## Tool Discipline

Use Read, Glob, and Grep to inspect code, configuration, tests, and evidence. Use
Write/Edit only for approved implementation or documentation changes. Do not call
Firecrawl, rotate keys, change account settings, scrape a target, or deploy merely
because this skill was invoked.

## Approval Boundaries

Require approval before expanding retry budgets, replaying production jobs, cancelling shared work, using stale data as a degraded mode, or bypassing a circuit breaker.

## Output

Return the state machine, idempotency keys, retry matrix, circuit and backpressure policy, reconciliation algorithm, degraded modes, test results, and recovery/rollback receipt.

## Error Handling

- Job ID was not persisted: search only through approved evidence; do not submit a duplicate blindly.
- Pagination is incomplete: mark the result partial and withhold completeness claims.
- Provider and downstream state cannot reconcile: stop automated replay and escalate with redacted evidence.

## Examples

- "Make crawl jobs restartable" persists job and pagination state before acknowledgment.
- "Retry every failure forever" is replaced with documented classes, deadlines, and a circuit breaker.

## Resources

Read [official Firecrawl evidence](references/official-docs.md) before relying on
an endpoint, SDK method, plan limit, price, retention option, or self-hosted release.
