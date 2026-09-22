---
name: vastai-reference-architecture
description: >-
  Design a governed Vast.ai GPU control plane that separates planning, paid mutation, execution, recovery, evidence, and teardown. Use when reviewing a production architecture spanning instances or Serverless. Trigger with: "design a Vast.ai architecture", "govern GPU workload lifecycles", "review a Vast.ai platform".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[workload-types-slos-data-class-and-budget]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - vastai
  - architecture
  - governance
  - reliability
compatibility: 'Requires workload and data classification, Vast.ai account design, immutable artifacts, external storage, observability, and incident ownership.'
---

# Governed Vast.ai GPU Workload Architecture

## Overview

Center the architecture on an immutable run or release manifest and a lifecycle ledger. Search and planning are read-only; paid resource creation crosses an approval boundary; execution writes recoverable state externally; teardown closes both cost and evidence.

## Prerequisites

- Batch, training, interactive, or Serverless workload inventory with SLOs
- Data, model, image, credential, region, reliability, and spend policies
- Owners for approval, execution, recovery, billing, security, and platform incidents

## Instructions

### Step 1: Define the immutable intent

Create a signed or versioned manifest containing workload bytes, image/template/model identity, GPU policy, data/checkpoint routes, SLOs, budget, and expiry.

### Step 2: Separate planner and mutator

Let a read-scoped planner evaluate offers or Serverless profiles. Require explicit approval before a narrowly scoped mutator creates, updates, transfers credit, or destroys.

### Step 3: Choose the executor

Use an instance lifecycle for bounded jobs or dedicated services; use Serverless endpoint/workergroup control for managed inference scaling and rolling updates.

### Step 4: Externalize durable state

Keep datasets, checkpoints, artifacts, event ledgers, and evidence outside disposable root disks with checksums and recovery objectives.

### Step 5: Observe and reconcile

Combine provider states, signed notifications, bounded polling, workload SLOs, balance, charges, and resource inventory; reconcile events against periodic reads.

### Step 6: Close every lifecycle

Accept output, copy evidence, destroy disposable resources, revoke temporary access, reconcile charges, and leave an auditable handoff for retained resources.

## Authentication

Use native Teams roles and distinct scoped keys for planning, mutation, monitoring, and administration. Workload storage and registry credentials must never inherit control-plane authority.

## Tool Discipline

Use Read and Grep to inspect manifests, configuration, provider output, and existing tests before proposing a mutation. Use Write or Edit only for the approved plan, implementation, test, or redacted receipt; do not create, update, destroy, or fund Vast.ai resources without explicit operator approval.

## Output

- Trust-boundary and component decision record
- Immutable manifest, lifecycle ledger, recovery, and observability contracts
- Threat, failure, cost, rollback, and teardown evidence plan

Return workload classes, chosen executors, authority boundaries, immutable artifacts, recovery targets, SLOs, budgets, event reconciliation, and lifecycle owners.

## Examples

A planner selects verified offers but cannot rent; an approved mutator creates from a signed run manifest; the training executor checkpoints externally; a signed event plus reconciliation loop detects failure; a finalizer destroys the instance and closes the charge ledger.

## Error Handling

| Failure | Response |
| --- | --- |
| One service can plan, fund, mutate, and erase evidence | Split authority and add independent approval and audit. |
| Durable state exists only on an instance | Move it to an external verified store before production. |
| Event stream is treated as complete | Add periodic resource reconciliation and idempotent processing. |
| Resource has no expiry or cleanup owner | Reject the architecture until the lifecycle can close. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Vast.ai concepts](https://docs.vast.ai/guides/concepts)
- [Serverless architecture](https://docs.vast.ai/guides/serverless/architecture)
- [API permissions](https://docs.vast.ai/api-reference/permissions)
