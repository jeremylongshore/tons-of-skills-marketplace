---
name: flexport-reference-architecture
description: >-
  Analyze and design a Flexport integration that separates REST v3 resources, MCP tools, webhook ingress, approval, and reconciliation. Use when producing an architecture, threat model, or service boundary. Trigger with: "design Flexport architecture", "Flexport MCP architecture", "Flexport integration boundaries".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[capabilities-and-trust-boundaries]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - flexport
  - architecture
  - design
compatibility: 'Requires approved Flexport capabilities, account context, and organizational security/data constraints.'
---

# Flexport REST, MCP, and Webhook Architecture

## Overview

Use three explicit provider planes: REST v3 for resource operations, MCP Streamable HTTP JSON-RPC for permissioned assistant tools, and signed webhooks for notifications. Join them only through durable application policy and reconciliation.

## Prerequisites

- Capability inventory split into reads, mutations, events, and assistant tools
- Identity, account, environment, and data-flow boundaries
- Business approval, operation ledger, queue, and recovery requirements

## Instructions

### Step 1: Draw provider surfaces

Show `api.flexport.com`, `mcp.flexport.com/mcp`, and public HTTPS webhook ingress as distinct external nodes.

### Step 2: Place credential boundaries

Use endpoint-scoped OAuth clients per REST workload, authenticated MCP sessions with documented tool roles, and a separate webhook secret.

### Step 3: Separate control and data

Put business approval and policy before booking/trade mutations; keep payload handling in minimized data services.

### Step 4: Add durable state

Persist operation keys, provider references, event dedupe state, cursor/link checkpoints, and redacted outcomes.

### Step 5: Add reconciliation

Connect events and uncertain outcomes to authorized REST/resource reads. Never make webhook delivery the sole source of truth.

### Step 6: Prove failure paths

Model token-cache failure, permission denial, additive schema change, duplicate/missing event, ambiguous mutation, and rollback.

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

A booking assistant queries rates through MCP, sends an exact candidate to an approval service, and records one operation key before booking. Signed events enqueue notifications, while a reconciler reads provider state to close gaps.

## Error Handling

| Failure | Response |
| --- | --- |
| REST and MCP contracts collapsed | Split transport, auth/session, errors, and pagination before implementation. |
| Webhook directly mutates core state | Insert verified durable enqueue and reconciliation. |
| Approval follows booking | Move it before the provider mutation. |
| Architecture logs payloads | Replace them with redacted operation receipts. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Flexport v3 API reference](https://apidocs.flexport.com/v3/)
- [MCP tools](https://apidocs.flexport.com/v3/tag/MCP-Tools/)
- [Webhook endpoints](https://apidocs.flexport.com/v3/tag/Webhook-Endpoints/)
