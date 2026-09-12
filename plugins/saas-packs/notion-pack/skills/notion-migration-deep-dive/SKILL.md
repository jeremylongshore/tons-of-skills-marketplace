---
name: notion-migration-deep-dive
description: >-
  Design and execute a reversible Notion content or schema migration with identity maps, checkpoints, and reconciliation. Use when moving data between schemas, workspaces, versions, or external systems. Trigger with "migrate Notion data", "upgrade Notion schema", or "backfill Notion pages".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<source> <destination> <migration-window>"
version: 1.40.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, notion, migration]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Notion actions require network access and explicit approval"
---
# Notion Migration Reconciliation

## Overview

Design and execute a reversible Notion content or schema migration with identity maps, checkpoints, and reconciliation.. This workflow produces an auditable decision or artifact before any live action.

## Prerequisites

- Current first-party Notion documentation and the selected integration's tested API-version contract.
- A named workspace owner, content or data owner, and operation owner.
- Synthetic or approved non-production fixtures with secrets and workspace content removed.

## Current Contract

Migration contracts must distinguish database containers, data sources, pages, properties, blocks, files, users, relations, and trash state. Search and export order are not durable migration checkpoints. Recheck the dated evidence map before relying on mutable fields, endpoints, versions, limits, or delivery behavior.

## Authentication

Use separate least-privilege source-read and destination-write identities where possible. Keep identity maps and sensitive content encrypted and tenant-scoped.

## Instructions

1. Freeze the source and destination contracts, selected versions, owners, and acceptance metrics.
2. Inventory schemas, stable IDs, relations, unsupported blocks, files, user mappings, and sensitive fields.
3. Create deterministic identity, property, relation, content, and lifecycle mappings with quarantine rules.
4. Run a synthetic dry run and then a small approved canary with resumable checkpoints.
5. Migrate in bounded batches; persist destination IDs before advancing source checkpoints.
6. Reconcile counts, hashes, relations, block order, files, quarantines, late changes, and rollback eligibility.

## Tool Discipline

Use Read, Glob, and Grep to inspect documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Invocation alone does not authorize network access, credentials, workspace content, user data, file transfer, deployment, capability or sharing changes, writes, spend, or deletion.

## Approval Boundaries

Require source and destination owners before reads or writes; require separate approval for historical export, user data, backfill, trash, or cutover.

## Error Handling

- Do not use titles as unique identities.
- Do not advance a checkpoint after partial destination acknowledgement.
- Freeze cutover on unexplained count or relation drift.

## Output

Return the contracts, mappings, checkpoints, batch ledger, reconciliation, quarantine, cutover decision, and rollback package. Identify assumptions, owners, expirations, and evidence gaps explicitly.

## Examples

- Migrate one legacy database schema to current data-source operations.
- Resume a cross-workspace page migration without duplicating accepted pages.

## Validation

Exercise and record these paths with expected and observed results:

- empty values
- relation cycles
- unsupported block
- expired file
- partial batch
- late source change

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources before relying on mutable behavior.
- Treat observed tenant behavior as environment-specific evidence, never a universal Notion guarantee.
