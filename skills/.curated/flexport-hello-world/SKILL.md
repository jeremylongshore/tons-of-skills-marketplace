---
name: flexport-hello-world
description: >-
  Prove a Flexport integration with one read-only shipment request and a defensively parsed receipt. Use when validating new credentials, network access, version selection, or response handling. Trigger with: "test Flexport API", "Flexport hello world", "verify shipment access".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[credential-alias-and-test-scope]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - flexport
  - validation
  - shipments
compatibility: 'Requires approved Flexport credentials and access to a tenant with a non-sensitive testable shipment or empty-list response.'
---

# Read-Only Flexport v3 Proof

## Overview

Establish connectivity without creating freight, documents, or bookings. Pin the intended API version, accept documented response wrappers, and preserve only a redacted proof.

## Prerequisites

- Approved read-only credential and credential alias
- Known account API version or explicit `Flexport-Version` choice
- A test policy that permits either one shipment reference or an empty list

## Instructions

### Step 1: Define the proof

Set the expected account, endpoint, version, and allowed evidence before making a call.

### Step 2: Acquire authentication

Reuse a cached OAuth client-credentials token, or use an explicitly approved API key. Keep the credential out of command text and logs.

### Step 3: Request shipments

Send `GET https://api.flexport.com/shipments` with Bearer authorization, JSON acceptance, and `Flexport-Version: 3` when an explicit v3 override is intended.

### Step 4: Parse defensively

Read the documented response envelope and pagination links without assuming invented ID prefixes, undocumented nested records, or a fixed set of additive fields.

### Step 5: Validate tenant safety

Confirm the response belongs to the intended account and emit only count, HTTP status, selected version, and a hashed operation identifier.

### Step 6: Fail closed

Do not progress from a successful read to document creation, booking, or mutation. Make the next action a separate approved workflow.

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

A deployment probe requests the first shipment page with a cached OAuth token, confirms HTTP 200 and the intended version, records `count=0` or a redacted count, then exits without following pagination.

## Error Handling

| Failure | Response |
| --- | --- |
| 401 response | Refresh once through the shared cache, then inspect credential state instead of retrying. |
| 403 response | Check endpoint resources and account access; do not switch to a broad key automatically. |
| Unexpected schema | Capture field names and version only, then compare with current v3 documentation. |
| Non-empty sensitive payload | Discard payload content and keep a metadata-only receipt. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Shipment API tutorial](https://developers.flexport.com/tutorials/shipment-api-tutorial/)
- [Versioning](https://apidocs.flexport.com/v3/tag/Versioning/)
- [Flexport API reference](https://apidocs.flexport.com/v3/)
