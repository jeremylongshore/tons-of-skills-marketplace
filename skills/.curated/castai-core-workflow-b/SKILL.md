---
name: castai-core-workflow-b
description: 'Enable CAST AI optimization through a measured canary with explicit node and workload policy boundaries. Use when observation-first onboarding is complete and Node Autoscaling, Workload Autoscaling, or managed HPA behavior can be activated. Trigger with: "enable CAST AI automation", "canary CAST AI autoscaling", "apply CAST AI optimization policies".'
allowed-tools: Read, Grep, Write, Edit, Bash(kubectl:*), Bash(terraform:*), Bash(castctl:*)
version: 2.0.0
argument-hint: '[cluster-and-canary-workload]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - kubernetes
  - cast-ai
  - autoscaling
  - rollout
compatibility: 'Requires a connected cluster, representative baseline, and approved ownership of node and workload scaling controls'
---

# CAST AI Controlled Optimization Rollout

## Overview

Turn recommendations into automation one bounded control at a time. Separate node capacity, vertical workload rightsizing, and horizontal replica control so each has an observable success condition and rollback.

## Prerequisites

- A healthy connected cluster and representative cost/workload baseline
- Current scaling policies, node templates, PDBs, HPAs, quotas, and protected namespaces
- A low-risk canary workload with an accountable owner

## Instructions

### Step 1: Define the control matrix

Use Read and Grep to map Node Autoscaling, Workload Autoscaler vertical mode, horizontal autoscaling, existing HPAs, and external provisioners. Record one owner for each control. Do not transfer HPA ownership implicitly.

### Step 2: Set guardrails

Use Write or Edit to define approved node templates, availability zones, instance lifecycle constraints, maximum CPU, workload minimums/maximums, policy assignment, PDB expectations, and rollback thresholds. Do not add the deprecated cluster minimum CPU setting.

### Step 3: Preview the change

Use Bash(terraform:_) to produce a saved reviewed plan when Terraform owns the configuration. Use Bash(castctl:_) only for supported inspection or documented feature operations. Confirm the diff affects the intended cluster and canary only.

### Step 4: Enable a workload canary

Choose Immediate mode only when controlled pod replacement is acceptable; the Eviction API will enforce PDBs. Choose Deferred mode when recommendations should apply on natural recreation. If horizontal autoscaling is enabled, review the native `autoscaling/v2` HPA configuration and any take-ownership decision.

### Step 5: Observe capacity and workload outcomes

Use Bash(kubectl:\*) to inspect pending pods, scheduling events, HPA state, pod replacements, PDBs, requests, and node changes. Compare availability, latency, saturation, and spend to the pre-change baseline; do not optimize on cost alone.

### Step 6: Expand or roll back

Expand one policy assignment group at a time only after the canary window passes. Roll back automation or policy assignment when error budget, capacity, disruption, or performance thresholds fail, while preserving evidence.

## Tool Discipline

Use Read and Grep for ownership and policy evidence. Use Write and Edit for the control matrix and rollback record. Use Bash(terraform:_), Bash(castctl:_), and Bash(kubectl:\*) only inside the approved plan, rollout, and observation boundaries.

## Output

- Node/workload/HPA ownership matrix
- Guardrails and canary selection
- Before-and-after availability, capacity, and cost evidence
- Expansion decision or tested rollback receipt

## Examples

A stateless deployment starts in Deferred vertical mode with no HPA ownership transfer. A later reviewed change enables policy-managed horizontal scaling after the workload owner approves replica bounds and stabilization behavior.

## Error Handling

| Failure                               | Response                                                                     |
| ------------------------------------- | ---------------------------------------------------------------------------- |
| PDB blocks Immediate mode             | Preserve availability and select Deferred mode or revise with owner approval |
| Pending pods cannot match templates   | Roll back and correct template constraints                                   |
| Existing HPA is unexpectedly replaced | Disable managed horizontal scaling and restore declared ownership            |
| Cost falls while latency regresses    | Roll back; performance guardrails take precedence                            |

## Resources

- [Rollout evidence and source notes](references/official-docs.md)
- [Scaling policies](https://docs.cast.ai/docs/woop-scaling-policies)
- [Horizontal Pod Autoscaling](https://docs.cast.ai/docs/horizontal-pod-autoscaling)
- [Node Autoscaling](https://docs.cast.ai/docs/autoscaler)
