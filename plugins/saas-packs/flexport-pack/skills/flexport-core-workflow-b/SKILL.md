---
name: flexport-core-workflow-b
description: >-
  Create and reconcile Flexport purchase orders, commercial invoices, and shipment documents without inventing update semantics. Use when moving approved trade data into Flexport or attaching documents. Trigger with: "create Flexport purchase order", "upload Flexport document", "submit commercial invoice".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[document-type-and-approved-record]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - flexport
  - documents
  - trade
compatibility: 'Requires endpoint-scoped Flexport credentials, approved trade data, and any account enablement required for commercial invoices.'
---

# Flexport Trade Document Workflow

## Overview

Treat structured trade records and uploaded files as separate governed operations. Validate referenced network entities first, apply only documented create/update behavior, and never assume an uploaded document can be updated in place.

## Prerequisites

- Approved source record and data owner
- Resolved Flexport entity, location, shipment, and product references
- Document malware scan, MIME policy, and retention decision

## Instructions

### Step 1: Select the resource

Choose purchase order, commercial invoice, or document from the business outcome; do not overload one endpoint with another resource's fields.

### Step 2: Resolve references

Verify network entity, location, shipment, and product identifiers with read-only lookups before mutation.

### Step 3: Validate permissions

Confirm the OAuth credential includes the required endpoint resource. Commercial invoice create/update also requires Flexport-side enablement and permission.

### Step 4: Submit once

Persist an operation digest, then use the documented endpoint: `/purchase_orders`, `/commercial_invoices`, or `/documents`. Base64 document content must remain within the documented 10 MB pre-encoding limit.

### Step 5: Reconcile the result

Store opaque returned IDs and retrieve the resource. For documents, replace through an approved new upload rather than inventing an update call.

### Step 6: Record lineage

Link the Flexport resource to the approved source revision, actor, version header, and redacted outcome.

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

A validated commercial invoice is enabled for the client, submitted once, read back by its opaque ID, and linked to the source revision. A corrected file becomes a separately approved document rather than an undocumented in-place edit.

## Error Handling

| Failure | Response |
| --- | --- |
| 422 response | Correct the source payload; do not retry unchanged validation failures. |
| Commercial invoice disabled | Stop and request Flexport enablement/permission. |
| Document too large | Reject before base64 encoding and route to an approved alternative. |
| Ambiguous create | Retrieve or reconcile by known business references before resubmission. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Purchase order tutorial](https://developers.flexport.com/tutorials/purchase-order-api-tutorial/)
- [Commercial invoice tutorial](https://developers.flexport.com/tutorials/commercial-invoices-api-tutorial/)
- [Documents tutorial](https://developers.flexport.com/tutorials/documents-api-tutorial/)
