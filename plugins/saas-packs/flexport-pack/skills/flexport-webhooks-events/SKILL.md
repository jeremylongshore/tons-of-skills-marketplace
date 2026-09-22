---
name: flexport-webhooks-events
description: >-
  Verify Flexport webhook signatures on the raw request body and reconcile real event types. Use when building a receiver, rotating webhook secrets, processing shipment or purchase-order events, or recovering delivery gaps. Trigger with: "verify Flexport webhook", "handle Flexport event", "reconcile webhook gap".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[receiver-event-types-and-secret-alias]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - flexport
  - webhooks
  - security
compatibility: 'Requires a public HTTPS receiver, Flexport account Settings access, raw-body access, and a secret store.'
---

# Flexport Webhook Integrity and Reconciliation

## Overview

Authenticate before parsing. Flexport documents both SHA-1 and SHA-256 signatures, with SHA-256 recommended in `X-Hub-Signature-256`; compare against the raw UTF-8 body and treat webhook delivery as a notification that may require API reconciliation.

## Prerequisites

- Unique receiver URL and high-entropy webhook secret
- Framework support for raw request bytes before JSON parsing
- Allowlisted slash/hash event types and idempotency store

## Instructions

### Step 1: Register deliberately

Configure the callback and secret in Flexport account Settings. Record the intended event types and owner.

### Step 2: Capture raw bytes

Read the exact request body before middleware transforms encoding or JSON layout.

### Step 3: Verify SHA-256

Compute HMAC-SHA256 with the stored secret, parse `X-Hub-Signature-256`, reject malformed or unequal-length inputs, and use constant-time comparison.

### Step 4: Acknowledge quickly

After authentication and durable enqueue, return HTTP 200 promptly. Keep business processing out of the request path.

### Step 5: Deduplicate and route

Use provider event identity when present or a stable payload digest. Allow only documented names such as `/shipment#created` or `/purchase_order#updated`.

### Step 6: Reconcile gaps

Use authorized REST `/events` or resource reads when evidence indicates a delivery gap; do not invent a webhook replay endpoint or retry schedule.

## Authentication

REST calls authenticate with a cached OAuth 2.0 client-credentials Bearer token using audience `https://api.flexport.com`, or an explicitly accepted broad API key. Use distinct credentials per workload and never log credentials or tokens. MCP calls use the authenticated connection to `https://mcp.flexport.com/mcp` and remain subject to each tool's documented account permissions.

## Tool Discipline

Use Read and Grep for discovery and evidence. Use Write or Edit only for the approved artifact, code, configuration, test, or receipt described by this workflow; do not make an unapproved Flexport-side change.

## Output

- Scoped decision or implementation artifact
- Redacted operation and validation receipt
- Failure, rollback, and follow-up ownership record

Return a machine-reviewable receipt in this shape; adapt the operation values, but never place credentials or provider payloads in it:

```yaml
surface: rest-v3
operation: shipment-read
decision: approved
outcome: verified
evidence:
  release_sha: recorded-out-of-band
  provider_reference: redacted
rollback_owner: logistics-platform
```

## Examples

The receiver verifies `X-Hub-Signature-256` over untouched bytes, durably enqueues `/shipment_leg#departed`, returns 200, and lets a worker reconcile the referenced shipment before updating local state.

## Error Handling

| Failure | Response |
| --- | --- |
| Signature missing or malformed | Return an authentication failure and store no payload. |
| Digest lengths differ | Reject before constant-time comparison rather than throwing. |
| Unknown event type | Quarantine metadata and compare with current event documentation. |
| Duplicate delivery | Return success after confirming the prior durable operation. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Webhook endpoints](https://apidocs.flexport.com/v3/tag/Webhook-Endpoints/)
- [Events](https://apidocs.flexport.com/v3/tag/Event/)
- [Milestones](https://apidocs.flexport.com/v3/tag/Milestones/)
