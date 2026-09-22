---
name: salesloft-core-workflow-b
description: >-
  Reconcile Salesloft cadence membership state and engagement counts with an incremental, restartable read workflow. Use when building sales outcome reporting or downstream CRM synchronization. Trigger with "Salesloft cadence analytics", "Salesloft membership sync", or "Salesloft engagement reconciliation".
argument-hint: "[repository-path] [team-alias] [cursor]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- salesloft
- reconciliation
model: inherit
effort: medium
compatibility: Designed for Claude Code
---
# Salesloft Cadence Outcome Reconciliation

## Overview

This skill synchronizes cadence membership state and its documented engagement counts without relying on obsolete activity paths. It preserves mutable-record semantics and a restartable cursor.

## Prerequisites

- A named team and destination dataset
- `cadences:read` plus any endpoint-specific read scope
- A durable microsecond-precision `updated_at` cursor
- A documented merge key and data-retention policy

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect schemas, sync checkpoints, and consumers. Use `WebFetch` only for current Salesloft endpoint and polling documentation. Use `Write` or `Edit` after confirming the destination contract.

## Current Contract

- `GET /v2/cadence_memberships` supports `updated_at` filters, `sort_by=updated_at`, direction, page, and `per_page` up to 100.
- A membership is mutable and reused when a person later returns to the same cadence.
- Current state includes processing, staged, active, scheduled, pending, completed, removed, reassigned, and archived outcomes.
- Documented counts include views, clicks, replies, calls, sent emails, and bounces.

## Authentication

Use the explicit team credential with the minimum read scopes. Never mix cursors or destination partitions between teams.

## Instructions

1. Define the destination key, accepted fields, retention window, and team partition.
2. Start from a durable cursor with a deliberate overlap window for equal timestamps.
3. Fetch memberships ordered by `updated_at` ascending with a bounded page size.
4. Upsert by stable membership ID and treat state and counts as replaceable snapshots.
5. Advance the cursor only after the destination transaction succeeds.
6. Deduplicate overlap records and compare source, processed, and committed counts.
7. Reconcile periodic samples against Salesloft and alert on gaps or backward cursors.

## Approval Boundaries

Keep this workflow read-only in Salesloft. Do not infer immutable cadence episodes, individual email events, or user performance conclusions from aggregate membership counts alone.

## Output

Return team partition, cursor interval, pages and endpoint cost, source/upsert/deduplicated counts, reconciliation result, and next durable cursor.

## Error Handling

| Condition | Response |
|---|---|
| Cursor moves backward | Stop and restore the last committed checkpoint. |
| Same timestamp repeats | Use overlap plus stable-ID deduplication; never skip blindly. |
| 429 | Preserve the page and cursor, then resume after bounded backoff. |
| Destination partial failure | Roll back or replay the page before advancing. |

## Examples

The example below shows the minimum redacted evidence expected from a successful invocation of this operator workflow.

```text
team=team-42; fetched=100; upserted=98; overlap=2; cursor=committed
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [List cadence memberships](https://developers.salesloft.com/docs/api/cadence-memberships-index/)
- [Efficient cursor poller](https://developers.salesloft.com/docs/platform/guides/building-an-efficient-cursor-poller/)
