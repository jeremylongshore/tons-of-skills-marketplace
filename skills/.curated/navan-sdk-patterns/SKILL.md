---
name: navan-sdk-patterns
description: >-
  Design an application-owned Navan adapter pinned to the tenant's actual integration contract. Use when wrapping Booking API, Expense API, SFTP, or direct integration behavior. Trigger with "build a Navan client", "wrap Navan API", or "type Navan responses".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<surface> <contract-revision> <language>"
version: 1.9.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, navan, adapter]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live or external Navan actions require network access and explicit approval"
---
# Navan Contract-Bound Adapter

## Overview

Design an application-owned Navan adapter pinned to the tenant's actual integration contract. This workflow produces an auditable decision or artifact before any live action.

## Prerequisites

- Access to the selected tenant's current Navan Help Center and contracted integration documentation.
- A named business owner and data owner for the travel or expense workflow.
- A non-production evidence set with secrets and traveler data removed.

## Current Contract

Do not assume a public SDK, base URL, pagination model, or error envelope. Preserve the vendor payload at the boundary, then map it into versioned application types backed by captured schemas and fixtures.

## Authentication

Accept a secret-provider callback or file-transfer credential reference, never a literal secret. Bind credentials, tenant identity, and host allowlist together so configuration cannot cross environments.

## Instructions

1. Inventory the enabled operation or file contract and record its revision.
2. Define transport-neutral input, result, page, and error types.
3. Implement authentication, timeout, size limit, and redacted telemetry at one boundary.
4. Preserve raw identifiers as opaque strings and money with explicit currency.
5. Add fixture tests for success, empty data, pagination, denial, throttling, and drift.
6. Expose writes only as separate methods with idempotency and approval requirements.

## Tool Discipline

Use Read, Glob, and Grep to inspect documentation, schemas, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Invocation alone does not authorize network access, credentials, traveler or expense data, bookings, payments, policy or identity changes, file transfers, deployments, or deletion.

## Approval Boundaries

Reading docs and fixtures is local; live calls, secrets, package additions, generated clients, file transfers, and state changes need explicit approval.

## Error Handling

- Unknown fields should be preserved or quarantined, not silently discarded.
- Do not guess retryability from status alone; follow the current tenant contract.
- Reject tenant/host mismatches before opening a connection.

## Output

Return adapter interfaces, contract revision, fixture inventory, redaction policy, retry classification, and unsupported operations. Identify assumptions, owners, expirations, and evidence gaps explicitly.

## Examples

- Wrap a contracted booking export behind an async iterator.
- Map expense money fields into amount-plus-currency values.

## Validation

Test offline first, then use one separately approved non-production read to compare the captured schema with reality. Record expected and observed results, including fail-closed behavior.

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources and the selected tenant's in-account contract before relying on mutable endpoints, fields, entitlements, limits, or delivery behavior.
- Record tenant observations as environment-specific evidence, never universal Navan guarantees.
