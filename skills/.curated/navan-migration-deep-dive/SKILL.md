---
name: navan-migration-deep-dive
description: >-
  Migrate travel or expense data flows to Navan with staged cutover and financial and traveler reconciliation. Use when replacing a TMC, expense platform, card feed, or custom integration. Trigger with "migrate to Navan", "Navan cutover", or "replace travel platform".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<legacy-system> <navan-surfaces> <cutover-window>"
version: 1.9.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, navan, migration]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live or external Navan actions require network access and explicit approval"
---
# Navan Platform Migration Reconciliation

## Overview

Migrate travel or expense data flows to Navan with staged cutover and financial and traveler reconciliation. This workflow produces an auditable decision or artifact before any live action.

## Prerequisites

- Access to the selected tenant's current Navan Help Center and contracted integration documentation.
- A named business owner and data owner for the travel or expense workflow.
- A non-production evidence set with secrets and traveler data removed.

## Current Contract

Migration must reconcile legacy and Navan concepts rather than forcing field-for-field equivalence. Booking lifecycle, traveler profile, policy, card, expense, receipt, currency, approval, and accounting meanings require explicit mapping.

## Authentication

Use separate migration identities and time-bound access. Avoid copying legacy secrets, personal data, or administrator privileges into steady-state integration accounts.

## Instructions

1. Inventory legacy workflows, data, owners, obligations, integrations, and open items.
2. Capture Navan tenant contracts and map concepts with loss and ambiguity labels.
3. Define historical migration, open-item transition, and future-state interfaces separately.
4. Rehearse with synthetic and approved bounded data.
5. Dual-run or shadow-process a controlled period and reconcile travelers, bookings, expenses, cards, and totals.
6. Cut over with freeze, communication, rollback, legacy retention, and decommission gates.

## Tool Discipline

Use Read, Glob, and Grep to inspect documentation, schemas, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Invocation alone does not authorize network access, credentials, traveler or expense data, bookings, payments, policy or identity changes, file transfers, deployments, or deletion.

## Approval Boundaries

Historical data movement, traveler communication, policy conversion, card or payment change, production cutover, and legacy deletion require authorized owners.

## Error Handling

- Do not manufacture missing legacy meaning.
- Keep unresolved open items visible through cutover.
- No legacy deletion before legal, finance, privacy, and rollback gates close.

## Output

Return the concept map, data disposition, dual-run evidence, open-item register, cutover plan, rollback, and decommission record. Identify assumptions, owners, expirations, and evidence gaps explicitly.

## Examples

- Move booking reporting while preserving legacy trip lineage.
- Transition expense reconciliation without duplicating reimbursements.

## Validation

Reconcile representative historical, open, cancelled, corrected, refunded, personal, and multi-currency cases. Record expected and observed results, including fail-closed behavior.

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources and the selected tenant's in-account contract before relying on mutable endpoints, fields, entitlements, limits, or delivery behavior.
- Record tenant observations as environment-specific evidence, never universal Navan guarantees.
