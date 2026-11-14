---
name: coreweave-cost-tuning
description: 'Optimize CoreWeave GPU cloud costs with right-sizing and scheduling.

  Use when reducing GPU spend, selecting cost-effective instances,

  or implementing scale-to-zero for dev workloads.

  Trigger with phrases like "coreweave cost", "coreweave pricing",

  "reduce coreweave spend", "coreweave budget".

  '
allowed-tools: Read, Write, Edit, Bash(kubectl:*), Grep
version: 1.15.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- gpu-cloud
- kubernetes
- inference
- coreweave
compatibility: Designed for Claude Code
---
# CoreWeave Cost experiment planning

> **Community-contributed.** Not affiliated with, endorsed by, or sponsored by CoreWeave, Inc. CoreWeave is a registered trademark of CoreWeave, Inc.

## Overview

Evaluate reversible capacity changes against the actual contract and measured workload.
Use Read to inspect the approved input files, Write the evidence report, and Edit only the proposed local artifact before review.
These procedures complement [CoreWeave’s official skills](https://github.com/coreweave/skills); they do not redistribute or replace that upstream distribution.

## Prerequisites

- The owner-approved organization, cluster context, namespace and resource names.
- A trusted kubeconfig from the approved secret location; no raw credentials in source, logs or terminal history.
- Installed kubectl compatible with the cluster, and authority for each proposed read or change.
- An agreed success criterion, resource budget, evidence destination and recovery owner.

## Instructions

1. Determine whether this is CKS Reserved Instances, Flex, Spot, On-Demand, Dedicated Inference or Serverless billing. Pod replica count and billed capacity are different quantities.

2. Read current customer rates and usage over a defined window. Record units, sampling coverage, taxes/credits and reservation terms. Use the cost-review script for scenario arithmetic; telemetry multiplied by a rate is an estimate, not an invoice.

3. Identify one feasible experiment: scheduling an interruptible workload, changing a tested instance type, reducing unused on-demand Nodes or changing a serving limit. A model parameter count alone does not determine GPU memory or performance.

4. For right-sizing or quantization, verify representative quality, latency, memory and throughput first. Obtain the approved model artifact and supported image; do not invent a quantized repository name.

5. Have the owner approve the exact resource or contract change. Scaling Pods to zero does not cancel a reserved commitment or a Flex holding fee. Report realized billing changes only after reconciliation.

## Examples

Set `CW_CONTEXT` and `CW_NAMESPACE` from the approved access request. Set each referenced resource variable to the exact owner-selected resource, not a wildcard or the first matching Pod.

```bash
: "${CW_CONTEXT:?approved context required}" "${CW_NAMESPACE:?approved namespace required}"
kubectl --context="$CW_CONTEXT" --namespace="$CW_NAMESPACE" get resourcequota
kubectl --context="$CW_CONTEXT" --namespace="$CW_NAMESPACE" get "deployment/$CW_DEPLOYMENT" -o wide
kubectl --context="$CW_CONTEXT" --namespace="$CW_NAMESPACE" get hpa
# Optional, separately authorized cluster inventory:
kubectl --context="$CW_CONTEXT" get nodes -L node.kubernetes.io/instance-type
```

These are operator examples, not commands run by this package’s offline tests. Mutating examples require approval for the exact manifest, environment and budget before execution.

## Output

- A UTC-stamped review identifying the observed state, evidence coverage and unresolved assumptions.
- A specific proposed next step, the owner who can authorize it, and a measurable acceptance or recovery check.
- A clear incomplete result when credentials, capacity, metrics or live validation are unavailable.

## Error Handling

| Condition | Response |
|---|---|
| Authentication or authorization denied | Stop; verify the intended identity and scope without escalating permissions automatically. |
| Empty or stale evidence | Record unknown and collect a bounded fresh sample; never substitute zero or healthy. |
| Admission, rollout or acceptance failure | Preserve the sanitized error and use the reviewed recovery path with its owner. |
| Output may contain a secret or workload data | Restrict sharing and review/redact before retaining or uploading it. |

## Resources

- [Operator details and evidence boundaries](references/operator-notes.md)
- [Primary reference 1](https://docs.coreweave.com/platform/capacity-plans)
- [Primary reference 2](https://docs.coreweave.com/observability/usage-monitoring)
- [Primary reference 3](https://docs.coreweave.com/products/inference/billing)

## Evidence status

Source-reviewed guidance with offline repository checks. No live CoreWeave account, paid GPU workload or provider-backed behavioral evaluation was used to validate this guide. Record live results separately before claiming workload success.
