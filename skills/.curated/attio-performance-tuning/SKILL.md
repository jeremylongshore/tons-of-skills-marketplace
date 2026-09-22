---
name: attio-performance-tuning
description: >-
  Analyze and improve Attio integration latency and throughput from measured query shape, pagination, concurrency, retry, and cache evidence while preserving correctness. Use when Attio requests are slow or queues are backing up. Trigger with "Attio performance", "speed up Attio sync", or "Attio query tuning".
argument-hint: "[repository-path] [measurement-window]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- attio
- performance
model: inherit
effort: high
compatibility: Designed for Claude Code
---
# Attio Query and Sync Performance

## Overview

This skill tunes observed bottlenecks without promising a universal latency target. It keeps query complexity, rate limits, freshness, and mutation safety visible.

## Prerequisites

- Latency distributions by endpoint and operation
- Queue depth, concurrency, retry, and 429 metrics
- Representative query filters, sorts, and object or list sizes
- A correctness baseline for synchronized fields

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect query construction, pagination, concurrency, caches, and telemetry. Use `WebFetch` only for current official Attio documentation. Use `Write` or `Edit` after a measured hypothesis and rollback threshold are stated.

## Current Contract

- Attio publishes separate global limits for reads and writes and score-based limits for record and entry queries.
- Complex filters and sorts can increase query score; raw request concurrency is not the only load variable.
- Pagination may be offset-based or cursor-based depending on the endpoint.
- Cache object and attribute discovery only with an explicit freshness and invalidation policy.

## Authentication

Use the workload's existing least-privilege Bearer token. Performance measurement does not justify additional scopes or access to broader CRM data.

## Instructions

1. Measure p50, p95, failure rate, 429 rate, queue age, and retry amplification for a representative window.
2. Segment by endpoint, method, filter/sort shape, page size, and workspace.
3. Verify that each paginator terminates according to its endpoint contract and does not refetch pages.
4. Rank hypotheses such as simpler filters, lower concurrency, bounded caching, change detection, or webhook-assisted work.
5. Change one variable, retain correctness assertions, and compare with the same workload.
6. Roll back when error rate, stale-data risk, or queue age crosses the declared threshold.

## Approval Boundaries

Do not trade away correctness, auditability, or data freshness for latency without owner approval. Do not raise concurrency merely because the published global ceiling is higher.

## Output

Return baseline metrics, segmented bottleneck evidence, the selected hypothesis and change, correctness checks, comparable after-metrics, and the explicit rollback decision.

## Error Handling

| Condition | Response |
|---|---|
| No representative baseline | Instrument and wait for usable evidence. |
| Query gets 429 despite low count | Inspect score-based complexity and shared workspace traffic. |
| Optimization changes results | Roll back and restore correctness first. |
| Cache serves stale schema | Invalidate it and tighten the freshness policy. |

## Examples

Input:

```text
symptom=query queue age; endpoint=record query; window=representative peak
```

Expected handoff:

```text
bottleneck=filter-score; change=simplified-query; correctness=pass; p95=improved
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Rate limiting](https://docs.attio.com/rest-api/guides/rate-limiting)
- [Pagination](https://docs.attio.com/rest-api/guides/pagination)
- [List records](https://docs.attio.com/rest-api/endpoint-reference/records/list-records)
