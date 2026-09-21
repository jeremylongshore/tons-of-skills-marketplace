---
name: quicknode-upgrade-migration
description: 'Migrate a QuickNode SDK, endpoint, chain API, token, or event product with inventory, compatibility tests, canary traffic, and rollback. Use when adopting the unified SDK, responding to a chain deprecation, or rotating infrastructure without losing writes or events. Trigger with: "upgrade QuickNode", "migrate a QuickNode endpoint", "plan a QuickNode cutover".'
allowed-tools: Read, Grep, Write, Edit, Bash(npm:*), Bash(qn:*)
version: 2.0.0
argument-hint: '[current-and-target-contract]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - quicknode
  - migration
  - upgrade
  - rollback
compatibility: 'SDK native targets and chain API deprecations must be checked against current QuickNode documentation'
---

# QuickNode Upgrade and Migration

## Overview

Treat client, endpoint, token, chain API, and event-pipeline changes as contract migrations. Preserve a parallel read path or replay boundary until the target proves identity, correctness, capacity, and recovery.

## Prerequisites

- Current and target SDK, endpoint, chain/network, and product inventory
- Compatibility tests and representative traffic
- Cutover owner, rollback window, and data-reconciliation plan

## Authentication

Keep target credentials separate from the current path during the dual run. Endpoint tokens authenticate RPC through a protected URL or `x-token` header; Admin API inspection uses a distinct `x-api-key`, while `qn` uses its authenticated account session. Redact all three from matrices and receipts.

## Instructions

### Step 1: Build the change matrix

Use Read and Grep to find SDK imports, endpoint URLs, API methods, protocols, chain IDs, archive assumptions, tokens, Stream/Webhook IDs, cursors, and platform targets.

### Step 2: Read current contracts

Verify the target SDK platform matrix, product API, chain deprecation, supported protocol, pruning policy, and method response. Do not derive compatibility from an unrelated chain quickstart.

### Step 3: Prepare the target

Use Bash(npm:*) for a reviewed pinned SDK update and lockfile change. Use Write or Edit to adapt behind a stable interface, add dual-read comparisons, and preserve old configuration for rollback.

### Step 4: Inspect provider resources

Use Bash(qn:*) for read-only current/target endpoint, security, usage, metrics, Stream, and Webhook state. Create or mutate resources only after an explicit operator checkpoint.

### Step 5: Canary and reconcile

Compare chain identity, response semantics, latency, errors, credits, transaction status, and event completeness. For event migrations, start from an overlap block and deduplicate by durable event identity.

### Step 6: Cut over and retire

Shift traffic gradually, retain the old endpoint/token through the rollback window, then revoke or archive only after evidence and owner approval. Record deprecation and consumer communication.

## Tool Discipline

Use Read/Grep for inventory, Write/Edit for adapters and tests, Bash(npm:*) for pinned package operations, and Bash(qn:*) for read-only resource evidence. Destructive retirement remains approval-gated.

## Output

- Current-to-target compatibility matrix
- Tested adapter and dual-run evidence
- Cutover and replay plan
- Rollback receipt and retirement approval

## Examples

A service moves from a legacy `Core` wrapper to the unified SDK for control-plane calls while retaining its chain provider adapter. Dual reads prove equivalence before the old dependency is removed.

## Error Handling

| Failure | Response |
| --- | --- |
| Target runtime cannot load SDK | Stop and revisit the native platform matrix |
| Dual reads differ | Classify semantic, freshness, or chain differences before cutover |
| Events are missing | Resume from the overlap cursor and deduplicate |
| Rollback credential was revoked | Stop rollout and restore a tested recovery identity |

## Resources

- [Migration evidence and source notes](references/official-docs.md)
- [Unified SDK](https://www.quicknode.com/docs/sdk)
- [Supported chains and pruning](https://www.quicknode.com/docs/platform/supported-chains-node-types)
