---
name: vastai-cost-tuning
description: >-
  Reduce Vast.ai GPU, storage, and bandwidth spend without weakening workload requirements or leaving stopped resources billable. Use when selecting offers, setting spot policy, cleaning idle resources, or reconciling invoices. Trigger with: "optimize Vast.ai cost", "find Vast.ai cost leaks", "compare Vast.ai offers".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[workload-profile-budget-and-time-window]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - vastai
  - cost
  - billing
  - offers
compatibility: 'Requires workload performance requirements, Vast.ai offer and instance data, billing-read access, and a cleanup owner.'
---

# Vast.ai GPU Cost and Leakage Control

## Overview

Optimize total useful-work cost, not headline GPU price. Account for performance, reliability, storage, bandwidth, loading behavior, stopped-instance charges, interruptible semantics, and recovery overhead.

## Prerequisites

- GPU/VRAM, throughput, reliability, geography, disk, and completion-time requirements
- Hourly and total budget plus checkpoint/restart cost assumptions
- Instance, volume, charge, and invoice inventory for the analysis window

## Instructions

### Step 1: Build a normalized offer set

Search verified rentable offers and retain GPU price, storage, bandwidth, reliability, `dlperf`, `dlperf_usd`, network, and host constraints.

### Step 2: Model useful-work cost

Estimate runtime from measured throughput, then add storage, data transfer, startup, checkpoint, failure, and operator recovery costs.

### Step 3: Choose rental semantics

Use on-demand when completion certainty dominates. Use bid pricing only for checkpointed work and pass an explicit bid; a bid search alone does not create an interruptible rental.

### Step 4: Find leakage

Identify stopped instances still paying storage, idle active GPUs, abandoned volumes, oversized disks, duplicate canaries, and failed jobs without teardown.

### Step 5: Apply bounded changes

Destroy confirmed abandoned resources, resize only through a tested replacement path, and preserve external artifacts before irreversible actions.

### Step 6: Reconcile savings

Compare charges and invoices before and after using completed-work units, not just hourly rate, and record any service or reliability regression.

## Authentication

Use billing-read for analysis and separate instance-write authority for approved cleanup. Never grant billing-write or credit-transfer permission to an optimizer.

## Tool Discipline

Use Read and Grep to inspect manifests, configuration, provider output, and existing tests before proposing a mutation. Use Write or Edit only for the approved plan, implementation, test, or redacted receipt; do not create, update, destroy, or fund Vast.ai resources without explicit operator approval.

## Output

- Normalized offer and useful-work cost model
- Leak inventory with owner and safe disposition
- Verified savings, performance delta, and cleanup receipt

Return window, workload unit, selected offer policy, resource IDs, modeled/actual cost, savings, and unresolved billing risk.

## Examples

A checkpointed batch job selects a high `dlperf_usd` bid offer with an explicit bid, while an idle stopped instance and orphaned volume are destroyed after artifact verification; savings are measured per completed batch.

## Error Handling

| Failure | Response |
| --- | --- |
| Required pricing field is absent | Mark the offer incomparable rather than assuming zero cost. |
| Spot work lacks external checkpoints | Use on-demand or add recovery before selecting bid pricing. |
| Stopped instance is called free | Correct the model because storage charges continue until destruction. |
| Cleanup ownership is unclear | Do not destroy; assign an owner and preserve the leak in the report. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Vast.ai pricing](https://docs.vast.ai/guides/pricing)
- [Billing](https://docs.vast.ai/guides/reference/billing)
- [Official CLI interruptible guidance](https://github.com/vast-ai/vast-cli/blob/master/vastai/SKILL.md#interruptible-spot-rentals)
