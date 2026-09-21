---
name: castai-prod-checklist
description: 'Run a fail-closed production-readiness review for a CAST AI cluster before enabling or expanding automation. Use when deciding onboarding approval, control-plane migration, or rollout between cluster rings. Trigger with: "review CAST AI for production", "CAST AI go-live checklist", "approve CAST AI automation".'
allowed-tools: Read, Grep, Write, Edit, Bash(kubectl:*), Bash(helm:*), Bash(terraform:*), Bash(castctl:*)
version: 2.0.0
argument-hint: '[cluster-and-change-record]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - kubernetes
  - cast-ai
  - production-readiness
  - governance
compatibility: 'Requires access to the target cluster, declared infrastructure source, application SLOs, and change-management evidence'
---

# CAST AI Production Readiness Gate

## Overview

Approve production only when identity, ownership, connectivity, observability, scaling safety, cost interpretation, rollback, and evidence are all explicit. An unchecked or unknown item is a stop, not a soft pass.

## Prerequisites

- Exact production kube context and CAST AI organization/region
- Reviewed infrastructure plan and pinned artifacts
- Workload owners, SLOs, PDBs, HPAs, quotas, and maintenance window
- Incident, rollback, and support escalation owners

## Instructions

### Step 1: Verify identity and ownership

Use Read and Grep to prove cluster, organization, region, cloud account, IaC source, reconcilers, and secret references. Confirm one owner for node provisioning, vertical rightsizing, and each HPA.

### Step 2: Verify installation and access

Use Bash(castctl:_) for supported version or status inspection, Bash(helm:_) for pinned release evidence, and Bash(kubectl:\*) for component readiness and warning events. Confirm least-privilege cloud permissions and required outbound connectivity.

### Step 3: Verify scaling guardrails

Review node templates, maximum CPU, cloud quotas, protected namespaces, workload policy assignment, minimum/maximum requests, apply mode, recommendation confidence, PDB behavior, HPA bounds, and ownership transfer. Reject deprecated cluster minimum CPU configuration.

### Step 4: Verify cost and reporting

Confirm baseline source, representative data window, public versus adjusted prices, automation adoption, and reconciliation owner. Do not use available or modeled savings as an unconditional release gate.

### Step 5: Verify delivery and rollback

Use Bash(terraform:_) for the saved plan and Bash(helm:_) for the reviewed render. Confirm no unexpected deletion, disconnect, IAM expansion, CRD replacement, webhook collision, or automation enablement. Use Write or Edit to record tested rollback steps and thresholds.

### Step 6: Make the decision

Record PASS only when every required item has evidence. Otherwise record HOLD with the exact owner and missing proof. Approve one cluster ring and one automation dimension at a time.

## Tool Discipline

Use Read and Grep for evidence review. Use Write and Edit for the signed gate record. Use Bash(kubectl:_), Bash(helm:_), Bash(terraform:_), and Bash(castctl:_) for non-secret inspection, render, and plan operations; do not perform the production change from the checklist.

## Output

- Evidence-linked readiness matrix
- Explicit PASS or HOLD decision
- Approved scope, window, and owners
- Rollback and incident triggers

## Examples

A cluster passes observation readiness but holds node automation because Karpenter ownership is unresolved. Another passes a Deferred workload canary while managed HPA takeover remains out of scope.

## Error Handling

| Failure                                   | Response                                 |
| ----------------------------------------- | ---------------------------------------- |
| Evidence is stale or from another cluster | Mark the gate HOLD                       |
| Ownership is shared or implicit           | Resolve control authority before release |
| Rollback is untested                      | Limit to observation mode                |
| Secret appears in an artifact             | Stop, rotate, and regenerate evidence    |

## Resources

- [Readiness evidence and source notes](references/official-docs.md)
- [Connect with castctl](https://docs.cast.ai/docs/connect-with-castctl)
- [Node Autoscaling](https://docs.cast.ai/docs/autoscaler)
- [Workload Autoscaler overview](https://docs.cast.ai/docs/workload-autoscaling-overview)
