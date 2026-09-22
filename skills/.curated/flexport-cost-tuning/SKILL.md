---
name: flexport-cost-tuning
description: >-
  Reduce unnecessary Flexport traffic and processing without making unsupported API pricing claims. Use when tuning polling, pagination, payload expansion, cache freshness, or reconciliation volume. Trigger with: "optimize Flexport requests", "reduce Flexport polling", "tune shipment freshness".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[workload-freshness-objective]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - flexport
  - optimization
  - operations
compatibility: 'Requires request metrics, business freshness objectives, and current endpoint pagination/expansion documentation.'
---

# Flexport Request-Volume and Freshness Tuning

## Overview

Optimize volume and latency against business freshness, not a fabricated per-request bill. Prefer event-driven invalidation plus bounded reconciliation and measured page/expansion choices.

## Prerequisites

- Baseline request counts by operation and outcome
- Business-approved freshness and recovery windows
- Metrics for pages read, expansions, cache hits, and reconciliation lag

## Instructions

### Step 1: Name the outcome

Tie each request to shipment tracking, trade document ingestion, invoice reconciliation, or booking—not generic synchronization.

### Step 2: Set freshness classes

Define active-shipment, completed-shipment, invoice, and reference-data windows from operational need; do not hard-code invented provider change rates.

### Step 3: Use events as hints

Let authenticated webhooks trigger targeted reads, then run bounded periodic reconciliation for missed deliveries.

### Step 4: Trim reads

Stop pagination at the required window, request only supported expansions, and avoid expansion on invoice index calls where Flexport recommends against it.

### Step 5: Cache safely

Cache read-only reference results under an explicit TTL and invalidate on evidence; never cache credentials, authorization decisions, or mutable booking approval.

### Step 6: Prove the change

Compare request count, stale-result rate, reconciliation time, and provider errors before and after; roll back if correctness worsens.

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

A shipment dashboard refreshes active records from verified events and a bounded reconciler, while completed shipments use a longer application TTL. The report claims fewer requests, not undocumented Flexport cost savings.

## Error Handling

| Failure | Response |
| --- | --- |
| Freshness objective absent | Stop optimization until the business owner defines acceptable staleness. |
| Cache serves stale critical state | Bypass and reconcile, then shorten or event-invalidate that class. |
| Expansion causes latency | Remove it from index calls and fetch detail only for selected records. |
| Volume drops but gaps rise | Roll back and restore the last proven reconciliation window. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Shipment API tutorial](https://developers.flexport.com/tutorials/shipment-api-tutorial/)
- [Freight invoices tutorial](https://developers.flexport.com/tutorials/freight-invoices-api-tutorial/)
- [Events](https://apidocs.flexport.com/v3/tag/Event/)
