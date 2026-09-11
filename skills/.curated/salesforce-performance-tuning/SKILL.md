---
name: salesforce-performance-tuning
description: 'Analyze and tune Salesforce query, pagination, batching, caching, automation, and asynchronous performance using measured org evidence. Use when resolving latency or throughput problems. Trigger with "tune Salesforce performance".'
argument-hint: "[org-alias] [workload]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, salesforce, performance, soql, query-plan]
model: inherit
effort: high
compatibility: Designed for Claude Code; query, index, automation, concurrency, and production workload changes require platform and object owner approval
---
# Evidence-Driven Salesforce Performance Tuning

## Overview

Optimize the end-to-end workload without trading correctness, permission enforcement, shared capacity, or recovery for a synthetic benchmark.

## Prerequisites

- Representative workload, latency and throughput objectives, business invariant, and current telemetry
- Queries, object volumes, selectivity, pagination, automation, locks, API mode, limits, and downstream timing
- Authorized performance org or sandbox, synthetic dataset, stop thresholds, and rollback owner

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect approved repository and evidence files, `WebFetch` to re-check current first-party Salesforce documentation, and `Write` or `Edit` only for secretless plans, fixtures, configuration, and redacted receipts.

## Current Contract

Salesforce offers versioned query and limits resources; query performance feedback through REST explain is explicitly Beta. Query plans, indexes, object cardinality, automation cost, and limits depend on the target org and must be measured.

## Authentication

Use an approved read-only performance principal first and a separately approved principal for canary writes. Do not collect broad record payloads or use administrator access to mask real permission cost.

## Instructions

1. Define the business invariant and measure end-to-end latency, throughput, error rate, API consumption, locks, retries, and downstream lag.
2. Trace time across client, network, authentication, query, pagination, automation, async jobs, event delivery, and reconciliation.
3. Inspect query shape, selected fields, predicates, cardinality, selectivity, ordering, pagination, and current metadata.
4. Use documented explain or query-plan tooling only under its current status and corroborate recommendations with measured tests.
5. Compare bounded changes to query design, caching, conditional requests, composite or bulk modes, concurrency, and scheduling.
6. Canary one change at a time with synthetic or approved non-production data and fixed stop thresholds.
7. Verify correctness, permissions, limits, event and business outcomes; roll back regressions and publish the evidence.

## Approval Boundaries

Do not request indexes, change automation, increase concurrency, add caches, alter consistency, or load production for a benchmark without owners.

## Output

Return the baseline trace, bottleneck evidence, tested alternatives, capacity effect, correctness checks, canary result, rollback, and recommendation.

## Error Handling

| Condition | Response |
|---|---|
| Explain output is treated as production proof | Label it Beta guidance and require representative measured validation. |
| Optimization changes returned records | Reject the change and restore the original business invariant. |
| Faster client behavior consumes unsafe shared capacity | Apply backpressure or scheduling before increasing rollout. |

## Example

A redacted completion receipt might look like this:

```text
workload=account-sync; baseline_p95=recorded; bottleneck=query; change=selective-filter; limits=safe; correctness=exact; canary=pass
```

## Resources

- [REST query performance feedback](https://developer.salesforce.com/docs/platform/api-rest/guide/dome-query-explain.html)
- [REST API limits](https://developer.salesforce.com/docs/platform/api-rest/guide/resources-limits.html)

## Next Steps

Run the workflow first in the lowest-risk authorized org and preserve its redacted receipt. Schedule a review against the next Salesforce seasonal release and the customer change calendar.
