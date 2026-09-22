---
name: flexport-observability
description: >-
  Instrument Flexport REST, MCP, OAuth, and webhook outcomes without logging logistics payloads or credentials. Use when defining metrics, traces, dashboards, or alerts. Trigger with: "monitor Flexport integration", "Flexport metrics", "trace Flexport webhooks".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[surface-and-service-objectives]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - flexport
  - observability
  - security
compatibility: 'Requires an approved telemetry platform, redaction policy, and business service objectives.'
---

# Identifier-Safe Flexport Observability

## Overview

Observe operations and reconciliation, not shipment contents. Build low-cardinality telemetry around surface, operation class, outcome, version, and queue health while keeping identifiers and payloads out.

## Prerequisites

- Approved metric labels and redaction rules
- Operation taxonomy across OAuth, REST, MCP, webhook, and local processing
- Business-defined service objectives and incident ownership

## Instructions

### Step 1: Define safe dimensions

Use environment, surface, operation class, status family, error class, version selection, and release. Exclude URLs with IDs, names, emails, routes, tags, documents, tokens, and raw messages.

### Step 2: Measure auth health

Track cache hit, refresh success, token-request count, and credential alias as a controlled internal dimension; never log tokens or secret fragments.

### Step 3: Measure reads and mutations separately

Record latency, attempts, pages, queue age, reconciliation lag, and ambiguous outcomes by operation class.

### Step 4: Measure webhooks in stages

Distinguish received, signature-valid, durably queued, deduplicated, processed, and reconciled counts.

### Step 5: Alert on objectives

Derive thresholds from approved freshness, queue, and error objectives—not arbitrary fixed seconds or undocumented rate headers.

### Step 6: Audit telemetry

Sample schemas and label cardinality for sensitive leakage and regressions before expanding collection.

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

A dashboard shows `surface=mcp`, `operation=shipment-read`, outcome, latency, and reconciliation lag. It never labels a series with FLEX-ID, route, company, email, or tool arguments.

## Error Handling

| Failure | Response |
| --- | --- |
| Identifier appears in labels | Drop or hash only under approved policy, then control cardinality. |
| Raw provider message contains data | Map to a safe error class and protect restricted details separately. |
| Alert has no business objective | Disable it until an owner defines the decision it drives. |
| Webhook counts diverge | Bound the window and run authenticated reconciliation. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Flexport v3 API reference](https://apidocs.flexport.com/v3/)
- [MCP tools](https://apidocs.flexport.com/v3/tag/MCP-Tools/)
- [Webhook endpoints](https://apidocs.flexport.com/v3/tag/Webhook-Endpoints/)
