---
name: workhuman-rate-limits
description: 'Discover and enforce the tenant-specific Workhuman capacity and retry contract for integrations and batch workflows. Use when controlling throughput or resolving throttling. Trigger with "govern Workhuman rate limits".'
argument-hint: "[workflow] [expected-volume]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.4.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, workhuman, rate-limits, backpressure, reliability]
model: inherit
effort: high
compatibility: Designed for Claude Code; production traffic and schedule changes require customer and integration-owner approval
---
# Workhuman Capacity and Backpressure Governance

## Overview

Replace guessed quotas with measured, documented capacity controls that protect recognition, worker-sync, reporting, and downstream systems.

## Prerequisites

- Current customer-authorized capacity, retry, batch, and support contract
- Expected records and requests by direction, operation, tenant, and time window
- Service-level objectives, recovery objectives, and authoritative reconciliation method

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect traffic and retry configuration, `WebFetch` for current vendor context, and `Write` or `Edit` for models, controls, fixtures, and redacted evidence.

## Current Contract

The cited Workhuman public pages do not publish universal request-per-minute limits, retry headers, batch sizes, or concurrency values. Treat all numbers as tenant- and operation-specific until confirmed in current authorized documentation or support evidence.

## Authentication

Partition capacity by the documented tenant and principal boundaries. Never rotate credentials, create extra principals, or distribute traffic to evade a limit.

## Instructions

1. Inventory every traffic source, operation, direction, schedule, principal, batch size, concurrency, and downstream dependency.
2. Obtain the current documented limits and retry semantics or record a vendor question; do not infer them from a short observation.
3. Establish baselines for latency, throughput, throttling, queue age, error class, batch duration, and reconciliation lag.
4. Implement shared admission control, bounded concurrency, timeout budgets, queue limits, jittered backoff, and retry caps.
5. Retry only operations proven safe by read semantics, idempotency, or authoritative reconciliation.
6. Test burst, sustained load, throttling, timeout, partial batch, downstream slowdown, and recovery with synthetic fixtures.
7. Present schedule or concurrency changes with evidence, projected capacity, abort threshold, owner, and rollback.
8. After approval, canary and compare observed behavior with the model; update the dated contract record.

## Approval Boundaries

Do not load-test production, increase schedules or concurrency, split principals, or retry ambiguous recognition and award writes without approval.

## Output

Return the documented capacity evidence, traffic inventory, baseline, control policy, retry classification, test result, canary measurements, and unresolved vendor limits.

## Error Handling

| Condition | Response |
|---|---|
| No capacity contract is available | Use a conservative customer-approved canary and ask Workhuman for authoritative limits. |
| Throttling response is ambiguous | Stop retry escalation and preserve headers and correlation evidence safely. |
| Queue threatens the recovery objective | Shed or pause approved low-priority work and notify the service owner. |

## Example

A redacted completion receipt might look like this:

```text
workflow=worker-sync; limit=customer-contract; concurrency=bounded; retries=safe-reads-only; burst-test=pass; canary=p95-within-slo
```

## Resources

- [Workhuman integrations](https://www.workhuman.com/capabilities/integrations/)
- [Workhuman security and privacy](https://www.workhuman.com/why-workhuman/security-and-privacy/)

## Next Steps

Revalidate the capacity model after contract, volume, schedule, tenant, or connector changes.
