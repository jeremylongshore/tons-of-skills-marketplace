---
name: salesforce-webhooks-events
description: 'Select and govern Salesforce change delivery across Pub/Sub API, Change Data Capture, Platform Events, event relay, Streaming API, Outbound Messages, or polling. Use when building event-driven integrations. Trigger with "design Salesforce events".'
argument-hint: "[org-alias] [business-change]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, salesforce, pub-sub-api, change-data-capture, events]
model: inherit
effort: high
compatibility: Designed for Claude Code; event enablement, publication, subscription, relay, and replay changes require Salesforce admin and data owner approval
---
# Salesforce Event and Change-Delivery Decision

## Overview

Choose the supported delivery contract from business semantics, entitlement, transport, ordering, replay, schema, security, and recovery evidence.

## Prerequisites

- Business event or record-change definition, producer, consumers, latency, ordering, volume, and recovery objective
- Current org edition, event entitlements, permissions, channels, schema, delivery allocation, and support contract
- Consumer idempotency, checkpoint or replay state, dead-letter path, reconciliation, and backfill owner

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect approved repository and evidence files, `WebFetch` to re-check current first-party Salesforce documentation, and `Write` or `Edit` only for secretless plans, fixtures, configuration, and redacted receipts.

## Current Contract

Pub/Sub API uses gRPC over HTTP/2 and Avro for platform events, Change Data Capture, and real-time event monitoring. CDC publishes near-real-time record changes and can emit gap or overflow events; other Salesforce delivery mechanisms have different contracts.

## Authentication

Use the documented OAuth and permission model for the selected producer and consumer. Protect tokens, event payloads, replay or checkpoint state, schemas, org identifiers, and personal data.

## Instructions

1. Define business semantics, source of truth, producer authority, consumers, payload minimum, ordering key, latency, and loss tolerance.
2. Discover the org edition, enabled event products, Pub/Sub or alternative availability, channels, permissions, schemas, and allocations.
3. Compare Pub/Sub API, CDC, custom Platform Events, event relay, Streaming API, Outbound Messages, and bounded polling against requirements.
4. Design idempotency, schema compatibility, checkpoint or replay handling, flow control, reconnect, dead letter, and poison-event isolation.
5. Model duplicate, delayed, out-of-order, gap, overflow, schema-change, permission-loss, quota, and consumer-outage cases.
6. Run a synthetic non-production publication or change canary and prove delivery, recovery, redaction, and no duplicate business effect.
7. Enable production in a bounded cohort, monitor delivery and business reconciliation, and maintain a documented backfill path.

## Approval Boundaries

Do not enable entities, create channels, publish events, expose fields, reset checkpoints, replay, or backfill without platform, data, security, and consumer-owner approval.

## Output

Return the delivery decision, entitlement evidence, schema and permission contract, capacity plan, recovery design, canary receipt, reconciliation, and owners.

## Error Handling

| Condition | Response |
|---|---|
| Gap or overflow event is observed | Pause trust in the stream, bound the affected interval, and run the approved reconciliation or backfill path. |
| Consumer checkpoint is lost | Do not guess; restore from durable state or reconcile from the source of truth. |
| Selected API is unavailable in the org | Choose a documented alternative and revise latency and recovery expectations. |

## Example

A redacted completion receipt might look like this:

```text
mode=pub-sub-cdc; channel=approved; schema=versioned; checkpoint=durable; canary=pass; duplicates=0; reconcile=pass
```

## Resources

- [Salesforce Pub/Sub API](https://developer.salesforce.com/docs/platform/pub-sub-api/overview)
- [Change Data Capture](https://developer.salesforce.com/docs/atlas.en-us.change_data_capture.meta/change_data_capture/cdc_intro.htm)

## Next Steps

Run the workflow first in the lowest-risk authorized org and preserve its redacted receipt. Schedule a review against the next Salesforce seasonal release and the customer change calendar.
