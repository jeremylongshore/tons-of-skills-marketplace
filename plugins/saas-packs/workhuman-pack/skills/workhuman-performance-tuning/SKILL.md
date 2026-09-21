---
name: workhuman-performance-tuning
description: 'Measure and tune Workhuman adapter, worker-sync, recognition, reporting, and Store workflows within documented tenant limits. Use when tuning latency or throughput. Trigger with "tune Workhuman performance".'
argument-hint: "[workflow] [service-level-objective]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.4.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, workhuman, performance, reliability, optimization]
model: inherit
effort: high
compatibility: Designed for Claude Code; load tests and production concurrency, schedule, cache, or batch changes require accountable-owner approval
---
# Workhuman Evidence-Based Performance Tuning

## Overview

Improve an identified bottleneck while preserving correctness, freshness, privacy, financial integrity, and downstream capacity.

## Prerequisites

- A named workflow, current baseline, service-level objective, volume model, and bottleneck hypothesis
- Customer-authorized capacity and behavior contracts for every dependent system
- Synthetic load fixtures, reconciliation, abort thresholds, and rollback ownership

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect code and telemetry, `WebFetch` for current vendor context, and `Write` or `Edit` for benchmarks, controls, tests, and redacted receipts.

## Current Contract

Workhuman supports global recognition, rewards, reporting, open-API use, and managed integrations, but its public pages do not publish universal performance limits. Optimize against measured customer behavior and current documented boundaries.

## Authentication

Keep principals tenant- and environment-scoped during measurement. Do not increase credentials or bypass governance to raise throughput.

## Instructions

1. Freeze the workflow, source and destination, record volume, freshness, latency and throughput objectives, and correctness invariants.
2. Measure queue time, service time, retries, throttling, batch duration, payload size, downstream latency, and reconciliation lag.
3. Isolate whether the bottleneck is scheduling, serialization, network, vendor processing, HCM, reporting, Store, or downstream logic.
4. Choose one controlled change: batching, bounded concurrency, connection reuse, field minimization, scheduling, checkpointing, or an approved cache.
5. Define cache authority, key, tenant boundary, TTL, invalidation, sensitive fields, and staleness tolerance before caching.
6. Test steady, burst, empty, duplicate, partial, timeout, throttle, downstream-slow, and recovery cases with synthetic data.
7. Present expected gain, capacity impact, correctness proof, privacy effect, abort threshold, and rollback.
8. Canary after approval and retain before-and-after percentiles, throughput, errors, reconciliation, and cost effects.

## Approval Boundaries

Do not load-test production, increase concurrency or schedules, cache workforce or award data, or relax correctness and privacy controls without approval.

## Output

Return the baseline, bottleneck evidence, selected change, test matrix, capacity and privacy review, canary comparison, reconciliation, and rollback status.

## Error Handling

| Condition | Response |
|---|---|
| Faster result changes authoritative state | Reject the optimization and preserve correctness. |
| Tail latency improves but errors rise | Roll back and investigate retries or downstream saturation. |
| Limit is undocumented | Use a bounded customer-approved canary and request vendor guidance. |

## Example

A redacted completion receipt might look like this:

```text
workflow=worker-sync; baseline-p95=18m; change=bounded-batches; canary-p95=9m; errors=unchanged; reconciliation=exact
```

## Resources

- [Workhuman integrations](https://www.workhuman.com/capabilities/integrations/)
- [Workhuman Social Recognition](https://www.workhuman.com/platform/social-recognition/)

## Next Steps

Monitor the new baseline through one full business cycle and revert if correctness or downstream health regresses.
