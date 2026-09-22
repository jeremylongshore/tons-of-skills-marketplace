---
name: castai-core-workflow-a
description: 'Connect a Kubernetes cluster to CAST AI in observation-first mode and establish a trustworthy cost baseline before automation. Use when onboarding a new EKS, GKE, AKS, or CAST AI Anywhere cluster. Trigger with: "connect a cluster to CAST AI", "start CAST AI cost monitoring", "onboard CAST AI safely".'
allowed-tools: Read, Grep, Write, Edit, Bash(castctl:*), Bash(kubectl:*)
version: 2.0.0
argument-hint: '[kube-context-or-onboarding-plan]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - kubernetes
  - cast-ai
  - onboarding
  - cost-monitoring
compatibility: 'Supports CAST AI documented connection paths; cloud permissions and available features vary by provider and subscription'
---

# CAST AI Observation-First Onboarding

## Overview

Connect one approved cluster with the recommended castctl path, keep optimization automation off initially, and prove identity, telemetry, ownership, and rollback before expanding control.

## Prerequisites

- A named kube context for EKS, GKE, AKS, or a supported CAST AI Anywhere environment
- Cluster-admin access for installation and reviewed least-privilege cloud permissions
- metrics-server when Workload Autoscaling will be evaluated
- An owner, maintenance window, rollback decision, and evidence location

## Instructions

### Step 1: Establish ownership

Use Read and Grep to locate existing CAST AI, autoscaler, Terraform, Helm, and GitOps definitions. Stop if another controller owns node provisioning or workload HPA behavior and no coexistence decision exists.

### Step 2: Preview the connection

Use Bash(castctl:\*) to verify the installed client, authenticate interactively to the intended organization, and run the documented connection dry-run. Record detected provider, cluster, region, selected features, namespace, and proposed cloud changes without connecting.

### Step 3: Review permissions and features

Confirm least-privilege cloud access and the exact cluster context. Cost Monitoring is always enabled; select Node Autoscaling or Workload Autoscaling only when entitlement, metrics, disruption, and ownership prerequisites are met. Use Write or Edit to capture the approved choices in the repository runbook.

### Step 4: Connect the cluster

Run the reviewed castctl connection during the approved window. Do not substitute the deprecated script flow for a supported castctl environment. Preserve the console URL and sanitized command receipt, never browser tokens or API keys.

### Step 5: Verify observation mode

Use Bash(kubectl:\*) to verify namespace workloads, readiness, events, and metrics prerequisites. Confirm the console receives the intended cluster and cost data while automation remains in the approved state. Allow sufficient data before judging savings or recommendations.

### Step 6: Hand off automation separately

Document baseline time, current controllers, policy candidates, protected workloads, and rollback owner. Make automation enablement a separate reviewed change using `castai-core-workflow-b`.

## Tool Discipline

Use Read and Grep to establish source-of-truth ownership. Use Write and Edit for the onboarding record and runbook. Use Bash(castctl:_) for documented auth, dry-run, connection, and status operations; use Bash(kubectl:_) for bounded verification. Never echo credentials or infer permission scope.

## Output

- Reviewed dry-run and permission inventory
- One connected cluster with documented feature state
- Agent and telemetry health evidence
- Baseline and automation handoff record

## Examples

An EKS team connects Cost Monitoring first, collects a representative baseline, and delays Node Autoscaling until Karpenter ownership is decided. A GKE team verifies metrics-server before selecting Workload Autoscaling.

## Error Handling

| Failure                                   | Response                                              |
| ----------------------------------------- | ----------------------------------------------------- |
| castctl detects the wrong cluster         | Stop and correct kube context before connecting       |
| Existing provisioner ownership is unclear | Keep optimization disabled and resolve architecture   |
| Agent is not ready                        | Collect events and logs; do not enable automation     |
| Cost data is incomplete                   | Verify telemetry and wait for a representative window |

## Resources

- [Onboarding evidence and source notes](references/official-docs.md)
- [Connect with castctl](https://docs.cast.ai/docs/connect-with-castctl)
- [Connecting your cluster](https://docs.cast.ai/docs/connecting-your-cluster)
- [Cost monitoring overview](https://docs.cast.ai/docs/cost-management)
