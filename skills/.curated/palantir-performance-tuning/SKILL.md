---
name: palantir-performance-tuning
description: >-
  Tune Foundry transforms, OSDK queries, and Compute Modules from measured bottlenecks and correctness constraints. Use when latency, queue time, memory, throughput, or freshness misses objectives. Trigger with "Palantir performance" or "Foundry build slow".
allowed-tools: Read,Glob,Grep,Write,Edit
version: 2.0.0
argument-hint: "[build-query-or-module]"
model: inherit
effort: high
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Requires current Palantir Foundry documentation and approved access for any live resource, permission, data, build, application, or deployment change
tags: [saas, palantir, foundry, performance, optimization]
---
# Palantir Workload Performance Tuning

## Overview

Identify whether delay comes from build scheduling, compute, data shape, transaction history, query breadth, network concurrency, or interactive replicas. Change one layer at a time and retain output parity and access controls.

## Prerequisites

- Name the workload owner, service/data objective, representative window, exact build/query/module, and correctness tolerance.
- Capture queue time, duration, CPU, memory, input/output volume, retries, pagination, selected properties, and replica behavior.
- Read `references/official-docs.md` and confirm required engine features before changing compute.
- Prepare a sandbox branch or non-production application and a repeatable benchmark.

## Current Contract

- Foundry build metrics show requested and observed CPU/memory and can distinguish scheduling from execution constraints.
- Single-node and Spark engines support different features; Polars is recommended for many production single-node transforms but is not universally interchangeable.
- Incremental histories can become progressively slow and may require a snapshot build.
- OSDK query performance depends on filters, selected properties, pagination, links, aggregations, and subscription shape.

## Instructions

1. Define one user-visible or data objective and reproduce the miss on an exact workload version.

2. Locate the dominant bottleneck using Foundry metrics, build reports, query traces or timings, and module replica evidence.

3. Choose one bounded experiment: engine/resource request, partition/join shape, incremental snapshot, query filter/property selection, pagination, concurrency, or replica configuration.

4. Run the benchmark and compare correctness, access behavior, latency distribution, throughput, queue time, resource use, and failure rate.

5. Promote only a statistically and operationally meaningful improvement, then observe a representative production window.

## Tool Discipline

- Use **Glob** to locate candidate repositories, manifests, configurations, and evidence without widening scope.
- Use **Grep** to find relevant identifiers, declarations, permissions, errors, and stale claims.
- Use **Read** to inspect the smallest required files and authoritative evidence.
- Use **Write** only for a new approved local draft, test, manifest, or evidence artifact.
- Use **Edit** only for a bounded approved change whose rollback is known.
- Do not use file tools as a substitute for authenticated Foundry operations or owner approval.

## Approval Boundaries

Data and pipeline owners approve transform or snapshot changes; application owners approve query changes; platform owners approve module resources or scaling. Do not trade away correctness, security, or availability without an explicit owner decision.

## Output

A performance profile, bottleneck hypothesis, experiment, exact version, before/after metrics, parity and access tests, accepted change, rollback threshold, and follow-up observation.

## Error Handling

| Condition | Response |
|---|---|
| Metrics show queue delay rather than compute saturation | Avoid increasing resources blindly; assess requested resources and scheduler availability. |
| An engine change loses a required feature | Reject the experiment and use a compatible engine or redesign the workload. |
| Incremental latency grows over time | Rehearse a controlled snapshot and validate parity before resetting history. |
| A faster query changes returned objects | Restore the prior query and correct filters, ordering, properties, or pagination. |

## Examples

### Example 1

Diagnose an OOM transform by comparing requested and observed memory, join shape, input volume, and engine features, then validate one resource or algorithm change on a branch build.

### Example 2

Reduce an OSDK page's latency by adding a selective filter, requesting only displayed properties, bounding page size, and proving the same authorized object set and continuation behavior.

## Validation

- The bottleneck is supported by measured platform evidence.
- Before/after runs use the same representative workload and exact code/data contract.
- Outputs and permissions remain equivalent within the approved tolerance.
- Tail latency, queue time, failures, and resource use are all reported.
- Rollback is tested or mechanically straightforward.

## Resources

- [Official documentation and contract notes](references/official-docs.md)
- Re-check the dated contract before any live operation.
- Treat unresolved or changed vendor behavior as a stop condition.
