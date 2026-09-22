---
name: flexport-prod-checklist
description: >-
  Validate and gate a Flexport integration for production with evidence across auth, versioning, data, mutations, webhooks, recovery, and rollback. Use when preparing to enable live traffic or a new provider capability. Trigger with: "Flexport production checklist", "launch Flexport integration", "go live with Flexport".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[release-sha-and-approved-capabilities]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - flexport
  - production
  - readiness
compatibility: 'Requires accountable engineering, security, data, and business owners plus a tested rollback.'
---

# Flexport Production Readiness Gate

## Overview

A checklist item passes only with a receipt tied to the immutable release and configuration. Read access, bookings, trade records, and webhook processing have different risk boundaries and must be approved separately.

## Prerequisites

- Immutable release SHA and environment manifest
- Named technical, security/data, and business approvers
- Read-only canary, reconciliation plan, incident owner, and rollback

## Instructions

### Step 1: Gate identity and auth

Verify account, credential alias/type, endpoint resources, token caching, secret injection, revocation, and MCP role permissions where used.

### Step 2: Gate contracts

Confirm v3/account version behavior, tolerant additive-field parsing, documented endpoints/tools, error classification, and pagination.

### Step 3: Gate data

Approve field minimization, destinations, telemetry redaction, retention/deletion, and tenant boundaries.

### Step 4: Gate mutations

Require durable operation keys, business approval for bookings/writes, ambiguous-outcome reconciliation, and one authoritative writer.

### Step 5: Gate webhooks

Prove raw-body `X-Hub-Signature-256` validation, durable enqueue before 200, deduplication, event allowlist, and gap reconciliation.

### Step 6: Gate launch and rollback

Run a read-only canary, expand by cohort, test rollback, and attach all receipts to the release decision.

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

The launch record enables shipment reads and signed webhook ingestion but leaves booking disabled because its human approval and ambiguous-outcome reconciliation evidence is incomplete.

## Error Handling

| Failure | Response |
| --- | --- |
| Evidence belongs to another SHA | Re-run the gate on the release candidate. |
| Owner or rollback absent | Do not launch. |
| Broad API key lacks exception | Replace it or obtain explicit risk acceptance. |
| Mutation reconciliation unproven | Keep that capability disabled. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Flexport v3 API reference](https://apidocs.flexport.com/v3/)
- [Using API credentials](https://developers.flexport.com/tutorials/using-api-credentials/)
- [Webhook endpoints](https://apidocs.flexport.com/v3/tag/Webhook-Endpoints/)
