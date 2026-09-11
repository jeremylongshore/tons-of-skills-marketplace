---
name: mindtickle-webhooks-events
description: 'Select and govern a supported Mindtickle change-ingestion pattern: documented event delivery, managed connector, polling, or export. Use when downstream systems need timely updates. Trigger with "ingest Mindtickle changes".'
argument-hint: "[use-case] [freshness-target]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, mindtickle, events, polling, webhooks]
model: inherit
effort: high
compatibility: Designed for Claude Code; event subscriptions, endpoints, schedules, and production writes require tenant, security, and downstream-owner approval
---
# Mindtickle Change Ingestion and Event Governance

## Overview

Choose the least risky supported delivery mode and make duplicates, ordering, authenticity, replay, privacy, reconciliation, and fallback explicit.

## Prerequisites

- A use case, source of truth, freshness objective, event or record volume, and downstream owner
- Current tenant documentation for available events, APIs, reports, exports, or managed connectors
- A data classification, retention policy, capacity contract, and recovery objective

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect consumers and schemas, `WebFetch` for current authorized contracts, and `Write` or `Edit` for ingestion code, fixtures, mappings, and redacted receipts.

## Current Contract

Mindtickle publicly confirms REST-based API families and managed integrations but does not publish a universal webhook registration route, event catalogue, signature header, or retry schedule. Treat webhook delivery as unavailable until tenant-authorized documentation explicitly defines it.

## Authentication

For documented push delivery, use the exact authenticity mechanism and secret lifecycle in the tenant contract. For polling or export, use a least-privilege tenant principal. Never invent an HMAC header or accept unauthenticated events.

## Instructions

1. Define the business transition, required fields, allowed delay, source authority, privacy class, and downstream mutation.
2. Inventory supported modes: managed connector, documented event delivery, incremental API read, scheduled report or export, and approved manual handoff.
3. Select the mode using supportability, authenticity, freshness, replay, observability, capacity, and cost—not a preference for webhooks.
4. Freeze schemas and define stable identity, deduplication, ordering assumptions, cursor or checkpoint ownership, and deletion behavior.
5. Implement validate-before-acknowledge, quarantine, bounded retry, dead-letter handling, and a reconciliation read or report.
6. Test valid, invalid, duplicate, late, out-of-order, missing-field, replay, revoked-auth, and outage cases with synthetic fixtures.
7. Present subscription, endpoint, schedule, or connector changes with exposure, owner, rollback, and secret plan.
8. After approval, canary the ingestion, reconcile against the source of truth, and retain only redacted operational evidence.

## Approval Boundaries

Do not expose an endpoint, create a subscription, enable a connector, poll production, replay messages, or mutate downstream records without named owners.

## Output

Return the selected mode and evidence, frozen schema, auth and secret plan, deduplication and ordering policy, failure tests, mutation preview, canary reconciliation, and fallback.

## Error Handling

| Condition | Response |
|---|---|
| Webhook contract is not documented | Use an approved polling, report, connector, or manual pattern; do not fabricate one. |
| Authenticity validation fails | Reject and quarantine without downstream mutation. |
| Checkpoint and source disagree | Stop advancement, reconcile the window, and preserve replay evidence. |

## Example

```text
use-case=completion-sync; mode=scheduled-report; freshness=daily; dedupe=source-id-plus-version; failure-fixtures=8-pass; reconciliation=exact
```

## Resources

- [Mindtickle integrations](https://www.mindtickle.com/platform/integrations/)
- [Subscription services](https://www.mindtickle.com/legal/description-of-subscription-services/)

## Next Steps

Review the selected delivery mode when tenant capabilities or freshness requirements change.
