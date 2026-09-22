---
name: ramp-performance-tuning
description: >-
  Analyze and tune Ramp pagination, concurrency, batching, webhooks, deferred tasks, and local persistence while preserving complete ordered reconciliation. Use when seeds are slow, syncs lag, or workloads encounter 504 responses. Trigger with "speed up Ramp sync" or "Ramp performance".
allowed-tools: Read,Glob,Grep,Write,Edit
version: 2.0.0
argument-hint: "[integration-or-environment]"
model: inherit
effort: high
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Requires current Ramp Developer API documentation and approved access for any live financial, card, identity, accounting, application, or configuration change
tags: [saas, ramp, performance, pagination, throughput]
---
# Ramp API Throughput and Sync Performance

## Overview

Measure first, then tune by endpoint and object lifecycle. Maximize useful work per request while staying below shared limits and keeping checkpoints at durable commit boundaries.

## Prerequisites

- Identify the Ramp application, environment, business entities, affected data and workflows, accountable owner, and rollback boundary.
- Read `references/official-docs.md` and re-check endpoint schemas, scopes, limits, and support status before a live operation.
- Use synthetic fixtures or Ramp sandbox until production access and business effects are explicitly approved.
- Prepare approved secret storage and a sanitized evidence location.

## Current Contract

- Ramp's default rate limit is 200 requests per rolling 10-second window per source IP, subject to current documentation and approved increases.
- API requests exceeding 60 seconds return 504; pagination and smaller work units are the primary controls for large reads.
- Most list endpoints support cursor-style pagination, but page sizes and incremental filters are endpoint-specific.
- Accounting batch endpoints may have explicit item caps and all-or-nothing behavior; current schema controls each batch.

## Instructions

1. Benchmark request latency, response bytes, records per page, pages per entity, retries, 429/504 rate, queue lag, database time, and reconciliation duration.

2. Separate initial full seed, incremental reads, webhook-driven fetches, periodic reconciliation, writes, and deferred tasks into independent budgets.

3. Increase page size only within the endpoint schema, bound concurrency below the shared IP window, add jitter, and persist after each downstream commit.

4. Use webhooks to trigger targeted reads, batch only where documented, and poll deferred tasks with bounded schedules rather than holding API requests open.

5. Load-test with synthetic or sandbox data, compare p50/p95/p99 plus completeness, then canary and retain rollback thresholds.

## Tool Discipline

- Use **Glob** to locate candidate code, manifests, fixtures, and evidence without widening scope.
- Use **Grep** to find relevant endpoints, fields, permissions, identifiers, errors, and stale assumptions.
- Use **Read** to inspect the smallest required local files and authoritative evidence.
- Use **Write** only for a new approved local draft, test, configuration, or evidence artifact.
- Use **Edit** only for a bounded approved change with a known rollback.
- Local file tools do not authorize a Ramp operation or replace owner approval.

## Approval Boundaries

Platform owners approve capacity and concurrency; data/accounting owners approve freshness and checkpoint changes; higher vendor limits require Ramp review.

## Output

A workload model, benchmark, endpoint budget, concurrency/page configuration, checkpoint design, load-test result, canary evidence, and rollback thresholds.

## Error Handling

| Condition | Response |
|---|---|
| Throughput rises with 429s | Lower and jitter concurrency across all workers sharing the source IP, then remeasure the rolling window. |
| Large pages trigger 504 | Reduce page or query scope and persist smaller committed units. |
| Checkpoint advances before downstream commit | Stop, rewind to the last durable checkpoint, and reconcile duplicates by source ID. |

## Examples

### Example 1

Reduce a multi-entity seed from serial tiny pages to bounded entity workers with schema-maximum pages and one shared limiter.

### Example 2

Replace bill status polling with webhooks plus targeted reads while retaining a scheduled full reconciliation.

## Validation

- Performance improves on measured latency or lag without missing or duplicating objects.
- Rate and timeout behavior remains within the current documented contract.
- Every cursor advances only after durable downstream commit.
- Results include sandbox/load evidence and a bounded production canary.

## Resources

- [Official documentation and contract notes](references/official-docs.md)
- Re-check the dated contract and current OpenAPI schema before any live request.
- Treat unresolved vendor behavior, authority, or financial state as a stop condition.
