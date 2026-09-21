---
name: procore-migration-deep-dive
description: >-
  Plan and execute a resumable Procore data migration with dependency ordering, stable origin identifiers, sync actions where supported, file transfer, checkpoints, reconciliation, and rollback. Use when importing or exporting construction records at scale. Trigger with: "migrate data to Procore", "build a Procore backfill", "reconcile a Procore migration".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[source-target-and-resource-domains]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - procore
  - data-migration
  - reconciliation
compatibility: 'Requires approved source and target access, a documented resource dependency graph, durable checkpoint storage, and a tested rollback plan.'
---

# Procore Resumable Data Migration

## Overview

Move records as an ordered, observable, and reversible program rather than a bulk request loop. Use documented resource contracts, stable external identity, supported sync actions, and separate file workflows while preserving tenant and project boundaries.

## Prerequisites

- Source and target owners, data classification, retention, and legal approval
- Resource inventory, volume, dependency graph, field mapping, and unsupported-feature list
- DMSA or user permission map, rate budget, checkpoint store, and rollback boundary

## Instructions

### Step 1: Profile and map

Count records and files by company, project, resource, status, and dependency. Map required fields, codes, users, locations, permissions, timestamps, and external identifiers.

### Step 2: Design stable identity

Use documented `origin_id` or equivalent only where the resource supports it. Define source-to-Procore mapping, collision handling, and a replay-safe uniqueness rule.

### Step 3: Order dependencies

Create prerequisite company and project data before dependent records. Follow documented API call sequencing and isolate unsupported resources for explicit disposition.

### Step 4: Execute resumably

Process bounded batches, follow rate headers, checkpoint after verified commits, and use sync actions only for supported resources. Transfer files through their separate documented upload and association flow.

### Step 5: Reconcile continuously

Compare counts, key fields, relationships, file checksums, failures, duplicates, and state hashes per batch. Quarantine poison records without blocking the entire migration.

### Step 6: Cut over and settle

Run final delta capture, freeze writes if required, verify parity, switch consumers, observe, and preserve rollback until the agreed settlement window closes.

## Authentication

Migration calls use an OAuth 2.0 Bearer token for the approved user or DMSA and explicit company and project scope. The migration must not obtain broad permissions merely to simplify dependency handling.

## Tool Discipline

Use Read and Grep to inspect mappings, contracts, checkpoints, and reconciliation evidence. Use Write or Edit only for the approved migration adapter, manifest, quarantine record, test, or receipt; never place source data in source control.

## Output

- Resource map, dependency order, and unsupported-feature disposition
- Batch checkpoints, identity mappings, and failure quarantine
- Parity, cutover, rollback, and settlement receipt

Return migrated and failed counts, checkpoint, divergence summary, file verification, permission boundary, and next safe action.

## Examples

A backfill creates prerequisite project metadata before RFIs, assigns stable external identity only on resources that support it, uploads attachments through the documented file flow, and advances each checkpoint only after count and relationship reconciliation.

## Error Handling

| Failure | Response |
| --- | --- |
| Origin identifier collides | Quarantine the record and resolve mapping ownership; do not overwrite blindly. |
| Resource lacks sync support | Use its documented endpoint with a specific idempotency plan or exclude it. |
| Batch parity fails | Stop checkpoint advancement and reconcile the smallest divergent set. |
| Rate budget falls | Pause according to response headers and resume from the last verified checkpoint. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Using Sync Actions](https://developers.procore.com/documentation/using-sync-actions)
- [API call sequencing](https://developers.procore.com/documentation/api-call-sequencing)
- [Direct file uploads](https://developers.procore.com/documentation/tutorial-uploads)
