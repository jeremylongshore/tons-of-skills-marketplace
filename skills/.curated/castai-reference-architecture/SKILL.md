---
name: castai-reference-architecture
description: 'Design a CAST AI reference architecture that separates hosted control-plane services, in-cluster components, cloud permissions, delivery ownership, and Kubernetes scaling controls. Use when reviewing architecture, planning multi-cluster rollout, or mapping responsibilities. Trigger with: "design CAST AI architecture", "map CAST AI components", "review CAST AI control planes".'
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[estate-or-cluster-scope]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - kubernetes
  - cast-ai
  - architecture
  - governance
compatibility: 'Covers documented CAST AI connection and umbrella-chart modes; exact components and permissions depend on selected features and provider'
---

# CAST AI Reference Architecture

## Overview

Describe the real control and data paths for one estate. Avoid a generic vendor diagram: show where identity, telemetry, recommendations, mutations, cloud provisioning, GitOps, and operator approvals actually cross boundaries.

## Prerequisites

- Cluster inventory, providers, regions, network zones, and CAST AI organizations
- Selected modes: read-only, Workload Autoscaler, Node Autoscaler, or full
- IaC/GitOps ownership, existing provisioners, HPAs, PDBs, and data policy

## Instructions

### Step 1: Establish trust zones

Use Read and Grep to map CAST AI hosted services, regional API base, enterprise or organization identity, cloud accounts, Kubernetes API servers, CI, GitOps controllers, secret managers, and operator workstations.

### Step 2: Map in-cluster components by mode

Represent the unified umbrella chart and its selected tag mode. Shared components include the agent, spot handler, and Kvisor; automation modes add controllers, evictor, pod mutator, workload autoscaler/exporter, pod pinner, or live-migration components as documented. Do not show every component as present unconditionally.

### Step 3: Map control paths

Separate observation snapshots, cost telemetry, workload recommendations, mutating admission, Eviction API operations, native HPA management, pending-pod observation, node provisioning, and cloud API calls. Label which paths read, recommend, mutate, or provision.

### Step 4: Map permission boundaries

Show human castctl login, service API keys, enterprise child-organization targeting, Kubernetes service accounts, cloud IAM, and optional Kvisor capabilities. Link each privilege to a feature and identify the revocation owner.

### Step 5: Map configuration authority

Use Write or Edit to declare whether castctl, Terraform, Helm GitOps, console, or workload annotations own each setting. Highlight conflicts with Karpenter, cloud autoscalers, native HPAs, and manual console changes.

### Step 6: Add failure and rollback paths

Include regional API loss, agent disconnect, missing metrics, webhook failure, exhausted cloud quota, unsatisfied node template, PDB denial, and bad policy rollout. Show observation continuity, fail-safe behavior, escalation, and rollback authority.

## Tool Discipline

Use Read and Grep for repository and environment evidence. Use Write and Edit for the architecture record and diagram source. Do not infer selected features, components, permissions, or network reachability from a default installation.

## Output

- Trust-zone and component view
- Read/recommend/mutate/provision data-flow view
- Identity, permission, and configuration-authority matrix
- Failure, rollback, and escalation paths

## Examples

A read-only cluster shows telemetry components but no node provisioner. A full-mode cluster shows CAST AI workload recommendations and node provisioning while GitOps remains the sole authority for chart values and policy definitions.

## Error Handling

| Failure                                | Response                                             |
| -------------------------------------- | ---------------------------------------------------- |
| Selected umbrella mode is unknown      | Mark components unresolved and inspect the release   |
| Two systems own the same control       | Surface an architecture decision, not a silent merge |
| Network path is assumed                | Label it unverified until tested                     |
| Permission cannot be tied to a feature | Treat it as excess privilege for review              |

## Resources

- [Architecture evidence and source notes](references/official-docs.md)
- [Hosted components](https://docs.cast.ai/docs/hosted-components)
- [Kubernetes permissions](https://docs.cast.ai/docs/kubernetes-permissions)
- [Cloud permissions](https://docs.cast.ai/docs/cloud-permissions)
