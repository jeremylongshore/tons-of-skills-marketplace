---
name: salesloft-performance-tuning
description: >-
  Analyze and improve measured Salesloft sync latency and throughput with cursor polling, bounded page size, safe concurrency, caching, and correctness checks. Use when an integration is slow or falling behind. Trigger with "Salesloft performance", "speed up Salesloft sync", or "Salesloft cursor poller".
argument-hint: "[repository-path] [operation]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- salesloft
- performance
model: inherit
effort: medium
compatibility: Designed for Claude Code
---
# Salesloft Sync Performance Tuning

## Overview

This skill optimizes one measured Salesloft path without trading away completeness or tenant isolation. It treats deep pagination and uncontrolled concurrency as cost and correctness risks.

## Prerequisites

- A named operation, team, dataset size, and service-level objective
- Baseline latency, pages, endpoint cost, remaining budget, retries, and lag
- Correctness assertions and replayable fixtures
- Durable cursor and destination transaction boundary

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to locate pagers, caches, concurrency, checkpoints, and metrics. Use `WebFetch` only for current official Salesloft contracts. Use `Write` or `Edit` after the baseline and target path are confirmed.

## Current Contract

- Supported list endpoints generally page from 1 with up to 100 records per page.
- Deep page indices incur higher documented cost, so full scans degrade shared team capacity.
- Salesloft's efficient polling pattern sorts `updated_at` ascending and persists a microsecond-precision cursor.
- A production poller must handle overlap and duplicate processing safely.
- Actual response headers, not assumed request counts, measure endpoint cost.

## Authentication

Use the existing tenant-bound read credential. Performance work must not broaden scopes or mix caches, cursors, or limiters between teams.

## Instructions

1. Measure the slow path with record count, page count, p50/p95 latency, endpoint cost, remaining budget, and lag.
2. Confirm the endpoint's supported filters and sort fields.
3. Replace repeated deep scans with an `updated_at` cursor, ascending order, page size up to 100, and a deliberate overlap window.
4. Persist destination data and cursor atomically; deduplicate by stable resource ID and content fingerprint.
5. Add bounded per-team concurrency and cache only data with explicit freshness rules.
6. Load-test with fixtures, then run a bounded canary against an approved team.
7. Compare before/after performance and reconciliation counts before rollout.

## Approval Boundaries

Do not raise concurrency, remove overlap, skip reconciliation, or cache prospect data beyond policy merely to improve latency.

## Output

Return baseline, bottleneck, change, cursor and cache rules, rate impact, correctness comparison, canary result, and measured improvement.

## Error Handling

| Condition | Response |
|---|---|
| Records missing | Roll back and widen overlap or repair cursor logic. |
| Duplicate side effects | Make the consumer idempotent before resuming. |
| Endpoint cost rises | Reduce deep pages or concurrency and inspect actual headers. |
| Cache crosses team | Purge affected entries and investigate tenant isolation. |

## Examples

The example below shows the minimum redacted evidence expected from a successful invocation of this operator workflow.

```text
lag=18m->3m; p95=2.4s->0.8s; reconciled=100%; endpoint-cost=-63%
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Efficient cursor poller](https://developers.salesloft.com/docs/platform/guides/building-an-efficient-cursor-poller/)
- [Filtering, paging, and sorting](https://developers.salesloft.com/docs/platform/api-basics/filtering-paging-sorting/)
