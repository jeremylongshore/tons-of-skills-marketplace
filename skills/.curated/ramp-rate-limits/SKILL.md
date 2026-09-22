---
name: ramp-rate-limits
description: >-
  Implement a shared Ramp request budget with rolling-window throttling, bounded retries, pagination, and 504 recovery. Use when clients receive 429 or 504 responses or share one outbound IP. Trigger with "Ramp rate limit" or "Ramp 429".
allowed-tools: Read,Glob,Grep,Write,Edit
version: 2.0.0
argument-hint: "[integration-or-environment]"
model: inherit
effort: high
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Requires current Ramp Developer API documentation and approved access for any live financial, card, identity, accounting, application, or configuration change
tags: [saas, ramp, rate-limits, retries, resilience]
---
# Ramp Rate-Limit and Timeout Control

## Overview

Coordinate all workers that share an egress IP, because independent per-process retries can amplify a rolling-window breach. Preserve idempotency and reconcile ambiguous writes before retry.

## Prerequisites

- Identify the Ramp application, environment, business entities, affected data and workflows, accountable owner, and rollback boundary.
- Read `references/official-docs.md` and re-check endpoint schemas, scopes, limits, and support status before a live operation.
- Use synthetic fixtures or Ramp sandbox until production access and business effects are explicitly approved.
- Prepare approved secret storage and a sanitized evidence location.

## Current Contract

- Ramp currently documents a default limit of 200 requests per rolling 10-second window per source IP.
- A 429 means pause and back off; immediate retries worsen contention.
- Requests taking longer than 60 seconds terminate with 504, so large reads should be paginated and work units reduced.
- Ramp recommends exponential backoff; actual throughput is lower than theoretical throughput and endpoint constraints still apply.

## Instructions

1. Inventory all services, jobs, tenants, endpoints, and retry layers sharing each source IP; measure arrival rate, burst, latency, 429/504, and business priority.

2. Implement one shared rolling-window limiter below the documented ceiling, with reserved capacity for interactive or recovery traffic.

3. Use bounded exponential backoff with full jitter for 429, 5xx, and safe 504 cases; cap attempts and total elapsed time.

4. Retry reads freely within budget, but retry writes only with an endpoint-supported idempotency key and post-timeout reconciliation.

5. Reduce pages or query scope for 504s, canary concurrency changes, and request a vendor increase only with measured demand and completeness evidence.

## Tool Discipline

- Use **Glob** to locate candidate code, manifests, fixtures, and evidence without widening scope.
- Use **Grep** to find relevant endpoints, fields, permissions, identifiers, errors, and stale assumptions.
- Use **Read** to inspect the smallest required local files and authoritative evidence.
- Use **Write** only for a new approved local draft, test, configuration, or evidence artifact.
- Use **Edit** only for a bounded approved change with a known rollback.
- Local file tools do not authorize a Ramp operation or replace owner approval.

## Approval Boundaries

Platform owners approve budgets and retry policy; business/finance owners approve write replay; Ramp must approve any limit increase.

## Output

A shared-egress inventory, limiter design, retry matrix, idempotency policy, benchmark, canary outcome, dashboards, and vendor increase evidence if needed.

## Error Handling

| Condition | Response |
|---|---|
| 429s continue below the local budget | Find other workloads sharing the egress IP and centralize their accounting. |
| A write returns 504 | Reconcile resource/task state before reuse of the original idempotency key. |
| Backoff grows queue lag | Prioritize by business criticality, shed nonessential polling, and preserve durable checkpoints. |

## Examples

### Example 1

Coordinate three sync workers behind one NAT with a shared rolling limiter and jittered retries.

### Example 2

Recover a 504-prone historical seed by reducing page scope and committing each page before cursor advance.

## Validation

- Aggregate egress stays below the re-verified current limit during load tests.
- Retry budgets are bounded and observable.
- Ambiguous writes cannot create duplicate financial effects.
- 429/504 reduction does not hide missing pages, stalled queues, or reconciliation gaps.

## Resources

- [Official documentation and contract notes](references/official-docs.md)
- Re-check the dated contract and current OpenAPI schema before any live request.
- Treat unresolved vendor behavior, authority, or financial state as a stop condition.
