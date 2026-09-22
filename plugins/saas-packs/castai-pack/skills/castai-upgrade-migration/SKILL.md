---
name: castai-upgrade-migration
description: 'Upgrade the CAST AI umbrella chart or migrate standalone releases with preserved values, explicit downtime, staged verification, and recovery evidence. Use when performing component updates, GitOps adoption, or consolidation with castctl. Trigger with: "upgrade CAST AI", "migrate CAST AI Helm releases", "move CAST AI to the umbrella chart".'
allowed-tools: Read, Grep, Write, Edit, Bash(helm:*), Bash(kubectl:*), Bash(castctl:*), Bash(terraform:*)
version: 2.0.0
argument-hint: '[cluster-and-target-release]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - kubernetes
  - cast-ai
  - upgrades
  - migration
compatibility: 'Umbrella-chart upgrades using reset-then-reuse-values require Helm 3.14 or newer; standalone migration requires current castctl support'
---

# CAST AI Upgrade and Umbrella Migration

## Overview

Inventory the installed topology, pin the target, preserve values, and rehearse recovery before changing a cluster. Treat standalone-to-umbrella consolidation as a downtime-bearing migration, not an ordinary chart bump.

## Prerequisites

- Exact kube context, installation owner, current releases, chart/provider locks, and target
- Maintenance window, workload and platform owners, rollback threshold, and evidence path
- Current backups of declared values and infrastructure state references without secret material

## Instructions

### Step 1: Classify the installation

Use Bash(helm:\*) to determine whether the namespace has one `castai` umbrella release or multiple standalone releases. Use Read and Grep to map Terraform, GitOps, console, and castctl ownership. Do not proceed while authorities conflict.

### Step 2: Capture the baseline

Use Bash(kubectl:\*) for component images, readiness, recent warning events, policy-visible workload health, PDBs, HPAs, and pending pods. Record selected umbrella mode and optional component overrides.

### Step 3: Review target and render

Pin the target chart or provider from current release metadata. Use Bash(helm:_) to render the proposed umbrella values and Bash(terraform:_) to save a reviewed plan when Terraform owns delivery. Inspect CRDs, RBAC, webhooks, component modes, removed values, and automation changes.

### Step 4: Choose upgrade or migration

For an existing umbrella release, use the documented chart upgrade with `--reset-then-reuse-values`; Helm 3.14 or newer is required. Pin the current chart version when changing configuration without changing components. For standalone releases, use Bash(castctl:\*) with `cluster migrate`; expect a window where components and both autoscalers are paused.

### Step 5: Protect recovery

Before standalone migration, set and protect the values-dump destination. If umbrella installation fails, preserve the generated values and debug snapshot, correct the conflict, then use documented values-file recovery. Do not publish dumps; they can contain sensitive configuration.

### Step 6: Verify and promote

Confirm one intended release, component readiness, cluster identity, telemetry, policy state, automation mode, HPAs, PDBs, and node/workload behavior. Compare the baseline and hold promotion on any unexplained drift.

## Tool Discipline

Use Read and Grep for release and ownership evidence. Use Write and Edit for the plan and recovery record. Use Bash(helm:_), Bash(terraform:_), Bash(kubectl:_), and Bash(castctl:_) only inside the approved render, migration, upgrade, and verification boundaries.

## Output

- Current-versus-target topology and artifact pins
- Reviewed upgrade or migration plan
- Preserved values and recovery procedure
- Post-change parity and health receipt

## Examples

A legacy cluster migrates four standalone releases with castctl during a maintenance window and verifies one umbrella release afterward. A GitOps cluster pins its current chart while changing values, avoiding an accidental component upgrade.

## Error Handling

| Failure                         | Response                                                                      |
| ------------------------------- | ----------------------------------------------------------------------------- |
| Helm is older than 3.14         | Upgrade the client before using reset-then-reuse-values                       |
| Migration dump contains secrets | Restrict it immediately and sanitize only a copy for review                   |
| Umbrella install fails          | Preserve generated recovery artifacts and use documented values-file recovery |
| Post-change automation differs  | Hold promotion and restore the reviewed mode                                  |

## Resources

- [Migration evidence and source notes](references/official-docs.md)
- [Hosted components](https://docs.cast.ai/docs/hosted-components)
- [Connect with castctl](https://docs.cast.ai/docs/connect-with-castctl)
- [Workload Autoscaler configuration](https://docs.cast.ai/docs/workload-autoscaling-configuration)
