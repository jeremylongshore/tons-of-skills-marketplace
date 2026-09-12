---
name: navan-data-sync
description: >-
  Synchronize Navan booking, expense, identity, and file-delivered data according to each documented source contract. Use when building durable ETL or correcting sync drift. Trigger with "Navan data sync", "Navan ETL", or "reconcile Navan feeds".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<surfaces> <destination> <freshness-objective>"
version: 1.9.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, navan, sync]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live or external Navan actions require network access and explicit approval"
---
# Navan Multi-Surface Data Synchronization

## Overview

Synchronize Navan booking, expense, identity, and file-delivered data according to each documented source contract. This workflow produces an auditable decision or artifact before any live action.

## Prerequisites

- Access to the selected tenant's current Navan Help Center and contracted integration documentation.
- A named business owner and data owner for the travel or expense workflow.
- A non-production evidence set with secrets and traveler data removed.

## Current Contract

Do not assume bookings are weekly full refreshes, transactions are append-only, or generic webhooks exist. Record snapshot, incremental, correction, deletion, ordering, and delivery semantics independently for every enabled API, file, or managed integration.

## Authentication

Use distinct read identities or transfer credentials per surface and tenant. Keep destination write credentials separate from Navan access and from any privileged write-back identity.

## Instructions

1. Build a surface ledger with contract revision, keys, timestamps, cadence, and correction semantics.
2. Capture a durable source checkpoint without advancing it before destination acknowledgement.
3. Land immutable raw records with hashes and sensitivity controls.
4. Normalize through versioned mappings while preserving source lineage.
5. Apply idempotent destination writes and quarantine unknown or conflicting records.
6. Reconcile source windows, destination acknowledgements, totals, late changes, and deletion obligations.

## Tool Discipline

Use Read, Glob, and Grep to inspect documentation, schemas, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Invocation alone does not authorize network access, credentials, traveler or expense data, bookings, payments, policy or identity changes, file transfers, deployments, or deletion.

## Approval Boundaries

Backfills, new surfaces, historical access, file retransmission, destination changes, checkpoint resets, and write-back require explicit approval.

## Error Handling

- Never compare opaque IDs lexicographically as a time watermark unless documented.
- Do not advance a checkpoint after a partial load.
- Freeze on unexplained source-to-destination drift.

## Output

Return the surface ledger, checkpoints, rows and hashes by stage, reconciliation deltas, quarantine, and recovery plan. Identify assumptions, owners, expirations, and evidence gaps explicitly.

## Examples

- Synchronize booking and expense feeds with independent checkpoints.
- Recover a missed file window without duplicating accepted records.

## Validation

Test snapshot, incremental, duplicate, late correction, deletion, partial page/file, destination failure, restart, and backfill. Record expected and observed results, including fail-closed behavior.

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources and the selected tenant's in-account contract before relying on mutable endpoints, fields, entitlements, limits, or delivery behavior.
- Record tenant observations as environment-specific evidence, never universal Navan guarantees.
