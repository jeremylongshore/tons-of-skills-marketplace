---
name: flexport-enterprise-rbac
description: >-
  Map Flexport endpoint-scoped OAuth credentials and MCP role permissions to approved workloads. Use when designing enterprise access, separating duties, reviewing permissions, or replacing shared broad API keys. Trigger with: "Flexport RBAC", "scope Flexport integration", "review Flexport permissions".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[workloads-roles-and-endpoints]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - flexport
  - rbac
  - governance
compatibility: 'Requires Flexport administrator involvement, an enterprise identity inventory, and owners for each integration workload.'
---

# Flexport Permission-Aware Access Broker

## Overview

Flexport has two access concepts that must not be conflated: OAuth clients select endpoint resources, while MCP tools document allowed account roles. API keys are broad across endpoints and should not be described as selectively scoped.

## Prerequisites

- Workload-to-outcome inventory and accountable owners
- Current REST endpoint resource and MCP tool permission documentation
- Credential registry with environment and rotation metadata

## Instructions

### Step 1: Map business outcomes

List reads, document changes, invoice work, booking commitments, and MCP tools by workload.

### Step 2: Assign separate credentials

Create one OAuth client per system and select only required endpoint resources. Create a replacement if new resources are later needed.

### Step 3: Map MCP roles

For each MCP tool, record the documented allowed roles and verify the connected user has one; do not infer permission from a REST credential.

### Step 4: Control broad keys

Inventory API keys as exceptions, document their all-endpoint blast radius, restrict storage, and plan replacement where OAuth fits.

### Step 5: Enforce application policy

Require business authorization above provider permission, especially for bookings, trade records, and sensitive shipment/customs data.

### Step 6: Review with evidence

Quarterly or event-driven reviews compare active workloads, credentials, tool use, and owners; revoke orphaned access promptly.

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

A tracking service gets shipment-only OAuth resources, while an MCP booking assistant runs for a Member with an application-level approver gate. Neither inherits the invoice importer's credential.

## Error Handling

| Failure | Response |
| --- | --- |
| Endpoint permission absent | Create a replacement scoped client after approval; do not reuse a broad key. |
| MCP role insufficient | Route to an authorized operator or redesign the task as read-only. |
| Credential owner departed | Suspend and reassign or rotate before continued use. |
| Shared key discovered | Contain its storage and migrate workloads to distinct credentials. |

## Resources

- [First-party source notes](references/official-docs.md)
- [API credential FAQ](https://developers.flexport.com/faq/api-credentials/)
- [Using API credentials](https://developers.flexport.com/tutorials/using-api-credentials/)
- [MCP tools](https://apidocs.flexport.com/v3/tag/MCP-Tools/)
