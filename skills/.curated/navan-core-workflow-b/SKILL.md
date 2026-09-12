---
name: navan-core-workflow-b
description: >-
  Implement reconciliation of contracted Navan expense data with an ERP or finance control plane. Use when operating the Expense API or a direct accounting integration. Trigger with "sync Navan expenses", "reconcile Navan spend", or "export Navan transactions".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<tenant> <ledger> <accounting-period>"
version: 1.9.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, navan, expenses]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live or external Navan actions require network access and explicit approval"
---
# Navan Expense Data Reconciliation

## Overview

Implement reconciliation of contracted Navan expense data with an ERP or finance control plane. This workflow produces an auditable decision or artifact before any live action.

## Prerequisites

- Access to the selected tenant's current Navan Help Center and contracted integration documentation.
- A named business owner and data owner for the travel or expense workflow.
- A non-production evidence set with secrets and traveler data removed.

## Current Contract

Navan publicly confirms an Expense API for custom ERP systems and direct accounting integrations. Transaction, receipt, reimbursement, approval, and settlement schemas are tenant-specific and must not be guessed from marketing pages.

## Authentication

Separate read-only reconciliation access from any approval, reimbursement, card, or accounting write capability. Limit downstream access to finance roles with an explicit business purpose.

## Instructions

1. Define the accounting period, entities, currencies, and source record classes.
2. Capture documented identifiers, amount semantics, lifecycle timestamps, and correction behavior.
3. Land source records and evidence hashes without exposing receipt contents in logs.
4. Map accounts, cost centers, tax, projects, and currencies through versioned rules.
5. Reconcile totals and record-level lineage before posting or export.
6. Route exceptions to a human queue and publish only after finance approval.

## Tool Discipline

Use Read, Glob, and Grep to inspect documentation, schemas, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Invocation alone does not authorize network access, credentials, traveler or expense data, bookings, payments, policy or identity changes, file transfers, deployments, or deletion.

## Approval Boundaries

Any posting, approval, reimbursement, card action, policy change, or release of receipt data requires explicit authorized-human approval.

## Error Handling

- Do not convert currency without a named rate source and effective time.
- Never infer approval from the presence of a transaction.
- Stop when entity, period, or total controls do not reconcile.

## Output

Return the period, entity matrix, source and ledger totals, exception classes, lineage receipt, and approval state. Identify assumptions, owners, expirations, and evidence gaps explicitly.

## Examples

- Reconcile approved expense data to a staging ledger.
- Quarantine a transaction whose currency or entity mapping is missing.

## Validation

Test duplicates, reversals, partial reimbursements, late receipts, multi-currency records, closed periods, and denied posting approval. Record expected and observed results, including fail-closed behavior.

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources and the selected tenant's in-account contract before relying on mutable endpoints, fields, entitlements, limits, or delivery behavior.
- Record tenant observations as environment-specific evidence, never universal Navan guarantees.
