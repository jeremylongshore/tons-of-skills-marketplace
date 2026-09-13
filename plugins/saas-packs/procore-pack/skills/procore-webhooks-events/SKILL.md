---
name: procore-webhooks-events
description: >-
  Operate Procore hooks, triggers, deliveries, deduplication, and reconciliation as a best-effort notification system. Use when creating webhook subscriptions, upgrading payload formats, or recovering delayed, duplicate, or discarded deliveries. Trigger with: "set up Procore webhooks", "handle duplicate Procore events", "reconcile Procore webhook gaps".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[company-or-project-scope-and-resource-events]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - procore
  - webhooks
  - event-processing
compatibility: 'Requires a public HTTPS receiver, durable queue, reconciliation store, and Webhooks API permissions for the intended Procore scope.'
---

# Procore Webhook and Reconciliation Boundary

## Overview

Use webhooks for freshness and REST reconciliation for completeness. A delivery tells the receiver that a committed Procore change occurred; it is not the resource itself and may be duplicated, delayed, or discarded after prolonged endpoint failure.

## Prerequisites

- Company or project scope, namespace, resource names, and event reasons
- Public HTTPS receiver that acknowledges quickly and queues work durably
- Webhooks API permission, OAuth principal, deduplication store, and reconciliation cursor

## Instructions

### Step 1: Choose payload format

Use the current recommended payload format for new integrations and record the schema contract. Treat string identifier changes and renamed event fields as a versioned migration.

### Step 2: Create the hook

Create one company- or project-scoped hook with an HTTPS destination, required namespace, minimal destination headers, and no secrets in logs.

### Step 3: Add bounded triggers

Subscribe only to documented resources and reasons the application processes. Verify hook and trigger state through the documented API.

### Step 4: Acknowledge and queue

Validate structure, record the event identifier, enqueue a follow-up read, and return a success response within the provider timeout. Process business work asynchronously.

### Step 5: Deduplicate and hydrate

Use event ID or ULID according to the chosen payload. Fetch the current resource from REST and make downstream processing idempotent.

### Step 6: Reconcile gaps

Monitor deliveries and run periodic REST scans from a durable cursor. Explicitly repair the gap after endpoint failure or discarded notifications.

## Authentication

Webhook configuration calls use an OAuth 2.0 Bearer token with Webhooks API permission. Destination authentication uses only minimal reviewed headers; never log those headers or confuse them with Procore OAuth credentials.

## Tool Discipline

Use Read and Grep to inspect handler code, delivery evidence, and endpoint contracts. Use Write or Edit only for the approved hook manifest, handler, test, cursor, or receipt; provider-side hook changes require explicit approval.

## Output

- Hook, trigger, payload-version, and permission manifest
- Receiver, deduplication, hydration, and reconciliation evidence
- Delivery health, gap window, and recovery receipt

Return scope, namespace, payload version, trigger set, acknowledgment result, and reconciliation checkpoint.

## Examples

An RFI update delivery is acknowledged and queued immediately. A worker deduplicates by the versioned event identifier, retrieves the current RFI, and updates downstream state; a periodic scan catches any notification lost during receiver downtime.

## Error Handling

| Failure | Response |
| --- | --- |
| Receiver exceeds provider timeout | Acknowledge after durable enqueue and move processing out of the request path. |
| Duplicate delivery | Treat it as a no-op after confirming the event identifier was completed. |
| Delivery queue was discarded | Determine the gap window and run REST reconciliation before resuming. |
| Destination secret appears in logs | Rotate it, scrub artifacts, and reduce logged headers. |

## Resources

- [First-party source notes](references/official-docs.md)
- [How webhooks work](https://developers.procore.com/documentation/webhooks)
- [Set up webhooks](https://developers.procore.com/documentation/webhooks-api)
- [Hooks API reference](https://developers.procore.com/reference/rest/hooks?version=latest)
