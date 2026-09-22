---
name: flexport-performance-tuning
description: >-
  Tune Flexport integration latency and throughput from measured pagination, expansion, and concurrency evidence. Use when reads are slow, backlogs grow, or MCP browsing needs scaling. Trigger with: "speed up Flexport integration", "tune Flexport pagination", "scale shipment reads".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[operation-and-baseline]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - flexport
  - performance
  - pagination
compatibility: 'Requires representative sanitized workloads, per-operation metrics, and rollback controls.'
---

# Measured Flexport Pagination and Concurrency

## Overview

Performance tuning must preserve correctness, account boundaries, and provider stability. Change one pagination, expansion, cache, or concurrency control at a time and validate full reconciliation.

## Prerequisites

- Baseline latency, pages, payload size, errors, and business freshness
- Documented pagination model for the selected REST endpoint or MCP tool
- Bounded worker pool and reversible configuration

## Instructions

### Step 1: Select one bottleneck

Name the operation, surface, dataset window, and business objective. Exclude token acquisition from request concurrency by using a shared cache.

### Step 2: Use native pagination

Follow REST response links where documented; for MCP `browse_shipments`, advance `end_cursor` while `has_next_page` is true and keep `first` within 1–100.

### Step 3: Control expansions

Avoid expansion on freight-invoice index calls as recommended; fetch detail only for records that need it.

### Step 4: Increase cautiously

Raise one page-size or worker limit for read-only work, measure latency/error/backlog effects, and stop on provider or correctness degradation.

### Step 5: Protect mutations

Keep bookings and trade-record writes serialized by business key and outside bulk read tuning.

### Step 6: Reconcile the result

Compare counts and terminal cursors/links over the same bounded window, then document the chosen control and rollback.

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

A shipment-risk scanner tests MCP page sizes of 10 and 50 on the same approved window, verifies identical shipment identities and terminal cursor state, then adopts the faster setting with a bounded worker pool.

## Error Handling

| Failure | Response |
| --- | --- |
| Result counts differ | Reject the tuning change and inspect cursor/link handling. |
| Latency improves but errors rise | Roll back concurrency and reassess the bottleneck. |
| Index expansion dominates payload | Remove it and fetch selected details separately. |
| Mutation entered bulk pool | Drain safely, reconcile outcomes, and restore per-key serialization. |

## Resources

- [First-party source notes](references/official-docs.md)
- [MCP tools](https://apidocs.flexport.com/v3/tag/MCP-Tools/)
- [Freight invoices tutorial](https://developers.flexport.com/tutorials/freight-invoices-api-tutorial/)
- [Shipment API tutorial](https://developers.flexport.com/tutorials/shipment-api-tutorial/)
