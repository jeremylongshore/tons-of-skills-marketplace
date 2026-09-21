---
name: flexport-local-dev-loop
description: >-
  Develop Flexport integrations locally with sanitized contract fixtures and explicit live-test boundaries. Use when implementing REST v3 parsers, MCP tool adapters, webhook verification, or failure handling. Trigger with: "develop Flexport locally", "mock Flexport API", "test Flexport webhook".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[surface-and-feature]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - flexport
  - development
  - testing
compatibility: 'Requires a local test runner and sanitized fixtures; live credentials are optional and must use an approved account.'
---

# Flexport Contract-Fixture Development Loop

## Overview

Most development should run without credentials. Model official v3, MCP, and webhook shapes as fixtures, then use a separately approved read-only live smoke test only for gaps fixtures cannot prove.

## Prerequisites

- Current first-party schema pages and snapshot date
- Sanitized success, pagination, additive-field, and error fixtures
- Separate local secret injection and no-production-data rule

## Instructions

### Step 1: Choose one contract

Name the exact REST endpoint, MCP tool, or webhook event and expected business outcome.

### Step 2: Capture shape, not data

Build synthetic fixtures from documented field names/types. Replace all identifiers, routes, parties, financials, and document content.

### Step 3: Test invariants

Cover required fields, unknown additive fields, opaque cursors/links, status/code/message errors, and missing authorization.

### Step 4: Exercise raw webhooks

Sign exact synthetic bytes with a test secret and test malformed, wrong-length, duplicate, and valid SHA-256 signatures before parsing.

### Step 5: Gate live checks

If needed, use an approved credential for one read-only operation. Never create bookings, documents, purchase orders, or invoices from the local loop.

### Step 6: Promote the receipt

Commit fixtures and assertions, not tokens or live payloads; record schema source and review date.

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

A developer implements `browse_shipments` pagination using synthetic `end_cursor` fixtures, adds an unknown field to prove tolerant parsing, and keeps the real MCP connection disabled in default tests.

## Error Handling

| Failure | Response |
| --- | --- |
| Fixture contains live data | Replace it with synthetic values and purge the original from artifacts. |
| Docs and observed shape differ | Record a minimal field-name diff and verify version/account context. |
| Test requests a mutation | Block it at the adapter and require an explicit higher environment. |
| Credential discovered in repository | Revoke or rotate, remove it from history, and repair secret injection. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Flexport v3 API reference](https://apidocs.flexport.com/v3/)
- [MCP tools](https://apidocs.flexport.com/v3/tag/MCP-Tools/)
- [Webhook endpoints](https://apidocs.flexport.com/v3/tag/Webhook-Endpoints/)
