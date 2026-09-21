---
name: ramp-incident-runbook
description: >-
  Analyze, contain, reconcile, and recover a Ramp integration incident involving authentication, webhooks, sync workers, financial writes, or card workflows. Use when responding to an active production degradation. Trigger with "Ramp incident" or "Ramp sync outage".
allowed-tools: Read,Glob,Grep,Write,Edit
version: 2.0.0
argument-hint: "[integration-or-environment]"
model: inherit
effort: high
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Requires current Ramp Developer API documentation and approved access for any live financial, card, identity, accounting, application, or configuration change
tags: [saas, ramp, incident-response, reliability, reconciliation]
---
# Ramp Integration Incident Runbook

## Overview

Protect financial correctness before throughput. Stop unsafe writes, preserve cursors and idempotency state, determine the blast radius by entity and object, and recover through controlled reconciliation.

## Prerequisites

- Identify the Ramp application, environment, business entities, affected data and workflows, accountable owner, and rollback boundary.
- Read `references/official-docs.md` and re-check endpoint schemas, scopes, limits, and support status before a live operation.
- Use synthetic fixtures or Ramp sandbox until production access and business effects are explicitly approved.
- Prepare approved secret storage and a sanitized evidence location.

## Current Contract

- Ramp errors expose status, structured error information, and `x-trace-id` for correlation.
- Webhook delivery and polling can overlap, so recovery must be idempotent and reconcile objects rather than replay blindly.
- 429 and 5xx may be transient; 504 crosses Ramp's 60-second request timeout and leaves write outcomes potentially ambiguous.
- Accounting success is not complete until the downstream ERP receipt and Ramp sync receipt agree.

## Instructions

1. Declare severity and owners; freeze deploys, credential changes, cursor advancement, and affected writes while leaving safe reads and evidence capture available.

2. Bound impact by environment, entity, endpoint/event, release, time window, object IDs, amounts, queue depth, webhook lag, and downstream system.

3. Classify vendor, auth, permission, schema, rate, timeout, data, or deployment cause using sanitized trace IDs and exact artifact/config changes.

4. Contain by disabling only the unsafe writer or subscription path; reconcile ambiguous writes and deferred tasks before retries.

5. Recover a bounded cohort with original idempotency keys, compare source and destination totals, then expand gradually and complete post-incident credential/evidence cleanup.

## Tool Discipline

- Use **Glob** to locate candidate code, manifests, fixtures, and evidence without widening scope.
- Use **Grep** to find relevant endpoints, fields, permissions, identifiers, errors, and stale assumptions.
- Use **Read** to inspect the smallest required local files and authoritative evidence.
- Use **Write** only for a new approved local draft, test, configuration, or evidence artifact.
- Use **Edit** only for a bounded approved change with a known rollback.
- Local file tools do not authorize a Ramp operation or replace owner approval.

## Approval Boundaries

The incident commander controls containment and recovery. Finance approves financial replay or reversal; security controls credential action; data owners approve production evidence handling.

## Output

A timestamped incident record, blast-radius ledger, containment state, trace IDs, object reconciliation, replay/reversal decisions, recovery gates, and follow-up owners.

## Error Handling

| Condition | Response |
|---|---|
| Pressure rises to replay the whole queue | Keep the freeze and reconcile a bounded window first; throughput does not override duplicate-risk controls. |
| A token may be compromised | Revoke or rotate through security, inventory affected clients, and prove old credentials fail. |
| Ramp and ERP totals disagree | Quarantine the cohort and resolve per-object references before resuming sync marking. |

## Examples

### Example 1

Contain a webhook consumer that duplicated ERP posts, reconcile by Ramp transaction ID, reverse duplicates, and replay one canary window.

### Example 2

Handle widespread 429s by pausing workers, preserving checkpoints, lowering concurrency, and proving complete catch-up.

## Validation

- Unsafe writes are stopped without destroying queues, cursors, or idempotency evidence.
- Blast radius is quantified by object and amount, not only request count.
- Recovery proves no loss or duplicate financial effect.
- Timeline, decisions, approvals, trace IDs, and corrective actions are durable.

## Resources

- [Official documentation and contract notes](references/official-docs.md)
- Re-check the dated contract and current OpenAPI schema before any live request.
- Treat unresolved vendor behavior, authority, or financial state as a stop condition.
