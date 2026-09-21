---
name: castai-ci-integration
description: 'Build a fail-closed CI lane for CAST AI configuration without exposing production credentials to untrusted changes. Use when validating CAST AI Terraform, Helm values, workload annotations, or an authorized read-only API smoke test. Trigger with: "test CAST AI in CI", "gate CAST AI changes", "add a CAST AI contract job".'
allowed-tools: Read, Grep, Write, Edit, Bash(terraform:*), Bash(helm:*), Bash(kubectl:*), Bash(castctl:*)
version: 2.0.0
argument-hint: '[workflow-or-infrastructure-path]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - kubernetes
  - cast-ai
  - ci-integration
  - operations
compatibility: 'Requires a repository with CAST AI infrastructure definitions; any live probe requires a protected environment and a dedicated read-only identity'
---

# CAST AI CI Contract Lane

## Overview

Keep pull-request checks local and credential-free. Validate syntax, rendered Kubernetes objects, policy invariants, and destructive change boundaries before allowing a separately protected job to inspect a real CAST AI environment.

## Prerequisites

- The workflow, Terraform, Helm values, and workload manifest paths in scope
- An explicit source of truth for each CAST AI setting
- Maintainer approval for any protected live probe

## Instructions

### Step 1: Map the trust boundary

Use Read and Grep to identify fork execution, secret references, Terraform backends, generated plans, Helm values, kubeconfig use, and direct CAST AI calls. Classify each check as offline, protected read-only, or prohibited.

### Step 2: Build the required offline lane

Use Bash(terraform:_) for formatting, initialization without applying, validation, and a saved plan. Use Bash(helm:_) to lint or template the pinned chart and Bash(kubectl:\*) only for client-side schema validation against rendered manifests. Treat unexpected resource deletion, provider replacement, cluster disconnect, automation enablement, or HPA ownership transfer as review-blocking changes.

### Step 3: Validate CAST AI policy invariants

Use Write or Edit to add deterministic checks for approved regions, cluster identifiers, policy names, node-template bounds, workload automation modes, protected namespaces, disruption budgets, and maximum CPU limits. Reject deprecated cluster minimum CPU settings and unreviewed wildcard scope.

### Step 4: Isolate the optional live lane

If live evidence is required, place it in an independent protected-environment job that cannot run for forks. Use a dedicated read-only organization-scoped identity, a pinned CAST AI region, a fixed cluster allowlist, a short timeout, and redacted output. Prefer a documented status read; never enable automation or apply infrastructure from the probe.

### Step 5: Prove negative behavior

Run the workflow with missing and sentinel credentials. Confirm the offline lane stays green, the live lane skips safely, logs contain no key or raw cluster inventory, and plan artifacts have restricted retention.

## Tool Discipline

Use Read and Grep for workflow and configuration inspection. Use Write and Edit for checks and workflow changes. Use Bash(terraform:_), Bash(helm:_), Bash(kubectl:_), and Bash(castctl:_) only for their documented validation or dry-run operations; do not apply, connect, disconnect, or mutate a live cluster without a separate approved change window.

## Output

- A required credential-free validation job
- A separately protected read-only smoke test, if justified
- Policy, deletion, and secret-handling assertions
- Negative-path and redaction receipts

## Examples

A pull request renders the pinned CAST AI chart, validates Terraform, and rejects a new HPA ownership transfer. A release job may inspect one approved cluster only after environment approval and records status classes rather than raw API payloads.

## Error Handling

| Failure                                   | Meaning                           | Response                                              |
| ----------------------------------------- | --------------------------------- | ----------------------------------------------------- |
| A fork can read a CAST AI key             | CI trust boundary failed          | Disable the live job and rotate the exposed identity  |
| A plan enables automation unexpectedly    | Change exceeds reviewed intent    | Block and require an explicit policy review           |
| Offline checks need the network           | Required lane is nondeterministic | Pin fixtures and local schemas                        |
| A rendered object transfers HPA ownership | Workload control may change       | Require workload-owner approval and rollback evidence |

## Resources

- [CI evidence and source notes](references/official-docs.md)
- [CAST AI API access](https://docs.cast.ai/docs/api-access)
- [Connect with castctl](https://docs.cast.ai/docs/connect-with-castctl)
- [Autoscaler settings](https://docs.cast.ai/docs/autoscaler-settings)
