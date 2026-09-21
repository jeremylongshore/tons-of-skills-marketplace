---
name: vastai-migration-deep-dive
description: >-
  Migrate a GPU workload from another provider to Vast.ai through inventory, container and data parity, a checkpointed canary, measured comparison, and rollback. Use when planning or executing a provider cutover. Trigger with: "migrate Runpod to Vast.ai", "move GPU jobs to Vast.ai", "validate a Vast.ai migration".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[source-provider-workload-and-cutover-objective]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - vastai
  - migration
  - cutover
  - rollback
compatibility: 'Requires source-provider inventory, portable workload artifacts, Vast.ai capacity, external storage, and an approved rollback window.'
---

# Evidence-Gated Migration to Vast.ai

## Overview

Separate portability from cutover. First identify source-provider dependencies, then prove immutable image, storage, networking, secrets, GPU, and output behavior on a disposable Vast.ai canary before moving production work.

## Prerequisites

- Source inventory covering images, accelerators, storage, network, identity, schedules, and cost
- Acceptance thresholds for correctness, throughput, latency, recovery, and total spend
- Versioned data/checkpoint transfer, dual-run or drain plan, and rollback owner

## Instructions

### Step 1: Freeze source truth

Record source release, image digest, GPU profile, command, secrets interfaces, ports, persistent data, checkpoints, SLOs, and representative outputs.

### Step 2: Map Vast.ai equivalents

Choose offer or Serverless profiles, template, disk/volume/cloud-copy route, scoped keys, SSH/network mode, and lifecycle semantics.

### Step 3: Prove artifact parity

Run the same image and input sample on one disposable Vast.ai target; verify CUDA, dependencies, output schema, checksums, and external checkpoint recovery.

### Step 4: Compare production characteristics

Measure startup, throughput, latency, reliability, bandwidth, storage, interruption recovery, and cost per accepted unit.

### Step 5: Cut over reversibly

Quiesce or dual-run according to data semantics, move only verified state, switch a bounded slice, and monitor explicit acceptance gates.

### Step 6: Accept or roll back

Promote only if every gate passes. Otherwise restore source routing, reconcile writes and checkpoints, and destroy rejected Vast.ai resources.

## Authentication

Translate identity to scoped Vast.ai keys and separate storage/registry credentials. Do not export source-provider credentials into images or long-lived Vast.ai environment variables.

## Tool Discipline

Use Read and Grep to inspect manifests, configuration, provider output, and existing tests before proposing a mutation. Use Write or Edit only for the approved plan, implementation, test, or redacted receipt; do not create, update, destroy, or fund Vast.ai resources without explicit operator approval.

## Output

- Source-to-Vast dependency and control map
- Canary parity, recovery, performance, and cost evidence
- Cutover or rollback timeline with reconciled data and resource cleanup

Return source/target releases, immutable identities, data checkpoint, acceptance deltas, decision, rollback point, and destroyed resources.

## Examples

A Runpod training job keeps its container contract, moves checkpoints to a versioned cloud prefix, proves resume on one Vast.ai canary, then shifts scheduled jobs while the source environment remains available for one rollback window.

## Error Handling

| Failure | Response |
| --- | --- |
| Source dependency has no target equivalent | Design and test an adapter before cutover. |
| Data or output checksums differ | Stop migration and reconcile the semantic difference. |
| Target capacity violates policy | Delay or approve a documented alternate; do not weaken constraints silently. |
| Rollback window closes early | Issue NO-GO until source restoration remains provable. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Runpod to Vast migration](https://docs.vast.ai/examples/migrations/runpod-to-vast)
- [Salad to Vast migration](https://docs.vast.ai/examples/migrations/salad-to-vast)
- [Vast.ai concepts](https://docs.vast.ai/guides/concepts)
