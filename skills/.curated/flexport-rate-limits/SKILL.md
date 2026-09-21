---
name: flexport-rate-limits
description: >-
  Analyze and control Flexport request volume without inventing undocumented global limits or headers. Use when handling throttling, OAuth token budgets, endpoint-specific quotas, pagination pressure, or retry policy. Trigger with: "Flexport rate limit", "throttle Flexport calls", "budget Flexport tokens".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[surface-endpoint-and-observed-evidence]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - flexport
  - reliability
  - quotas
compatibility: 'Requires per-operation metrics, bounded queues, and current endpoint documentation or observed provider responses.'
---

# Evidence-Driven Flexport Quota Control

## Overview

Build controls from documented endpoint constraints and observed responses, not a fictional universal requests-per-minute number. The clearest fixed budget is OAuth token issuance: at most 10 token requests per day per documented credential flow.

## Prerequisites

- Inventory by OAuth, REST endpoint, and MCP tool
- Shared token cache and per-workload queues
- Observed statuses, provider messages, and latency without sensitive payloads

## Instructions

### Step 1: Separate budgets

Track token acquisition, read traffic, mutations, webhook processing, and MCP tool calls independently.

### Step 2: Eliminate token churn

Reuse each 24-hour OAuth JWT through a shared cache and single-flight refresh so business concurrency does not consume the 10/day token-request budget.

### Step 3: Honor explicit evidence

Apply endpoint-specific documented limits and provider retry signals when present. Do not assume rate-limit headers or `Retry-After` exist universally.

### Step 4: Shape reads

Use documented page sizes/cursors or links, avoid expensive expansions on index calls, and stop pagination when the business window is satisfied.

### Step 5: Serialize mutations

Queue bookings and record creation by business key, cap attempts, and reconcile ambiguous outcomes before retry.

### Step 6: Tune from receipts

Change concurrency only from measured latency/error evidence and preserve the before/after decision.

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

An importer reads freight invoices from `/invoices` in pages of 10 as recommended for performance, caches its OAuth token, limits concurrent reads based on observed behavior, and never claims a global Flexport quota that the docs do not publish.

## Error Handling

| Failure | Response |
| --- | --- |
| 429 without retry metadata | Pause the affected surface, use bounded backoff with jitter, and seek provider guidance. |
| Token requests approach 10/day | Stop acquisition and repair cache sharing before tokens expire. |
| Queue grows after concurrency increase | Roll back the increase and inspect endpoint latency/error evidence. |
| Mutation throttled | Reconcile existing business references before resubmitting. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Using API credentials](https://developers.flexport.com/tutorials/using-api-credentials/)
- [Freight invoices tutorial](https://developers.flexport.com/tutorials/freight-invoices-api-tutorial/)
- [Flexport API reference](https://apidocs.flexport.com/v3/)
