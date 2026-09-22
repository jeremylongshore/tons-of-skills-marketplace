---
name: ramp-webhooks-events
description: >-
  Build a verified, idempotent Ramp webhook receiver with raw-body HMAC validation, fast acknowledgement, durable processing, and reconciliation. Use when handling transaction, bill, reimbursement, spend-request, or other Ramp events. Trigger with "Ramp webhooks" or "verify Ramp signature".
allowed-tools: Read,Glob,Grep,Write,Edit
version: 2.0.0
argument-hint: "[integration-or-environment]"
model: inherit
effort: high
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Requires current Ramp Developer API documentation and approved access for any live financial, card, identity, accounting, application, or configuration change
tags: [saas, ramp, webhooks, events, idempotency]
---
# Ramp Webhook Verification and Processing

## Overview

Verify authenticity before parsing, acknowledge only after durable receipt, and treat each event as a notification to reconcile current resource state. Design for retries, duplicates, and out-of-order delivery.

## Prerequisites

- Identify the Ramp application, environment, business entities, affected data and workflows, accountable owner, and rollback boundary.
- Read `references/official-docs.md` and re-check endpoint schemas, scopes, limits, and support status before a live operation.
- Use synthetic fixtures or Ramp sandbox until production access and business effects are explicitly approved.
- Prepare approved secret storage and a sanitized evidence location.

## Current Contract

- New subscriptions begin `pending_verification`; Ramp sends a challenge that must be returned and submitted to activate the subscription.
- Business deliveries include `X-Ramp-Webhook-ID` and `X-Ramp-Signature`; the latter is HMAC-SHA256 of the exact raw request body using the subscription secret.
- Receivers must respond within 10 seconds. Ramp retries 429, 5xx, timeouts, and connection errors up to 10 total attempts with exponential backoff and jitter.
- The same event ID is reused across retries, and events may arrive out of order.

## Instructions

1. Select only documented event types and underlying read scopes; register an HTTPS endpoint and store the returned webhook secret in an approved secret manager.

2. Complete the challenge flow and record subscription ID, state, business, events, scopes, endpoint, secret version, and owner without logging the secret.

3. Capture exact raw bytes, verify `X-Ramp-Signature` with constant-time comparison, validate expected event/business, then deduplicate by stable event ID.

4. Durably enqueue the verified event before returning 2xx within 10 seconds; process asynchronously and fetch current resource state when business action needs full or ordered data.

5. Test duplicates, invalid signature, unknown event, out-of-order events, 429/5xx retry, secret rotation, queue failure, and scheduled API reconciliation.

## Tool Discipline

- Use **Glob** to locate candidate code, manifests, fixtures, and evidence without widening scope.
- Use **Grep** to find relevant endpoints, fields, permissions, identifiers, errors, and stale assumptions.
- Use **Read** to inspect the smallest required local files and authoritative evidence.
- Use **Write** only for a new approved local draft, test, configuration, or evidence artifact.
- Use **Edit** only for a bounded approved change with a known rollback.
- Local file tools do not authorize a Ramp operation or replace owner approval.

## Approval Boundaries

Application/security owners approve endpoint and secret handling; data/finance owners approve subscribed objects and downstream actions. Production mock events require care because live receivers can process them as real activity.

## Output

A subscription inventory, challenge receipt, raw-body verification design, event ledger, durable queue, retry and dedupe tests, reconciliation job, rotation plan, and monitoring.

## Error Handling

| Condition | Response |
|---|---|
| Signature differs after parsing | Verify the original bytes before middleware mutation or JSON reserialization. |
| Processing exceeds 10 seconds | Persist the verified event and acknowledge; move business work to an asynchronous consumer. |
| An older event arrives after a newer one | Fetch current object state and apply a monotonic business transition rather than trusting arrival order. |

## Examples

### Example 1

Receive `transactions.ready_to_sync`, verify and enqueue it, fetch current transaction state, and create one idempotent ERP work item.

### Example 2

Rotate a subscription secret while proving invalid signatures fail and duplicate event IDs never duplicate effects.

## Validation

- Pending verification reaches active state through the documented challenge.
- Invalid signatures and unexpected business/event types fail before processing.
- Durable receipt, 2xx timing, duplicate, retry, and out-of-order behavior are proven.
- Periodic reconciliation detects events missed during extended downtime.

## Resources

- [Official documentation and contract notes](references/official-docs.md)
- Re-check the dated contract and current OpenAPI schema before any live request.
- Treat unresolved vendor behavior, authority, or financial state as a stop condition.
