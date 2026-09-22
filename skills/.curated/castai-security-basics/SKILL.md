---
name: castai-security-basics
description: 'Review CAST AI identity, Kubernetes RBAC, cloud IAM, Kvisor, network, and evidence boundaries against enabled features. Use when preparing onboarding, automation expansion, or security-agent changes. Trigger with: "secure CAST AI", "audit CAST AI permissions", "review Kvisor access".'
allowed-tools: Read, Grep, Write, Edit, Bash(kubectl:*), Bash(helm:*)
version: 2.0.0
argument-hint: '[cluster-and-enabled-features]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - kubernetes
  - cast-ai
  - security
  - least-privilege
compatibility: 'Requires declared CAST AI feature mode and read access to rendered Kubernetes and cloud permission definitions'
---

# CAST AI Least-Privilege Review

## Overview

Review permissions against the components actually enabled. Distinguish observation, optimization, operator lifecycle, Kvisor telemetry, optional cluster proxy, and cloud-provider access instead of labeling the entire installation read-only or full-access.

## Prerequisites

- Selected umbrella-chart mode and optional features
- Rendered Helm resources, service accounts, RBAC, cloud IAM, and secret references
- Organization roles, API-key inventory, network policy, and data-classification rules

## Instructions

### Step 1: Establish feature scope

Use Read and Grep to map read-only, Workload Autoscaler, Node Autoscaler, full, Kvisor options, reliability metrics, GPU or storage telemetry, operator management, and cluster proxy. Flag enabled components that lack a named business owner.

### Step 2: Review identity boundaries

Separate human castctl login from service API keys. Verify organization role bindings, region, enterprise child targeting, storage, rotation, and revocation. Reject keys in values, URLs, Terraform output, logs, or support artifacts.

### Step 3: Review Kubernetes permissions

Use Bash(helm:_) to render the pinned installation and Bash(kubectl:_) for bounded RBAC inspection. Compare each service account to current documented permissions. Account for agent deployment patching, operator lifecycle permissions, Kvisor cluster reads, optional scan jobs, and feature-gated token or pod-resize permissions.

### Step 4: Review cloud permissions

Map each AWS, GCP, Azure, or other permission to monitoring, onboarding, automation, discovery, commitments, or storage telemetry. Do not reuse an automation role for read-only monitoring when the provider supports narrower access.

### Step 5: Review network and data paths

Document regional egress, private connectivity, webhook destinations, telemetry classes, retention, and support-transfer controls. Do not invent a static IP allowlist or a broad `0.0.0.0/0` policy under the label of least privilege.

### Step 6: Record disposition

Use Write or Edit to mark every finding KEEP, NARROW, REMOVE, or INVESTIGATE with owner, evidence, risk, and rollback. Treat Kvisor security documentation as evolving and verify current product scope before enabling a feature.

## Tool Discipline

Use Read and Grep for configuration and permission mapping. Use Write and Edit for the review record. Use Bash(helm:_) and Bash(kubectl:_) only for rendered and effective RBAC inspection; never retrieve Secret data or mutate access.

## Output

- Enabled-feature and component inventory
- Human, service, Kubernetes, and cloud identity matrix
- Network, telemetry, and retention boundary
- Evidence-linked permission dispositions

## Examples

A read-only deployment retains agent snapshot reads but rejects node-provisioning cloud actions. Kvisor storage telemetry is held until its provider permissions and data audience are explicitly approved.

## Error Handling

| Failure                                    | Response                                                           |
| ------------------------------------------ | ------------------------------------------------------------------ |
| Feature mode is unknown                    | Inspect the release before judging permissions                     |
| Permission has no documented feature owner | Mark it INVESTIGATE, not safe                                      |
| A key is exposed                           | Revoke, rotate, and remove the exposure                            |
| Current Kvisor behavior is ambiguous       | Hold the feature and verify current documentation/support guidance |

## Resources

- [Security evidence and source notes](references/official-docs.md)
- [Kubernetes permissions](https://docs.cast.ai/docs/kubernetes-permissions)
- [Cloud permissions](https://docs.cast.ai/docs/cloud-permissions)
- [Kvisor](https://docs.cast.ai/docs/kvisor)
