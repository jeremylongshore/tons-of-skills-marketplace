---
name: vastai-core-workflow-a
description: >-
  Analyze and execute a checkpointed Vast.ai training job from offer policy through artifact recovery and destruction. Use when a repeatable single-job GPU run needs budget and interruption controls. Trigger with: "run training on Vast.ai", "checkpoint a Vast.ai job", "recover Vast.ai training artifacts".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[training-command-gpu-policy-and-checkpoint-target]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - vastai
  - training
  - checkpoints
  - instances
compatibility: 'Requires an immutable training image, reachable checkpoint storage, a scoped Vast.ai key, and an approved GPU budget.'
---

# Checkpointed Vast.ai Training Run

## Overview

Treat a training run as a recoverable state machine, not an SSH session. Bind code and image identity, select an offer through policy, persist checkpoints outside the disposable root disk, export final evidence, and destroy.

## Prerequisites

- Immutable image and code revision with deterministic training command
- GPU, VRAM, disk, reliability, geography, and price policy
- Checkpoint destination, resume test, runtime deadline, and cleanup owner

## Instructions

### Step 1: Freeze the run manifest

Record code revision, image digest, dataset version, command, seed, expected checkpoint cadence, budget, and output destination.

### Step 2: Select and create

Search only verified rentable offers that meet the manifest, record price components, and create one labeled instance. Persist `new_contract` immediately.

### Step 3: Reach readiness safely

Poll structured instance state with a deadline and terminal branches. Confirm image identity, disk headroom, GPU model, and CUDA visibility.

### Step 4: Run with external checkpoints

Start the workload so checkpoints are uploaded or copied to durable storage at the declared cadence. A local checkpoint alone is not recovery evidence.

### Step 5: Verify completion or resume

Validate artifact checksums and run metadata. For an interruption, provision a replacement from policy and prove resume from the last durable checkpoint.

### Step 6: Close the cost boundary

Copy final logs and checksums, destroy the instance, confirm removal, and reconcile actual spend against the manifest.

## Authentication

Use a scoped control-plane key for search and instance operations. Give the workload only the storage credential needed for its checkpoint prefix, with no Vast.ai billing or team authority.

## Tool Discipline

Use Read and Grep to inspect manifests, configuration, provider output, and existing tests before proposing a mutation. Use Write or Edit only for the approved plan, implementation, test, or redacted receipt; do not create, update, destroy, or fund Vast.ai resources without explicit operator approval.

## Output

- Frozen run and offer-selection manifest
- State, checkpoint, resume, artifact, and spend evidence
- Confirmed instance destruction and discrepancy report

Return revision, image digest, offer and instance IDs, checkpoint URI/checksum, terminal result, actual spend, and cleanup confirmation.

## Examples

A fine-tuning job checkpoints every ten minutes to a run-specific object prefix; after a simulated interruption, a replacement instance resumes from the last checksum and the original contract is destroyed.

## Error Handling

| Failure | Response |
| --- | --- |
| No compliant offer exists | Pause the run and report the binding constraint; do not silently weaken reliability or price policy. |
| Checkpoint upload fails | Stop training before the recovery window is exceeded and repair storage access. |
| Host goes offline | Use the last external checkpoint on a different host and preserve the affected instance ID for support. |
| Artifact checksum fails | Do not mark the run complete; retain evidence and rerun from the last verified checkpoint. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Instance overview](https://docs.vast.ai/guides/instances/overview)
- [Data movement](https://docs.vast.ai/guides/instances/storage/data-movement)
- [Manage instances](https://docs.vast.ai/guides/instances/manage-instances)
