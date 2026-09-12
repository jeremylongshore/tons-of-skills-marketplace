---
name: navan-upgrade-migration
description: >-
  Upgrade a Navan API, file, identity, or direct-integration contract without silent data loss. Use when documentation, schemas, or tenant features change. Trigger with "upgrade Navan integration", "Navan schema changed", or "migrate Navan API".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<surface> <from-revision> <to-revision>"
version: 1.9.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, navan, upgrade]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live or external Navan actions require network access and explicit approval"
---
# Navan Contract Upgrade Control

## Overview

Upgrade a Navan API, file, identity, or direct-integration contract without silent data loss. This workflow produces an auditable decision or artifact before any live action.

## Prerequisites

- Access to the selected tenant's current Navan Help Center and contracted integration documentation.
- A named business owner and data owner for the travel or expense workflow.
- A non-production evidence set with secrets and traveler data removed.

## Current Contract

Treat the tenant documentation, delivered schema, and enabled feature set as versioned evidence even when no public semantic version exists. Separate additive drift from breaking field, identity, lifecycle, or delivery changes.

## Authentication

Reconfirm scopes, host, credential format, rotation requirements, and environment separation; do not carry forward obsolete credentials merely because old calls still succeed.

## Instructions

1. Inventory current operations, fields, mappings, consumers, and controls.
2. Capture old and new contract evidence and classify every delta.
3. Update fixtures and adapters before live traffic.
4. Dual-read or shadow-process a bounded window without duplicate writes.
5. Reconcile records, totals, sensitive fields, and downstream acknowledgements.
6. Cut over with explicit stop conditions and retain a tested rollback window.

## Tool Discipline

Use Read, Glob, and Grep to inspect documentation, schemas, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Invocation alone does not authorize network access, credentials, traveler or expense data, bookings, payments, policy or identity changes, file transfers, deployments, or deletion.

## Approval Boundaries

Scope changes, new fields, credential replacement, dual-running costs, write cutover, and rollback expiry require named owner approval.

## Error Handling

- Do not silently default a newly required field.
- A successful request can still produce a semantically broken mapping.
- Freeze cutover on unexplained reconciliation deltas.

## Output

Return a contract delta, consumer impact map, fixture changes, dual-run evidence, cutover plan, and rollback deadline. Identify assumptions, owners, expirations, and evidence gaps explicitly.

## Examples

- Migrate a booking file after a column and status change.
- Rotate an identity integration while proving tenant isolation.

## Validation

Replay historical fixtures through both versions and test rollback after a partial cutover. Record expected and observed results, including fail-closed behavior.

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources and the selected tenant's in-account contract before relying on mutable endpoints, fields, entitlements, limits, or delivery behavior.
- Record tenant observations as environment-specific evidence, never universal Navan guarantees.
