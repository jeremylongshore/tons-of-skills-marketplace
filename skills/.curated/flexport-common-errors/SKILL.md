---
name: flexport-common-errors
description: >-
  Classify Flexport REST, OAuth, webhook, and MCP failures into safe operator actions. Use when triaging status/code/message errors, permission failures, validation problems, or ambiguous mutations. Trigger with: "debug Flexport error", "Flexport 422", "Flexport permission denied".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[redacted-failure-receipt]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - flexport
  - errors
  - operations
compatibility: 'Requires a redacted response receipt with surface, operation, HTTP or JSON-RPC status, and correlation metadata.'
---

# Flexport Failure Classification

## Overview

Do not convert every failure into a retry. First identify the surface and operation class, then distinguish authentication, authorization, validation, provider availability, and ambiguous mutation outcomes.

## Prerequisites

- Redacted surface and operation name
- HTTP status or JSON-RPC error plus documented provider code/message
- Knowledge of whether the failed operation could mutate freight or trade records

## Instructions

### Step 1: Identify the surface

Label OAuth token, REST v3, MCP JSON-RPC, or webhook delivery; each has different failure semantics.

### Step 2: Protect evidence

Capture timestamp, credential alias, version header, operation digest, status/code/message, and provider correlation metadata without payloads or secrets.

### Step 3: Classify deterministically

Separate 401 authentication, 403 permission/scope, 404 resource or route, 400/422 request validation, throttling evidence, and 5xx/transport uncertainty.

### Step 4: Choose retry eligibility

Retry only transient, idempotent work with bounded backoff. Never retry a create or booking until its prior outcome is reconciled.

### Step 5: Correct the owner

Route credential issues to credential owners, schema issues to integration owners, business validation to data owners, and provider incidents to support.

### Step 6: Close with a proof

Record the corrected contract or recovered result and add a regression fixture when the defect was local.

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

A document upload returns 422 with a provider message. The operator preserves the code/message, fixes the source document metadata, and submits a new approved operation rather than repeatedly sending the unchanged payload.

## Error Handling

| Failure | Response |
| --- | --- |
| 401 persists after one cached-token refresh | Stop and inspect credential revocation, audience, and secret source. |
| 403 on one endpoint | Verify OAuth endpoint resources or MCP role permission; do not broaden silently. |
| 404 on `/tools/...` | Use the real MCP JSON-RPC endpoint rather than the synthetic docs path. |
| Timeout after mutation | Reconcile using known references before any retry. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Flexport v3 API reference](https://apidocs.flexport.com/v3/)
- [API credential FAQ](https://developers.flexport.com/faq/api-credentials/)
- [MCP tools](https://apidocs.flexport.com/v3/tag/MCP-Tools/)
