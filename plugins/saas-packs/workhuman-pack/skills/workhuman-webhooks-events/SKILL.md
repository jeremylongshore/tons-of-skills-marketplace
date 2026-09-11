---
name: workhuman-webhooks-events
description: 'Select and govern a supported Workhuman change-ingestion mode such as managed integration, documented event delivery, polling, report, or export. Use when building downstream updates. Trigger with "ingest Workhuman changes".'
argument-hint: "[use-case] [freshness-target]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.4.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, workhuman, events, polling, integrations]
model: inherit
effort: high
compatibility: Designed for Claude Code; event subscriptions, endpoints, schedules, connectors, and production processing require customer and downstream-owner approval
---
# Workhuman Change Ingestion and Event Governance

## Overview

Choose the least risky supported delivery mode and make authenticity, duplicates, ordering, replay, privacy, reconciliation, and fallback explicit.

## Prerequisites

- A defined business transition, source of truth, freshness target, expected volume, and downstream owner
- Current tenant documentation for managed integrations, events, APIs, reports, or exports
- Data classification, retention, capacity, incident, and recovery requirements

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect consumers and schemas, `WebFetch` for current first-party and tenant contracts, and `Write` or `Edit` for ingestion code, fixtures, mappings, and redacted receipts.

## Current Contract

Workhuman publicly confirms managed integrations and an open API but does not publish a universal webhook registration route, event catalogue, signature header, or retry schedule on the cited pages. Treat webhook delivery as unavailable until customer-authorized documentation defines it.

## Authentication

For documented push delivery, use the exact authenticity mechanism and secret lifecycle in the customer contract. For polling, reports, exports, or connectors, use a least-privilege authorized principal. Never invent an HMAC header or accept unauthenticated events.

## Instructions

1. Define transition, required fields, allowed delay, source authority, privacy class, and downstream mutation.
2. Inventory supported modes: managed connector, documented event delivery, incremental read, scheduled report or export, and approved manual handoff.
3. Select by supportability, authenticity, freshness, replay, observability, capacity, privacy, and cost—not a preference for webhooks.
4. Freeze schemas and define stable identity, deduplication, ordering assumptions, checkpoints, effective dates, and deletion behavior.
5. Implement validate-before-acknowledge, quarantine, bounded retry, dead-letter handling, and authoritative reconciliation.
6. Test valid, invalid, duplicate, late, out-of-order, missing-field, replay, revoked-auth, outage, and partial cases with synthetic fixtures.
7. Present endpoint, schedule, connector, or subscription changes with exposure, owner, rollback, secret plan, and approval.
8. Canary the approved mode, reconcile it to the authority, and retain only redacted operational evidence.

## Approval Boundaries

Do not expose an endpoint, create a subscription, enable a connector, poll production, replay messages, or mutate downstream records without named owners.

## Output

Return the selected mode and evidence, frozen schema, auth plan, deduplication and ordering policy, failure tests, mutation preview, canary reconciliation, and fallback.

## Error Handling

| Condition | Response |
|---|---|
| Webhook contract is not documented | Use an approved connector, polling, report, export, or manual pattern; do not fabricate one. |
| Authenticity validation fails | Reject and quarantine without downstream mutation. |
| Checkpoint and source disagree | Stop advancement, reconcile the window, and preserve replay evidence. |

## Example

A redacted completion receipt might look like this:

```text
use-case=award-to-payroll; mode=managed-workday; freshness=scheduled; dedupe=source-id-plus-version; failure-fixtures=10-pass; reconciliation=exact
```

## Resources

- [Workhuman integrations](https://www.workhuman.com/capabilities/integrations/)
- [Workhuman and workplace integrations overview](https://www.workhuman.com/blog/working-human-is-even-easier-with-workhuman-integrations/)

## Next Steps

Review the selected delivery mode whenever tenant capabilities, downstream authority, or freshness requirements change.
