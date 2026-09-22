---
name: castai-common-errors
description: 'Diagnose CAST AI connection, agent, node autoscaling, and workload autoscaling failures without making speculative changes. Use when a cluster is disconnected, recommendations are absent, pods are not optimized, or capacity does not scale as expected. Trigger with: "debug CAST AI", "CAST AI is not scaling", "why is CAST AI disconnected".'
allowed-tools: Read, Grep, Bash(kubectl:*), Bash(helm:*), Bash(castctl:*)
version: 2.0.0
argument-hint: '[cluster-context-or-symptom]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - kubernetes
  - cast-ai
  - diagnostics
  - operations
compatibility: 'Requires read access to the target kube context; console or API evidence may require an appropriately scoped CAST AI identity'
---

# CAST AI Failure Triage

## Overview

Separate observation, connectivity, policy, capacity, and disruption failures before proposing a change. Preserve the failing state, use current component topology, and stop when the evidence requires cloud-provider or CAST AI support access.

## Prerequisites

- The exact kube context, cluster, region, time window, and observed symptom
- Read-only access to the `castai-agent` namespace
- The declared installation owner: castctl, Terraform, GitOps, or console

## Instructions

### Step 1: Freeze the symptom

Record expected versus actual behavior, timestamps, workload identity, pending-pod reason, and recent configuration changes. Use Read and Grep on runbooks and IaC to determine whether Cost Monitoring, Node Autoscaling, or Workload Autoscaling is actually enabled.

### Step 2: Check installation health

Use Bash(castctl:_) for version or non-mutating status commands supported by the installed client. Use Bash(helm:_) to inspect releases and values, then Bash(kubectl:\*) to inspect workloads, readiness, events, and bounded logs in `castai-agent`. Do not restart components before collecting evidence.

### Step 3: Classify the failure plane

| Plane            | Evidence                                               | Likely boundary                                             |
| ---------------- | ------------------------------------------------------ | ----------------------------------------------------------- |
| Connection       | Agent readiness, outbound failures, console disconnect | Identity, network, or cloud permissions                     |
| Node scaling     | Pending pods, policy bounds, node-template fit         | Unsatisfied constraints or maximum CPU boundary             |
| Workload scaling | Missing recommendations, policy assignment, metrics    | Metrics server, confidence, policy, or unsupported workload |
| Disruption       | Eviction denial, PDB events, deferred changes          | PDB or selected apply mode                                  |
| Reporting        | Missing cost or savings window                         | Ingestion, baseline, adoption, or pricing configuration     |

### Step 4: Test one hypothesis

Choose the smallest reversible check. Confirm regional endpoint alignment, effective scaling-policy assignment, metrics availability, supported workload type, node-template constraints, and cloud quota. Treat the deprecated cluster minimum CPU setting as migration debt, not a current control to add.

### Step 5: Decide the owner and remedy

Map the evidence to the owning layer. Change repository-managed values only through their source of truth; do not mix console edits into Terraform or GitOps ownership. Escalate with a redacted bundle when the failure is inside the hosted control plane or an undocumented provider response.

## Tool Discipline

Use Read and Grep for configuration and runbook evidence. Use Bash(kubectl:_), Bash(helm:_), and Bash(castctl:\*) only for bounded inspection commands. Do not apply, upgrade, restart, connect, disconnect, or expose Secret objects during diagnosis.

## Output

- A timestamped symptom and environment summary
- Evidence grouped by failure plane
- One supported root-cause hypothesis with confidence
- A reversible remedy, rollback condition, and escalation owner

## Examples

Recommendations are absent because metrics-server is missing, so the remedy belongs to cluster observability. A node remains pending because every approved node template conflicts with its constraints; increasing a global limit without reviewing the workload is not the remedy.

## Error Handling

| Failure                               | Response                                                            |
| ------------------------------------- | ------------------------------------------------------------------- |
| Kube context is ambiguous             | Stop before any cluster command and resolve it                      |
| Logs include credentials or inventory | Redact locally and do not attach raw output                         |
| A PDB blocks Immediate mode           | Preserve the PDB and evaluate Deferred mode with the workload owner |
| Evidence points to cloud quota        | Escalate to the cloud owner with the exact denied dimension         |

## Resources

- [Triage evidence and source notes](references/official-docs.md)
- [Node autoscaling overview](https://docs.cast.ai/docs/autoscaler)
- [Workload Autoscaler overview](https://docs.cast.ai/docs/workload-autoscaling-overview)
- [Connecting your cluster](https://docs.cast.ai/docs/connecting-your-cluster)
