---
name: ramp-core-workflow-b
description: >-
  Implement a reconciled two-way Ramp accounting integration for chart-of-accounts data and sync-ready spend objects. Use when exporting transactions, bills, reimbursements, transfers, or cashbacks to an ERP. Trigger with "Ramp accounting sync" or "Ramp ERP integration".
allowed-tools: Read,Glob,Grep,Write,Edit
version: 2.0.0
argument-hint: "[integration-or-environment]"
model: inherit
effort: high
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Requires current Ramp Developer API documentation and approved access for any live financial, card, identity, accounting, application, or configuration change
tags: [saas, ramp, accounting, erp, reconciliation]
---
# Ramp-to-ERP Accounting Sync

## Overview

Mirror ERP coding structures into Ramp, pull only eligible objects, post them once to the ERP, and send explicit success or failure receipts back to Ramp. Preserve entity boundaries and an auditable idempotency ledger.

## Prerequisites

- Identify the Ramp application, environment, business entities, affected data and workflows, accountable owner, and rollback boundary.
- Read `references/official-docs.md` and re-check endpoint schemas, scopes, limits, and support status before a live operation.
- Use synthetic fixtures or Ramp sandbox until production access and business effects are explicitly approved.
- Prepare approved secret storage and a sanitized evidence location.

## Current Contract

- An API accounting connection is distinct from Ramp's direct ERP integrations; direct connections are blocked from API sync marking by default.
- Sync-ready filters differ by object type. Transactions and several objects use `sync_status=SYNC_READY`; bills use `sync_ready=true`.
- `POST /developer/v1/accounting/syncs` accepts an idempotency key, sync type, and explicit successful or failed object receipts.
- Multi-entity reads must be scoped with `entity_id`, and Ramp IDs used for accounting selections differ from ERP remote IDs.

## Instructions

1. Inventory entities, object types, chart fields, remote IDs, tax/vendor relationships, direct integrations, owners, and the reconciliation period.

2. Push or update chart-of-accounts structures in bounded validated batches; retain Ramp IDs and ERP remote IDs in a typed mapping table.

3. Fetch each eligible object type with its documented ready-to-sync filter and paginate completely within one entity at a time.

4. Post to the ERP using a stable source-object key, then record the ERP reference and only afterward submit the Ramp success receipt; submit structured failure receipts for rejected objects.

5. Reconcile counts, amounts, currencies, line splits, entities, and status in both systems; quarantine mismatches and repeat reconciliation after any retry.

## Tool Discipline

- Use **Glob** to locate candidate code, manifests, fixtures, and evidence without widening scope.
- Use **Grep** to find relevant endpoints, fields, permissions, identifiers, errors, and stale assumptions.
- Use **Read** to inspect the smallest required local files and authoritative evidence.
- Use **Write** only for a new approved local draft, test, configuration, or evidence artifact.
- Use **Edit** only for a bounded approved change with a known rollback.
- Local file tools do not authorize a Ramp operation or replace owner approval.

## Approval Boundaries

Accounting owns mappings and period policy; each entity owner approves scope; finance approves production posting and replay. Do not mark an object synced without a durable ERP receipt.

## Output

An entity-aware mapping inventory, cursor/checkpoint ledger, ERP post receipts, Ramp sync receipts, mismatch queue, reconciliation totals, and rollback/reversal procedure.

## Error Handling

| Condition | Response |
|---|---|
| An object is already posted in the ERP | Resolve by the stable Ramp source ID and reuse the existing ERP reference; do not create a second journal entry. |
| A chart batch partly appears to succeed | Treat the documented batch as all-or-nothing, read current state, and resend only after reconciliation. |
| A direct integration rejects sync marking | Stop and resolve the accounting-connection architecture with Ramp and the finance owner. |

## Examples

### Example 1

Export one entity's sync-ready card transactions to an ERP and prove every successful Ramp receipt maps to one journal reference.

### Example 2

Migrate bills and reimbursements while quarantining currency or coding mismatches instead of marking them synced.

## Validation

- Each exported object has one stable Ramp ID, entity, ERP reference, and receipt state.
- Amounts use endpoint-defined minor units and currencies without floating-point conversion.
- Every page and object type is reconciled; no cursor is advanced past an uncommitted unit.
- Failure receipts and replay decisions are visible to accounting operators.

## Resources

- [Official documentation and contract notes](references/official-docs.md)
- Re-check the dated contract and current OpenAPI schema before any live request.
- Treat unresolved vendor behavior, authority, or financial state as a stop condition.
