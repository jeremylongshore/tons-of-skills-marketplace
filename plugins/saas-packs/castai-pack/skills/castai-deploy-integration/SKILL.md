---
name: castai-deploy-integration
description: 'Deploy CAST AI through a reviewable GitOps or Terraform lane with pinned artifacts, explicit control ownership, and staged promotion. Use when standardizing CAST AI across clusters or moving console-managed configuration into code. Trigger with: "deploy CAST AI with GitOps", "manage CAST AI as code", "roll out CAST AI to multiple clusters".'
allowed-tools: Read, Grep, Write, Edit, Bash(helm:*), Bash(terraform:*), Bash(kubectl:*), Bash(castctl:*)
version: 2.0.0
argument-hint: '[infrastructure-root-and-cluster-ring]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - kubernetes
  - cast-ai
  - gitops
  - deployment
compatibility: 'Requires an existing infrastructure delivery system and cloud-specific CAST AI permissions reviewed for each target cluster'
---

# CAST AI Deployment Integration

## Overview

Make the repository the declared source of truth for CAST AI installation and policy, then promote one cluster ring at a time. Keep registration, cloud permissions, chart configuration, and automation decisions independently reviewable.

## Prerequisites

- Target clusters grouped into canary, staging, and production rings
- A chosen owner: Terraform, GitOps Helm, castctl, or console
- Pinned provider, module, chart, and policy inputs
- Secret delivery that does not commit or render credentials into artifacts

## Instructions

### Step 1: Inventory existing ownership

Use Read and Grep to find CAST AI resources, individual component charts, the unified `castai` chart, Terraform state addresses, Flux or Argo CD objects, and console-only settings. Stop if two systems can reconcile the same resource.

### Step 2: Define the repository contract

Use Write or Edit to separate cluster registration, cloud IAM, Helm values, scaling policies, node templates, workload annotations, notification settings, and automation toggles. Parameterize organization, region, and cluster identity; never parameterize a secret with a committed literal.

### Step 3: Render and plan

Use Bash(helm:_) to lint and render the pinned chart. Use Bash(terraform:_) to format, validate, and save a plan. Use Bash(kubectl:\*) for client-side manifest checks. Review RBAC, webhooks, CRDs, namespace, disruption behavior, deleted resources, and ownership transfers.

### Step 4: Handle existing installations

If the cluster uses individual CAST AI Helm releases, evaluate the documented `castctl cluster migrate` path to the unified umbrella chart. Use Bash(castctl:\*) only after recording current releases, values, rollback, and the exact cluster context.

### Step 5: Promote by ring

Apply through the declared delivery controller to one canary cluster. Verify agent health, telemetry, policy state, and automation boundaries before staging and production. Require an explicit approval between rings and preserve the reviewed artifact digest.

### Step 6: Prove rollback and drift detection

Document how to revert the Git commit or Terraform change, restore policy assignments, and detect console drift. A rollback must preserve cluster connectivity and workload availability; do not assume uninstalling is harmless.

## Tool Discipline

Use Read and Grep for ownership discovery. Use Write and Edit for infrastructure definitions and runbooks. Use Bash(helm:_), Bash(terraform:_), and Bash(kubectl:_) for bounded render, plan, and verification. Use Bash(castctl:_) only for documented migration or connection actions inside an approved window.

## Output

- Source-of-truth and ownership map
- Pinned rendered and planned artifacts
- Ring promotion and health receipts
- Drift and rollback procedure

## Examples

A team migrates legacy per-component releases to the unified chart in one canary cluster, then lets Argo CD own the pinned result. Terraform continues to own cloud IAM but not Helm values.

## Error Handling

| Failure                                       | Response                                    |
| --------------------------------------------- | ------------------------------------------- |
| Two reconcilers own one object                | Stop promotion and choose one authority     |
| Plan deletes registration or IAM unexpectedly | Reject the plan and reconcile state         |
| Rendered output includes a key                | Remove the secret from values and rotate it |
| Canary loses telemetry                        | Roll back before promoting another cluster  |

## Resources

- [Deployment evidence and source notes](references/official-docs.md)
- [Connect with castctl](https://docs.cast.ai/docs/connect-with-castctl)
- [Connecting your cluster](https://docs.cast.ai/docs/connecting-your-cluster)
- [Workload Autoscaler configuration](https://docs.cast.ai/docs/workload-autoscaling-configuration)
