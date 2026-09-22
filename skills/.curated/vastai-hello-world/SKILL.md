---
name: vastai-hello-world
description: >-
  Rent, verify, use, and destroy a first Vast.ai GPU instance with bounded cost and explicit failure cleanup. Use when running a safe platform canary or onboarding exercise. Trigger with: "rent my first Vast.ai GPU", "run a Vast.ai canary", "test Vast.ai end to end".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[gpu-requirement-budget-and-image]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - vastai
  - instances
  - onboarding
  - cost-control
compatibility: 'Requires the Vast.ai CLI, a valid API key, account credit, an SSH public key, and an approved container image.'
---

# First Vast.ai GPU Rental With a Cost Fence

## Overview

Prove the complete renter lifecycle without leaving billable storage behind. Search a verified offer, register SSH before creation, capture the returned contract ID, bound readiness polling, run one GPU check, retrieve evidence, and destroy.

## Prerequisites

- Maximum hourly price, maximum elapsed time, GPU/VRAM need, disk size, and region policy
- Approved image tag and registered SSH public key
- Cleanup owner who can destroy the contract even when the workload fails

## Instructions

### Step 1: Verify identity and budget

Run `vastai show user --raw`; confirm the intended account and enough credit. Set an external deadline and total-spend ceiling before searching.

### Step 2: Search a suitable offer

Use `vastai search offers --raw` with `verified=true`, `rentable=true`, reliability, direct-port, GPU, disk, and price constraints. Record the selected offer ID and quoted price components.

### Step 3: Create exactly one instance

Create with an immutable image tag, SSH, direct networking when required, and the smallest sufficient disk. Capture `new_contract` as the instance ID.

### Step 4: Wait with terminal branches

Poll `vastai show instance ID --raw` until `actual_status` is `running`. Abort and clean up on timeout, `exited`, `unknown`, or `offline`; never poll forever.

### Step 5: Run and collect the canary

Resolve the SSH URL, execute `nvidia-smi`, run the bounded workload, and copy out the small result or checksum.

### Step 6: Destroy and prove cleanup

Destroy the instance non-interactively and confirm it no longer appears. Destruction is irreversible but is required to stop storage charges.

## Authentication

Use a scoped key that can search offers and manage instances but cannot transfer credit or administer teams. Keep SSH private keys local and never pass them through instance environment variables.

## Tool Discipline

Use Read and Grep to inspect manifests, configuration, provider output, and existing tests before proposing a mutation. Use Write or Edit only for the approved plan, implementation, test, or redacted receipt; do not create, update, destroy, or fund Vast.ai resources without explicit operator approval.

## Output

- Selected offer and cost-policy decision
- Instance state timeline and GPU canary result
- Artifact checksum plus confirmed destruction receipt

Return account ID, offer ID, instance ID, price, state transitions, canary result, and cleanup confirmation with secrets removed.

## Examples

An operator rents one verified RTX 4090 below the approved hourly ceiling, reaches `running` within the deadline, records a CUDA device check, copies out a checksum, and destroys the contract in a guaranteed cleanup path.

## Error Handling

| Failure | Response |
| --- | --- |
| No offer satisfies policy | Do not relax controls silently; report which constraint eliminated capacity. |
| Instance remains loading | Respect the deadline, inspect image size and host network, then destroy and choose another offer. |
| Instance becomes exited, unknown, or offline | Stop polling, salvage only if safe, destroy, and retry on a different host. |
| Cleanup command fails | Escalate immediately with the instance ID because storage may still be billing. |

## Resources

- [First-party source notes](references/official-docs.md)
- [CLI hello world](https://docs.vast.ai/cli/hello-world)
- [Manage instances](https://docs.vast.ai/guides/instances/manage-instances)
- [Official CLI skill](https://github.com/vast-ai/vast-cli/blob/master/vastai/SKILL.md)
