---
name: ramp-migration-deep-dive
description: >-
  Plan and execute a controlled migration from a legacy expense or card platform to Ramp with identity, spend-control, open-item, and accounting reconciliation. Use when an enterprise cutover requires parallel run and rollback. Trigger with "migrate to Ramp" or "Ramp cutover plan".
allowed-tools: Read,Glob,Grep,Write,Edit
version: 2.0.0
argument-hint: "[integration-or-environment]"
model: inherit
effort: high
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Requires current Ramp Developer API documentation and approved access for any live financial, card, identity, accounting, application, or configuration change
tags: [saas, ramp, migration, cutover, reconciliation]
---
# Legacy Expense Platform to Ramp Migration

## Overview

Treat the migration as a sequence of independently reconciled cohorts, not a bulk import. Map business meaning before identifiers, keep legacy and Ramp authority explicit during coexistence, and retire the old platform only after financial close.

## Prerequisites

- Identify the Ramp application, environment, business entities, affected data and workflows, accountable owner, and rollback boundary.
- Read `references/official-docs.md` and re-check endpoint schemas, scopes, limits, and support status before a live operation.
- Use synthetic fixtures or Ramp sandbox until production access and business effects are explicitly approved.
- Prepare approved secret storage and a sanitized evidence location.

## Current Contract

- Ramp users, entities, funds, cards, transactions, bills, reimbursements, vendors, and accounting objects have distinct relationships and endpoint contracts.
- Current virtual-card authority is fund-backed and governed through spend controls; legacy card abstractions should not be mapped one-to-one without review.
- Accounting connections distinguish Ramp identifiers from ERP remote identifiers and require explicit sync receipts.
- Webhook coverage and incremental filters vary by object, so migration reconciliation cannot depend on one universal change feed.

## Instructions

1. Inventory legacy tenants/entities, users, roles, cards, limits, policies, vendors, open expenses, bills, reimbursements, receipts, accounting mappings, integrations, and retention duties.

2. Create a signed semantic mapping for each object and state, including unsupported values, money/currency conversion, ownership, destination ID, and disposition.

3. Build sandbox fixtures for normal, boundary, duplicate, missing-owner, invalid-currency, closed-period, and rollback cases; validate against current Ramp schemas.

4. Migrate one entity or department cohort, run parallel read/reconciliation, and hold card or accounting writes until users, controls, balances, and mappings are approved.

5. Cut over with frozen checkpoints and named authority, reconcile open and late-arriving items through financial close, then revoke legacy access under retention policy.

## Tool Discipline

- Use **Glob** to locate candidate code, manifests, fixtures, and evidence without widening scope.
- Use **Grep** to find relevant endpoints, fields, permissions, identifiers, errors, and stale assumptions.
- Use **Read** to inspect the smallest required local files and authoritative evidence.
- Use **Write** only for a new approved local draft, test, configuration, or evidence artifact.
- Use **Edit** only for a bounded approved change with a known rollback.
- Local file tools do not authorize a Ramp operation or replace owner approval.

## Approval Boundaries

Business and finance owners approve semantic mappings and cutover; security/privacy approve identity and data movement; accounting approves balances, mappings, and final close.

## Output

A source inventory, semantic map, cohort plan, exception ledger, ID crosswalk, sandbox proof, parallel-run reconciliation, cutover/rollback record, and retirement evidence.

## Error Handling

| Condition | Response |
|---|---|
| A legacy state has no Ramp equivalent | Quarantine it with an owner and explicit transform, manual handling, or no-migrate decision. |
| A user or entity mapping is ambiguous | Stop the cohort; do not assign spend authority by name similarity. |
| Late transactions arrive after cutover | Apply the frozen coexistence rule, migrate or settle once, and reconcile both systems through close. |

## Examples

### Example 1

Migrate one subsidiary's users and recurring software cards into approved Funds while keeping the legacy issuer read-only for late settlement.

### Example 2

Move open reimbursements and vendor mappings, reconcile ERP references, and retire the old export only after period close.

## Validation

- Every source record has one destination, exception, or approved retirement disposition.
- Identity, entity, currency, amount, and accounting mappings reconcile independently.
- No spend authority or production write is enabled before approval.
- Rollback and coexistence cover late, duplicated, and in-flight records.

## Resources

- [Official documentation and contract notes](references/official-docs.md)
- Re-check the dated contract and current OpenAPI schema before any live request.
- Treat unresolved vendor behavior, authority, or financial state as a stop condition.
