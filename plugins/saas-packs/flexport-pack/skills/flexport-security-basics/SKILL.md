---
name: flexport-security-basics
description: >-
  Analyze and harden Flexport credentials, tokens, webhook verification, data exposure, and mutation controls. Use when performing threat modeling, security review, credential rotation, or receiver implementation. Trigger with: "secure Flexport integration", "review Flexport secrets", "Flexport webhook security".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[integration-and-threat-model]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - flexport
  - security
  - hardening
compatibility: 'Requires an approved secret store, TLS egress/ingress, access review, and incident response.'
---

# Flexport Integration Security Baseline

## Overview

Protect four high-value boundaries: OAuth/API credentials, cached tokens, webhook secrets/raw bodies, and business mutations that can create freight or trade records.

## Prerequisites

- Threat model with account, workload, and data boundaries
- Endpoint-scoped credential plan and broad-key exception register
- Secret scanning, redacted telemetry, rotation, and incident procedures

## Instructions

### Step 1: Minimize credentials

Prefer distinct endpoint-scoped OAuth clients. Treat API keys as broad-access exceptions and never record secret values or suffixes.

### Step 2: Protect tokens

Request with the documented audience/grant, cache encrypted 24-hour JWTs, single-flight refresh, and never pass tokens through browser state or logs.

### Step 3: Authenticate webhooks first

Verify raw-body HMAC-SHA256 from `X-Hub-Signature-256`, reject malformed/length-mismatched values, then parse and enqueue.

### Step 4: Constrain egress and input

Allow documented Flexport hosts, validate schemas and sizes, preserve opaque IDs, and reject unexpected mutation intent.

### Step 5: Guard mutations

Require business authorization, durable operation keys, one writer, and reconciliation before retrying bookings or record creation.

### Step 6: Exercise response

Test credential revocation, webhook secret rotation, log leakage, provider outage, and rollback with metadata-only evidence.

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

A shipment reader and invoice importer use different scoped OAuth clients. A leaked client triggers revocation and replacement of only that workload, while webhook processing remains isolated behind its own secret.

## Error Handling

| Failure | Response |
| --- | --- |
| Credential committed or logged | Revoke/rotate, contain the artifact, and repair injection/redaction. |
| Signature checked after JSON parsing | Reject the implementation and restore raw-body verification. |
| Broad key used by many workloads | Segment and migrate to scoped clients. |
| Uncertain booking retry requested | Block it until provider state is reconciled. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Using API credentials](https://developers.flexport.com/tutorials/using-api-credentials/)
- [API credential FAQ](https://developers.flexport.com/faq/api-credentials/)
- [Webhook endpoints](https://apidocs.flexport.com/v3/tag/Webhook-Endpoints/)
