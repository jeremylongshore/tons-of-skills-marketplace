---
name: mindtickle-performance-tuning
description: 'Diagnose and improve a Mindtickle integration with measured latency, backlog, freshness, and reconciliation evidence. Use when reports or syncs miss objectives. Trigger with "tune Mindtickle performance".'
argument-hint: "[service] [measurement-window]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, mindtickle, performance, observability, reliability]
model: inherit
effort: high
compatibility: Designed for Claude Code; production load, concurrency, caching, and schedule changes require service and tenant-owner approval
---
# Evidence-Driven Mindtickle Integration Performance

## Overview

Improve the customer-controlled integration path from a reproducible baseline while respecting tenant contracts, privacy, freshness, and correctness.

## Prerequisites

- A service-level objective, representative workload, current contract digest, and observation window
- Metrics for latency, attempts, errors, retries, backlog age, throughput, freshness, and reconciliation
- A non-production load path or approved canary with explicit abort thresholds

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect traces and configuration, `WebFetch` for current authorized contracts, and `Write` or `Edit` for benchmarks, controlled changes, tests, and redacted receipts.

## Current Contract

Performance spans the customer application, network, identity, adapter, tenant operations, and downstream systems. Mindtickle states support for scalable integrations but does not publish universal latency or quota targets, so customer objectives and tenant-specific evidence must remain separate.

## Authentication

Benchmark with synthetic or aggregate data and a least-privilege non-production principal. Never use extra credentials to create artificial concurrency or include payload contents in traces.

## Instructions

1. Define the user or business symptom, objective, correctness invariant, workload, and baseline window.
2. Break elapsed time into queue, customer processing, network, tenant response, downstream processing, and reconciliation.
3. Segment by operation, page or batch, payload class, tenant, response class, and time without exposing personal data.
4. Rank bottlenecks by measured contribution and distinguish latency from throttling, backlog, and data-quality delay.
5. Propose one controlled change at a time: scheduling, bounded concurrency, pagination, batching, caching, indexing, or payload reduction only where the contract permits it.
6. Define cache ownership, freshness, invalidation, privacy, and stale-data behavior before enabling a cache.
7. Run the experiment within abort thresholds and compare p50, tail latency, errors, retries, backlog, freshness, and reconciliation.
8. Retain the change only when the improvement is repeatable and correctness is unchanged; otherwise roll back.

## Approval Boundaries

Do not load-test production, raise concurrency, retain learner data in a cache, or trade correctness for speed without explicit owners.

## Output

Return the objective, baseline, bottleneck evidence, experiment, approvals, before-and-after metrics, correctness reconciliation, decision, and rollback receipt.

## Error Handling

| Condition | Response |
|---|---|
| Metrics omit queue or retry time | Repair instrumentation before claiming improvement. |
| Vendor behavior changes during a test | Stop, preserve the window, and rerun after the contract is stable. |
| Faster run produces divergent data | Roll back immediately and investigate correctness first. |

## Example

```text
objective=freshness-under-target; baseline=7d; bottleneck=customer-queue; change=schedule-partition; tail-latency=improved; reconciliation=exact
```

## Resources

- [Mindtickle integrations](https://www.mindtickle.com/platform/integrations/)
- [Mindtickle Service Level Agreement](https://www.mindtickle.com/legal/service-level-agreement/)

## Next Steps

Observe the retained change for a full workload cycle and update the capacity policy with measured evidence.
