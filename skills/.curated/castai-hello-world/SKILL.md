---
name: castai-hello-world
description: 'Run a safe first CAST AI cluster connection that proves Cost Monitoring and agent health before enabling optimization. Use when starting a new evaluation, sandbox, or operator walkthrough. Trigger with: "CAST AI hello world", "try CAST AI safely", "connect my first CAST AI cluster".'
allowed-tools: Read, Grep, Write, Bash(castctl:*), Bash(kubectl:*)
version: 2.0.0
argument-hint: '[sandbox-kube-context]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - kubernetes
  - cast-ai
  - quickstart
  - onboarding
compatibility: 'Requires a supported Kubernetes cluster, castctl, reviewed cloud permissions, and an approved CAST AI organization'
---

# CAST AI Safe First Connection

## Overview

Prove the minimum useful loop: identify one sandbox cluster, preview the connection, connect with Cost Monitoring, verify telemetry, and leave optimization automation unchanged.

## Prerequisites

- A disposable or non-production kube context with an accountable owner
- castctl installed from an official distribution and authenticated to the intended organization
- Cluster-admin and reviewed provider permissions
- An approved evidence and cleanup plan

## Instructions

### Step 1: Confirm the sandbox

Use Bash(kubectl:\*) to print the current context and inspect only basic cluster identity. Use Read and Grep to ensure the cluster is not already owned by CAST AI, another autoscaler, Terraform, or GitOps.

### Step 2: Preview with castctl

Use Bash(castctl:\*) to check the client version and run the documented cluster connection dry-run. Review detected provider, cluster name, region, organization, proposed features, namespace, and cloud changes.

### Step 3: Record the decision

Use Write to capture the dry-run, selected cluster, owners, features, start time, expected telemetry, and cleanup path. Cost Monitoring is always enabled; do not select Node or Workload Autoscaling merely to complete a quickstart.

### Step 4: Connect once

Run the reviewed interactive connection. Confirm the prompt resolves the same cluster and organization. Keep the returned console URL, but never store the browser token, kubeconfig, or API key in the receipt.

### Step 5: Verify the loop

Use Bash(kubectl:\*) to verify `castai-agent` namespace workloads, readiness, and recent warning events. Confirm the console identifies the correct cluster and begins showing cost data. Treat an empty initial report as ingestion time, not proof of zero cost.

### Step 6: Close or hand off

If the evaluation continues, hand off to observation-first onboarding. If it ends, use the documented disconnect path only after reviewing cloud and cluster cleanup effects and preserving the final receipt.

## Tool Discipline

Use Read and Grep for ownership checks. Use Write for the sanitized quickstart receipt. Use Bash(castctl:_) for documented dry-run, connection, and status operations and Bash(kubectl:_) for bounded verification only.

## Output

- Reviewed connection preview
- One correctly identified sandbox cluster
- Agent and initial telemetry evidence
- Explicit continuation or cleanup owner

## Examples

A team connects a sandbox EKS cluster for Cost Monitoring, confirms agent readiness, and waits for representative data. It does not enable node automation or change workload requests during the first session.

## Error Handling

| Failure                                      | Response                                                 |
| -------------------------------------------- | -------------------------------------------------------- |
| The context is production                    | Stop and select an approved sandbox                      |
| Dry-run detects the wrong provider or region | Correct environment selection before connecting          |
| Agent pods fail readiness                    | Collect bounded evidence and do not add features         |
| Cleanup consequences are unclear             | Leave state unchanged and escalate to the platform owner |

## Resources

- [Quickstart evidence and source notes](references/official-docs.md)
- [Connect with castctl](https://docs.cast.ai/docs/connect-with-castctl)
- [Cost monitoring overview](https://docs.cast.ai/docs/cost-management)
- [Connecting your cluster](https://docs.cast.ai/docs/connecting-your-cluster)
