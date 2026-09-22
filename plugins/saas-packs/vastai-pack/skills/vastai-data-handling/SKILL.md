---
name: vastai-data-handling
description: >-
  Manage datasets, checkpoints, models, and artifacts through Vast.ai instances, volumes, and cloud connections with integrity and teardown controls. Use when data must move to, from, or between Vast.ai resources. Trigger with: "copy data to Vast.ai", "protect Vast.ai checkpoints", "recover data before destroying an instance".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[source-destination-data-class-and-recovery-objective]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - vastai
  - data
  - checkpoints
  - integrity
compatibility: 'Requires approved storage endpoints, Vast.ai copy or cloud-copy access, integrity manifests, and a data-retention policy.'
---

# Recoverable Vast.ai Data Movement

## Overview

Disposable instance storage is a working tier, not the system of record. Choose the supported location syntax, verify checksums, use trusted datacenters for sensitive cloud sync, and externalize recovery artifacts before stop, expiry, or destroy.

## Prerequisites

- Classified source, destination, size, checksum, encryption, and retention requirements
- Approved local, instance, volume, or saved cloud-connection identifiers
- Recovery point objective and owner for copy verification and cleanup

## Instructions

### Step 1: Plan the route

Choose `local:`, `C.instance:path`, `V.volume:path`, or saved cloud connection syntax based on the documented supported directions. Do not assume volumes can copy directly to local.

### Step 2: Prepare least privilege

Scope the Vast.ai control key and cloud credential to the required operation and prefix. Prefer a trusted datacenter for sensitive Cloud Sync.

### Step 3: Transfer into a staging path

Copy to a versioned temporary destination with enough disk and bandwidth budget. Never target `/root` or `/`, which can break SSH permissions and future copies.

### Step 4: Verify before promotion

Compare size, count, cryptographic checksums, and a workload-level sample before renaming or consuming the staged data.

### Step 5: Checkpoint externally

Write checkpoints and final artifacts to a recoverable volume or cloud target at a cadence inside the recovery objective.

### Step 6: Close retention

Verify the external copy, remove temporary credentials, and destroy or retain instance/volume data according to policy; record ongoing storage cost.

## Authentication

Keep storage credentials distinct from `VAST_API_KEY`, prefix-scoped, and short-lived. Never place either credential in copy logs, image layers, or evidence manifests.

## Tool Discipline

Use Read and Grep to inspect manifests, configuration, provider output, and existing tests before proposing a mutation. Use Write or Edit only for the approved plan, implementation, test, or redacted receipt; do not create, update, destroy, or fund Vast.ai resources without explicit operator approval.

## Output

- Source/destination route and data-class decision
- Transfer, checksum, checkpoint, and recovery evidence
- Retention, credential revocation, and residual-storage receipt

Return location types and IDs, byte/file counts, checksums, checkpoint age, verification result, and remaining storage owner.

## Examples

A training dataset moves from a saved cloud connection to `C.123:/workspace/data`, is verified in a staging directory, and checkpoints return to a run-specific cloud prefix before the instance is destroyed.

## Error Handling

| Failure | Response |
| --- | --- |
| Requested route is unsupported | Choose a documented intermediate instance, volume, or cloud path. |
| Checksum differs | Quarantine the destination and repeat from a known source; do not train on it. |
| Instance is nearing expiry or failure | Prioritize external checkpoint recovery and record any unrecoverable window. |
| Credential is broader than the prefix | Stop the transfer and issue a narrower credential. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Official CLI file copy](https://github.com/vast-ai/vast-cli/blob/master/vastai/SKILL.md#file-copy)
- [Manage instances data notes](https://docs.vast.ai/guides/instances/manage-instances)
- [Billing and storage charges](https://docs.vast.ai/guides/reference/billing)
