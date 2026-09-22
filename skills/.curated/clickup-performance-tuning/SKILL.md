---
name: clickup-performance-tuning
description: >-
  Analyze and improve ClickUp throughput and freshness with endpoint-aware pagination, bounded concurrency, caching, and webhook invalidation. Use when ClickUp syncs are slow or rate constrained. Trigger with "ClickUp performance", "speed up ClickUp sync", or "ClickUp pagination".
argument-hint: "[sync-path] [baseline-window]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- clickup
- performance
model: inherit
effort: high
compatibility: Designed for Claude Code; benchmarks require authorized synthetic or non-sensitive data
---
# ClickUp Throughput and Freshness Tuning

## Overview

Tune measured bottlenecks while preserving completeness, ordering, freshness, and rate safety. Reject optimizations that improve speed by dropping provider records.

## Prerequisites

- A baseline of request volume, p50/p95 latency, page counts, payload sizes, 429s, queue age, and reconciliation
- Completeness and freshness assertions plus synthetic load fixtures
- Known endpoint-specific pagination and current token limit

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect the repository, adapters, configuration names, tests, and evidence. Use `WebFetch` only for current official ClickUp documentation. Use `Write` or `Edit` after confirming the target file, Workspace boundary, and requested mode.

## Current Contract

- Get Tasks returns 100 tasks per zero-based page and has explicit filters for closed tasks and subtasks; use `include_timl` for Tasks in Multiple Lists.
- Task comments use `start` plus `start_id` after the first 25 newest comments.
- The v2 task surface does not offer a general fields-selection parameter; do not invent one.
- Webhook invalidation can reduce polling, but delivery must be signed, idempotent, and reconciled.

## Authentication

Use a personal token only for accountable individual/testing work or OAuth Authorization Code for a user-facing integration. Inject the token server-side through a governed secret reference, send it in `Authorization`, verify authorized Workspace IDs, and never print the token, OAuth client secret, or webhook secret.

## Instructions

1. Measure each endpoint and business operation before changing caching or concurrency.
2. Verify pagination termination, ordering, filters, and reconciliation on boundary fixtures.
3. Coalesce duplicate reads and cache stable hierarchy metadata with explicit invalidation.
4. Set concurrency from the token's current remaining/reset headers and downstream queue capacity.
5. Use webhooks to invalidate or enqueue targeted reads while retaining a reconciliation sweep.
6. Benchmark the same cohort and reject improvements that lose records or violate freshness.

## Approval Boundaries

Do not raise concurrency, lengthen freshness windows, omit pages, or replace reconciliation with webhooks without owner-approved SLOs.

## Output

Return baseline/after latency and requests, completeness, freshness, cache hit rate, concurrency, 429s, and rollback decision.

## Error Handling

| Condition | Response |
|---|---|
| Page loop repeats or skips records | Stop and fix cursor/page state before tuning. |
| Cache serves stale task state | Invalidate and roll back the cache change. |
| 429 rate increases | Reduce concurrency and honor reset headers. |
| Webhook gap appears | Restore reconciliation reads and repair event handling. |

## Examples

The example below is a redacted operator receipt; it contains no task text, member data, credential, or webhook secret.

```text
cohort=500-tasks; complete=yes; requests=-31%; p95=-22%; 429=0; freshness=within-slo
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Get Tasks reference](https://developer.clickup.com/reference/gettasks)
- [Authentication](https://developer.clickup.com/docs/authentication)
- [Rate limits](https://developer.clickup.com/docs/rate-limits)
