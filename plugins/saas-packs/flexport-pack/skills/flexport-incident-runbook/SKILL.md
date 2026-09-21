---
name: flexport-incident-runbook
description: >-
  Analyze, contain, and reconcile a Flexport integration incident without unsafe retries or invented webhook replay APIs. Use when events stop, payload parsing fails, credentials break, or mutation outcomes are uncertain. Trigger with: "Flexport incident", "missing Flexport events", "reconcile Flexport outage".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[incident-window-and-affected-surface]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - flexport
  - incident-response
  - reconciliation
compatibility: 'Requires an incident commander, read access to redacted telemetry, and an approved reconciliation credential.'
---

# Flexport Delivery-Gap Incident Runbook

## Overview

Preserve freight correctness first. Freeze uncertain mutations, separate provider delivery from local processing, and reconstruct affected state with documented resource/event reads.

## Prerequisites

- Incident owner, severity, start time, and affected tenant/workflow
- Last known good release and configuration
- Bounded reconciliation query and business owners for disputed state

## Instructions

### Step 1: Contain

Disable automatic bookings and affected writes. Keep authenticated webhook acceptance only if durable enqueue and deduplication remain correct.

### Step 2: Bound the window

Identify first/last bad receipt by surface, operation, release, credential alias, and version without examining broad sensitive payloads.

### Step 3: Split failure domains

Test OAuth, REST read, MCP connection, webhook ingress, queue processing, and downstream state independently.

### Step 4: Reconcile read-only

Use `/events` or affected resource reads to compare provider state with durable local operation keys. Do not assume Flexport exposes a webhook replay endpoint.

### Step 5: Repair deterministically

Reprocess authenticated durable events or apply approved state corrections exactly once; reconcile uncertain creates/bookings before retry.

### Step 6: Recover and learn

Restore traffic by cohort, verify the full incident window, rotate exposed credentials if needed, and add a sanitized regression fixture.

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

A receiver deployment parsed bodies before signature validation and dropped events. The team restores the prior release, queries the bounded event/resource window, deduplicates by durable operation identity, and backfills only missing local transitions.

## Error Handling

| Failure | Response |
| --- | --- |
| Provider reads unavailable | Maintain the mutation freeze and preserve the reconciliation window. |
| Duplicate business action found | Stop workers and choose one authoritative provider resource. |
| Event type newly additive | Update tolerant routing and replay only authenticated durable items. |
| Incident needs sensitive payload | Escalate access and minimize fields rather than copying broad logs. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Events](https://apidocs.flexport.com/v3/tag/Event/)
- [Shipment API tutorial](https://developers.flexport.com/tutorials/shipment-api-tutorial/)
- [Webhook endpoints](https://apidocs.flexport.com/v3/tag/Webhook-Endpoints/)
