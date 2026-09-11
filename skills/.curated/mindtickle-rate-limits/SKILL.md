---
name: mindtickle-rate-limits
description: 'Discover and enforce a Mindtickle tenant''s documented capacity, retry, pagination, and concurrency contract. Use when planning bulk syncs or responding to throttling. Trigger with "handle Mindtickle limits".'
argument-hint: "[contract-path] [workload-profile]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, mindtickle, rate-limits, resilience, capacity]
model: inherit
effort: medium
compatibility: Designed for Claude Code; load tests and production schedule changes require tenant-owner and service-owner approval
---
# Mindtickle Capacity and Retry Contract

## Overview

Replace guessed quotas with an evidence-backed workload envelope and a conservative client policy that protects the tenant and downstream systems.

## Prerequisites

- Current tenant documentation or written vendor guidance for the operations in scope
- A workload profile with record counts, freshness target, windows, and priority
- Metrics for attempts, latency, responses, retries, backlog, and reconciliation

## Tool Discipline

Use `Read`, `Glob`, and `Grep` for workload and adapter configuration, `WebFetch` for current authorized contracts, and `Write` or `Edit` for a versioned policy and synthetic test fixtures.

## Current Contract

Mindtickle publicly states its integrations support high-volume transactions but does not publish universal endpoint quotas. Numeric limits, response headers, pagination, safe concurrency, and retry behavior must come from the customer's current contract or observed authorized responses.

## Authentication

Use a non-production, least-privilege principal for any capacity probe. Never distribute load across extra credentials or tenants to evade a documented limit.

## Instructions

1. Inventory each operation's documented pagination, batch size, concurrency, timeout, retry, and idempotency behavior.
2. Mark every missing value unknown; do not fill gaps with generic numbers.
3. Model peak demand, allowable staleness, downstream limits, and replay volume after an outage.
4. Define a conservative token or concurrency policy, bounded exponential backoff with jitter, and a total retry budget.
5. Add backpressure, dead-letter or quarantine handling, and write reconciliation where the contract permits.
6. Validate locally with synthetic throttle, timeout, malformed-response, and recovery fixtures.
7. Obtain approval before a controlled tenant probe; stop at the first throttling or instability signal.
8. Version the resulting envelope with evidence, owner, expiry, dashboards, and escalation thresholds.

## Approval Boundaries

Do not load-test production, evade limits, increase concurrency, or replay writes without tenant and service-owner approval.

## Output

Return the operation inventory, known and unknown limits, workload model, client policy, retry budget, test evidence, monitoring thresholds, and vendor questions.

## Error Handling

| Condition | Response |
|---|---|
| Limit signal is undocumented | Reduce concurrency, preserve redacted evidence, and ask Mindtickle for clarification. |
| Retry budget is exhausted | Quarantine remaining work and alert; do not loop indefinitely. |
| Backlog threatens freshness | Prioritize by business policy or renegotiate the window; never discard silently. |

## Example

```text
limits=tenant-documented; unknowns=2; concurrency=conservative; retries=bounded; throttle-fixture=pass; production-probe=not-run
```

## Resources

- [Mindtickle integrations](https://www.mindtickle.com/platform/integrations/)
- [Mindtickle support services](https://www.mindtickle.com/legal/support-services/)

## Next Steps

Exercise backlog recovery in a sandbox and review the workload envelope after contract or volume changes.
