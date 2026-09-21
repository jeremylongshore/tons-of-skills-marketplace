---
name: ramp-cost-tuning
description: >-
  Reduce Ramp integration workload and operating cost without losing financial completeness. Use when polling, storage, retries, or accounting synchronization consumes excessive capacity. Trigger with "optimize Ramp sync cost" or "reduce Ramp API calls".
allowed-tools: Read,Glob,Grep,Write,Edit
version: 2.0.0
argument-hint: "[integration-or-environment]"
model: inherit
effort: high
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Requires current Ramp Developer API documentation and approved access for any live financial, card, identity, accounting, application, or configuration change
tags: [saas, ramp, cost, efficiency, webhooks]
---
# Ramp Integration Cost and Workload Tuning

## Overview

Cost tuning is a correctness exercise: remove redundant retrieval, not evidence. Establish a complete baseline, shift change detection to webhooks where supported, and preserve periodic reconciliation for missed or non-evented changes.

## Prerequisites

- Identify the Ramp application, environment, business entities, affected data and workflows, accountable owner, and rollback boundary.
- Read `references/official-docs.md` and re-check endpoint schemas, scopes, limits, and support status before a live operation.
- Use synthetic fixtures or Ramp sandbox until production access and business effects are explicitly approved.
- Prepare approved secret storage and a sanitized evidence location.

## Current Contract

- Ramp recommends persisting an initial full sync locally and fetching new or changed records incrementally where endpoint semantics support it.
- Incremental filters are endpoint-specific; for example, transaction `synced_after` covers accounting sync events, not every transaction update.
- Webhooks reduce polling but do not remove the need for idempotent consumption and periodic reconciliation.
- Batch and page limits are endpoint-specific and must be read from the current schema before tuning.

## Instructions

1. Measure requests, pages, transferred bytes, retries, storage growth, reconciliation lag, webhook volume, and operator toil by endpoint and entity.

2. Classify each poll as initial seed, supported incremental read, unsupported change detection, recovery reconciliation, or waste.

3. Replace eligible near-real-time polling with scoped webhooks and a durable deduplicating queue; retain scheduled reconciliation for gaps.

4. Use maximum safe page sizes, endpoint filters with verified semantics, bounded concurrency, conditional local reads, and batch operations where documented.

5. Compare pre/post completeness, latency, error rate, API demand, infrastructure cost, and recovery time before accepting the change.

## Tool Discipline

- Use **Glob** to locate candidate code, manifests, fixtures, and evidence without widening scope.
- Use **Grep** to find relevant endpoints, fields, permissions, identifiers, errors, and stale assumptions.
- Use **Read** to inspect the smallest required local files and authoritative evidence.
- Use **Write** only for a new approved local draft, test, configuration, or evidence artifact.
- Use **Edit** only for a bounded approved change with a known rollback.
- Local file tools do not authorize a Ramp operation or replace owner approval.

## Approval Boundaries

Data and accounting owners approve any freshness or retention change. Platform owners approve queue, schedule, and capacity changes; vendor limit increases require a documented support request.

## Output

A cost baseline, endpoint demand map, proposed changes, completeness guardrails, benchmark results, rollback thresholds, and accountable owners.

## Error Handling

| Condition | Response |
|---|---|
| Request count drops but records go missing | Roll back and reconcile the full affected window; the optimization failed its correctness gate. |
| A filter name looks incremental | Verify its exact semantics in first-party docs before using it as a checkpoint. |
| Webhook volume spikes | Backpressure the consumer and deduplicate; do not discard events or disable reconciliation silently. |

## Examples

### Example 1

Replace five-minute bill polling with bill webhooks plus a nightly entity-scoped reconciliation.

### Example 2

Persist a transaction seed locally and eliminate repeated full-history downloads while retaining a documented re-seed path.

## Validation

- Before and after datasets reconcile by entity, object ID, amount, currency, and status.
- Freshness objectives and recovery windows are explicit.
- No undocumented limit, filter, or batching guarantee is assumed.
- Savings are measured without weakening audit, security, or incident evidence.

## Resources

- [Official documentation and contract notes](references/official-docs.md)
- Re-check the dated contract and current OpenAPI schema before any live request.
- Treat unresolved vendor behavior, authority, or financial state as a stop condition.
