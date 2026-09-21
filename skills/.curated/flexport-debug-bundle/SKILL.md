---
name: flexport-debug-bundle
description: >-
  Assemble a metadata-only Flexport diagnostic package without sweeping environment files, logs, or payloads. Use when escalating an API, MCP, OAuth, or webhook defect. Trigger with: "create Flexport debug bundle", "escalate Flexport issue", "collect Flexport diagnostics".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[incident-id-and-failing-operation]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - flexport
  - debugging
  - support
compatibility: 'Requires an incident workspace, approved redaction policy, and a named recipient for the diagnostic manifest.'
---

# Redacted Flexport Diagnostic Manifest

## Overview

Collect the smallest evidence that can distinguish contract, permission, version, transport, and provider failures. Never archive an entire environment, log directory, request body, webhook payload, or credential file.

## Prerequisites

- Incident ID, time window, surface, and failing operation
- Approved redaction rules and evidence recipient
- Known credential alias, application release, and expected Flexport version

## Instructions

### Step 1: Set an allowlist

Declare exact metadata fields before collection: timestamps, release SHA, surface, operation, version header, status/code/message, correlation ID, and payload digest.

### Step 2: Collect configuration shape

Record variable names, endpoint hosts, feature flags, and credential aliases—not values, tokens, secret suffixes, or `.env` content.

### Step 3: Summarize attempts

List bounded attempt timestamps and outcomes. Exclude raw request/response bodies, document data, route details, names, emails, and addresses.

### Step 4: Add contract evidence

Include a minimal sanitized fixture or field-name diff only when necessary to reproduce the failure.

### Step 5: Review twice

Run automated secret/sensitive-data scanning, then require a human owner to approve the exact manifest and recipient.

### Step 6: Transfer and expire

Use the approved support channel, record a checksum and expiry, then delete according to incident evidence policy.

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

A webhook escalation contains the receiver release SHA, event-type string, signature-header presence, body digest, status outcome, and timestamps. It contains neither the webhook body nor the secret.

## Error Handling

| Failure | Response |
| --- | --- |
| Secret scanner fires | Stop transfer, remove the material, rotate if exposure occurred, and rescan. |
| Payload needed for reproduction | Create a synthetic minimal fixture rather than shipping production content. |
| Recipient or purpose unclear | Do not build or send the manifest. |
| Archive tool proposes broad paths | Reject it and use the explicit allowlist only. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Flexport v3 API reference](https://apidocs.flexport.com/v3/)
- [Webhook endpoints](https://apidocs.flexport.com/v3/tag/Webhook-Endpoints/)
- [API credential FAQ](https://developers.flexport.com/faq/api-credentials/)
