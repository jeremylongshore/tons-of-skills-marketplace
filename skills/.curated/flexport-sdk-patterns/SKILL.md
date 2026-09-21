---
name: flexport-sdk-patterns
description: >-
  Design typed adapters for Flexport REST v3 and the Flexport MCP server while preserving their different contracts. Use when building a client library, response parser, MCP transport, or shared integration boundary. Trigger with: "build Flexport client", "type Flexport responses", "connect Flexport MCP".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[language-and-required-capabilities]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - flexport
  - architecture
  - sdk
compatibility: 'Requires current Flexport v3 and MCP schemas plus a typed application language or runtime validation library.'
---

# Flexport Dual-Surface Client Contracts

## Overview

REST resources and MCP tools are two distinct public surfaces. Keep separate transports, authentication/session handling, error models, and pagination adapters behind business-level interfaces.

## Prerequisites

- Inventory of required REST endpoints and MCP tools
- Pinned account/version behavior and schema snapshot date
- Runtime validation, redaction, timeout, and test-fixture strategy

## Instructions

### Step 1: Define business ports

Express outcomes such as `readShipment`, `browseRisk`, or `evaluateRate`; keep HTTP paths and MCP JSON-RPC details behind adapters.

### Step 2: Build the REST adapter

Use base `https://api.flexport.com`, Bearer authentication, optional `Flexport-Version`, documented envelopes, status/code/message errors, and link-style pagination where documented.

### Step 3: Build the MCP adapter

Use Streamable HTTP JSON-RPC at `POST https://mcp.flexport.com/mcp`. Treat the per-tool paths shown in reference pages as synthetic documentation, not literal REST routes.

### Step 4: Validate at runtime

Accept documented additive fields, preserve opaque identifiers/cursors, and reject missing required fields without guessing replacements.

### Step 5: Normalize evidence, not schemas

Return a stable application result and surface provider metadata separately; do not force REST and MCP payloads into one lossy provider model.

### Step 6: Contract-test both surfaces

Replay sanitized official-shape fixtures for success, pagination, permission errors, additive fields, and ambiguous transport failure.

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

The application calls one `ShipmentReader` interface. Its REST adapter follows shipment pagination links; its MCP adapter sends `tools/call` for `browse_shipments` and advances `end_cursor`, while both return the same minimal internal summary.

## Error Handling

| Failure | Response |
| --- | --- |
| Synthetic tool path called as REST | Replace it with an MCP JSON-RPC `tools/call` request. |
| Unknown additive field | Preserve or ignore it safely; do not fail a tolerant reader. |
| Required field absent | Quarantine the response and compare against the current schema. |
| Transport outcome ambiguous | Reconcile the operation rather than blind-retrying a mutation. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Flexport v3 API reference](https://apidocs.flexport.com/v3/)
- [MCP tools](https://apidocs.flexport.com/v3/tag/MCP-Tools/)
- [Versioning](https://apidocs.flexport.com/v3/tag/Versioning/)
