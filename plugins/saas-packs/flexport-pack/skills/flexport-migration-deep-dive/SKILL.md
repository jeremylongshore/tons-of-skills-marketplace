---
name: flexport-migration-deep-dive
description: >-
  Migrate a legacy or v2-era Flexport integration to current v3 and MCP-aware contracts without unsafe concurrent production writers. Use when inventorying old endpoints, changing versions, or replacing custom workflows. Trigger with: "migrate Flexport integration", "upgrade Flexport v2", "adopt Flexport MCP".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[current-surface-and-target-outcome]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - flexport
  - migration
  - versioning
compatibility: 'Requires a legacy contract inventory, current Flexport account version context, and an authorized cutover owner.'
---

# Controlled Flexport Integration Migration

## Overview

Migration is a sequence of read-only comparison, explicit field mapping, shadow evaluation, and one controlled write owner. Never dual-book freight or dual-create trade records merely to compare systems.

## Prerequisites

- Endpoint/tool inventory with read/write classification
- Captured account default version and any `Flexport-Version` overrides
- Business-key mapping, rollback plan, and reconciliation owner

## Instructions

### Step 1: Inventory reality

Trace every legacy path, version header, response assumption, event name, expansion, credential, and mutation.

### Step 2: Map to documented targets

Choose current v3 REST endpoints or MCP tools by outcome. Record unsupported fields/operations rather than guessing equivalents.

### Step 3: Build tolerant readers

Accept documented envelopes and additive fields, preserve opaque identifiers, and add sanitized fixtures for old/new differences.

### Step 4: Shadow reads only

Compare current and target read paths over an approved sample. Normalize only business facts and investigate discrepancies.

### Step 5: Cut over one writer

Freeze the legacy mutation queue, reconcile in-flight operations, switch one authoritative writer, and retain a rapid rollback that cannot produce concurrent writes.

### Step 6: Verify and retire

Reconcile provider resources, events, and local operation keys across the cutover window before removing old credentials/code.

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

A v2-era shipment reader moves to v3 with an explicit version override and tolerant fields. Its booking path remains unchanged until a separate approved cutover can guarantee one writer and reconcile every in-flight booking.

## Error Handling

| Failure | Response |
| --- | --- |
| No mapping for a legacy field | Escalate the business dependency; do not fabricate a target. |
| Read comparison diverges | Pause cutover and verify version, expansion, pagination, and semantics. |
| Both writers become active | Freeze both, reconcile provider state, and restore one owner. |
| Rollback could duplicate freight | Do not execute it until operation identities are reconciled. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Versioning](https://apidocs.flexport.com/v3/tag/Versioning/)
- [Flexport v3 API reference](https://apidocs.flexport.com/v3/)
- [MCP tools](https://apidocs.flexport.com/v3/tag/MCP-Tools/)
