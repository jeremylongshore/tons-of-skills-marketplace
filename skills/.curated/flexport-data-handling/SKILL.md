---
name: flexport-data-handling
description: >-
  Analyze, minimize, and govern Flexport shipment, customs, invoice, purchase-order, and document data. Use when mapping fields, designing storage, exporting records, or setting retention with the real data owner. Trigger with: "handle Flexport data", "minimize shipment fields", "govern Flexport documents".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[data-flow-and-approved-purpose]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - flexport
  - data-governance
  - privacy
compatibility: 'Requires a data owner, approved purpose, destination controls, and organization-specific legal/security policy.'
---

# Flexport Logistics Data Minimization

## Overview

Flexport payloads can contain commercial, personal, customs, financial, and document content. This skill does not invent universal GDPR, CCPA, ITAR, or retention rules; it makes the accountable owner and policy explicit.

## Prerequisites

- Documented purpose and accountable data owner
- Field-level source-to-destination map
- Approved classification, residency, access, retention, and deletion policy

## Instructions

### Step 1: Inventory exact fields

Map only fields needed for the approved outcome, including identifiers embedded in routes, parties, documents, invoices, customs, tags, or MCP tracking output.

### Step 2: Classify with policy

Apply the organization's authoritative classification and legal guidance. Do not infer a regime from an HS code, endpoint, country, or shipment mode.

### Step 3: Minimize collection

Prefer opaque resource IDs and derived operational state over raw documents, addresses, names, emails, entry numbers, or charge details.

### Step 4: Protect transport and storage

Use approved encrypted channels and stores, workload-scoped credentials, tenant boundaries, and access logging.

### Step 5: Control outputs

Redact logs, metrics, prompts, tickets, debug bundles, and analytics. Never include document bodies, tokens, or full route/party payloads by default.

### Step 6: Enforce lifecycle

Attach retention/deletion rules to the approved data class, test deletion and backup behavior, and record exceptions with owner and expiry.

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

A delay alert stores a shipment's opaque Flexport ID, milestone category, and alert state. It does not copy route addresses, customs entries, tags, or document content into observability systems.

## Error Handling

| Failure | Response |
| --- | --- |
| Purpose cannot justify a field | Remove it before ingestion. |
| Destination lacks approved controls | Block export and route to the data owner. |
| Legal rule uncertain | Ask counsel or policy owner; do not encode a guessed retention period. |
| Sensitive data reaches logs | Contain access, purge where possible, and repair redaction. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Shipment API tutorial](https://developers.flexport.com/tutorials/shipment-api-tutorial/)
- [Documents tutorial](https://developers.flexport.com/tutorials/documents-api-tutorial/)
- [Customs entries tutorial](https://developers.flexport.com/tutorials/customs-entries-api-tutorial/)
