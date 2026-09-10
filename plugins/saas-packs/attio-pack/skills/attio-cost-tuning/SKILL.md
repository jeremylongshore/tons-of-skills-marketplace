---
name: attio-cost-tuning
description: >-
  Analyze and reduce avoidable Attio integration cost and load by measuring request volume, query complexity, synchronization churn, and retained data before changing architecture. Use when an Attio workload is wasteful or operationally expensive. Trigger with "Attio cost", "reduce Attio API usage", or "Attio sync efficiency".
argument-hint: "[repository-path] [measurement-window]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.7.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- attio
- optimization
model: inherit
effort: high
compatibility: Designed for Claude Code
---
# Attio Workload Cost Review

## Overview

This skill optimizes application-controlled workload rather than guessing at plan prices. It converts observed traffic and synchronization behavior into a ranked change proposal.

## Prerequisites

- A representative measurement window and environment
- Request counts grouped by endpoint, method, status, and caller
- Query shapes, pagination behavior, and retry counts
- Current account terms for any commercial decision

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to locate polling loops, duplicate writes, query construction, caches, and telemetry. Use `WebFetch` only for current official Attio documentation. Use `Write` or `Edit` after a measured baseline and rollback plan exist.

## Current Contract

- Do not encode fixed prices, entitlements, or savings claims in code or durable guidance.
- Read and write requests have different published rate-limit tiers; record and entry queries can also incur score-based limits.
- A lower request count is not automatically better if it increases query complexity or stale-data risk.
- Webhooks can replace some polling, but delivery is at least once and requires deduplication.

## Authentication

Use the existing least-privilege Bearer credential for observation. Cost analysis never requires broader scopes than the workload already uses.

## Instructions

1. Establish request volume, retry amplification, polling frequency, and duplicate-write baseline.
2. Identify calls that fetch unused fields, repeat stable discovery, or write unchanged values.
3. Separate offset/cursor traversal costs by endpoint and inspect expensive record or entry filters.
4. Model candidate changes: cached schema discovery, change detection, bounded concurrency, webhook-assisted sync, or shorter retention.
5. Quantify impact with ranges and state freshness, reliability, and complexity tradeoffs.
6. Implement one reversible change and compare it with the same measurement window.

## Approval Boundaries

Do not change commercial plans, delete retained data, reduce audit history, or replace polling with webhooks without owner review of reliability and recovery behavior.

## Output

Return baseline metrics, top cost or load drivers, ranked proposals, assumptions, selected change, rollback trigger, and post-change comparison.

## Error Handling

| Condition | Response |
|---|---|
| No reliable telemetry | Instrument first; label estimates as unverified. |
| Provider pricing is needed | Consult the current account and official commercial source. |
| Optimization increases 429s | Reduce concurrency or query complexity and roll back. |
| Fewer calls create stale data | Restore the prior freshness boundary. |

## Examples

Input:

```text
window=seven representative days; symptom=repeated object-schema reads
```

Expected handoff:

```text
baseline=measured; change=bounded schema cache; freshness=preserved; rollback=defined
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Rate limiting](https://docs.attio.com/rest-api/guides/rate-limiting)
- [Configuring webhooks](https://docs.attio.com/rest-api/guides/webhooks)
- [Pagination](https://docs.attio.com/rest-api/guides/pagination)
