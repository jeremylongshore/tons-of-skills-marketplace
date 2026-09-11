---
name: salesforce-reliability-patterns
description: 'Build Salesforce integration reliability with idempotency, bounded retries, durable state, dead letters, reconciliation, backfill, and tested recovery. Use when designing resilient systems. Trigger with "harden Salesforce reliability".'
argument-hint: "[integration] [failure-mode]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, salesforce, reliability, idempotency, recovery]
model: inherit
effort: high
compatibility: Designed for Claude Code; retry, replay, queue, failover, and data repair changes require system and data-owner approval
---
# Salesforce Reliability and Recovery Patterns

## Overview

Make every read, write, job, and event path safe under duplicate, delayed, partial, uncertain, throttled, and unavailable outcomes.

## Prerequisites

- Business invariants, sources of truth, operation classes, stable keys, ordering, latency, and recovery objectives
- Current Salesforce API, event, limit, error, job-result, and transaction contracts
- Durable queue and checkpoint stores, quarantine or dead-letter path, reconciliation, backfill, and owners

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect approved repository and evidence files, `WebFetch` to re-check current first-party Salesforce documentation, and `Write` or `Edit` only for secretless plans, fixtures, configuration, and redacted receipts.

## Current Contract

Salesforce synchronous, composite, bulk, and event surfaces have different transaction, result, retry, ordering, and recovery semantics. CDC can emit gap or overflow events; no transport removes the need for idempotency and reconciliation.

## Authentication

Use separate minimum-permission principals for runtime, repair, and diagnostics. Protect tokens, payloads, checkpoints, dead letters, and repair tooling from unauthorized access and logging.

## Instructions

1. Classify each operation as read, create, update, upsert, delete, job, publish, or consume and define its invariant and stable key.
2. Document timeout, error, partial-result, transaction, limit, ordering, duplicate, replay, and retention semantics from current contracts.
3. Design idempotency through external IDs, request ledgers, deduplication keys, conditional state, or invariant checks appropriate to the operation.
4. Retry only classified transient failures with bounded attempts, jitter, budget, and circuit breaking; reconcile uncertain outcomes first.
5. Persist queue, job, checkpoint, schema, and dead-letter state durably with redaction, retention, and ownership.
6. Test token expiry, timeouts, partial writes, locks, hard limits, duplicate events, gaps, schema drift, consumer outage, and restart.
7. Run recovery and backfill drills, compare against the source of truth, and measure recovery objectives and duplicate business effects.

## Approval Boundaries

Do not replay, purge queues, skip failed records, alter checkpoints, repair data, fail over, or change retry budgets without application and data owners.

## Output

Return the operation contracts, failure matrix, idempotency and retry design, durable-state schema, test results, recovery receipt, gaps, and owners.

## Error Handling

| Condition | Response |
|---|---|
| Write timed out with unknown outcome | Reconcile by stable key or request ledger before any retry. |
| Event gap or overflow is detected | Bound the interval and use the approved source-of-truth reconciliation or backfill. |
| Dead-letter payload contains sensitive data | Restrict and redact the store, assess exposure, and repair producers before replay. |

## Example

A redacted completion receipt might look like this:

```text
integration=orders; key=erp_id; retries=transient-only; ledger=durable; dlq=encrypted; chaos=pass; recovery=42m
```

## Resources

- [Change Data Capture](https://developer.salesforce.com/docs/atlas.en-us.change_data_capture.meta/change_data_capture/cdc_intro.htm)
- [Composite REST resources](https://developer.salesforce.com/docs/platform/api-rest/guide/resources-composite-composite.html)

## Next Steps

Run the workflow first in the lowest-risk authorized org and preserve its redacted receipt. Schedule a review against the next Salesforce seasonal release and the customer change calendar.
