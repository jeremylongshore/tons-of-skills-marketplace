---
name: coreweave-performance-tuning
description: 'Optimize CoreWeave GPU inference latency and throughput.

  Use when reducing inference latency, maximizing GPU utilization,

  or tuning batch sizes and concurrency.

  Trigger with phrases like "coreweave performance", "coreweave latency",

  "coreweave throughput", "optimize coreweave inference".

  '
allowed-tools: Read, Write, Edit, Bash(kubectl:*), Bash(python3:*), Grep
version: 1.13.0
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
# CoreWeave Measured performance experiments

> **Community-contributed.** Not affiliated with, endorsed by, or sponsored by CoreWeave, Inc. CoreWeave is a registered trademark of CoreWeave, Inc.

## Overview

Locate scheduling, image, model-load, queueing or execution bottlenecks before tuning.
Use Read to inspect the approved input files, Write the evidence report, and Edit only the proposed local artifact before review.
These procedures complement [CoreWeave’s official skills](https://github.com/coreweave/skills); they do not redistribute or replace that upstream distribution.

## Prerequisites

- The owner-approved organization, cluster context, namespace and resource names.
- A trusted kubeconfig from the approved secret location; no raw credentials in source, logs or terminal history.
- Installed kubectl compatible with the cluster, and authority for each proposed read or change.
- An agreed success criterion, resource budget, evidence destination and recovery owner.

## Cost and safety gate

Before any billable action, follow the [mandatory cost gate](references/cost-gate.md).
Use the local `scripts/review-cost-plan.py` helper to inspect the exact plan;
then obtain explicit user confirmation through the trusted approval channel.
No plan, missing price, changed digest or expired approval means no execution.
Default to offline inspection; server dry-run and Terraform plan are account calls.

## Instructions

1. Record the workload, image/model version, precision, GPU/Node count, input/output lengths, concurrency, topology and warm/cold cache state. Without comparable conditions a throughput comparison is inconclusive.

2. Split latency into scheduling, image pull, model load, queue delay, prefill and decode where the runtime exposes those measurements. Track failures and quality alongside latency and completed work.

3. Run one owner-approved staging change at a time, using the pinned runtime version documentation for flags. Verify an autoscaler metric adapter exists before proposing DCGM-based HPA configuration.

4. Compare the same evaluation set and load distribution against the baseline, including tail latency and cost per successful unit. Do not publish fabricated tokens/second, cold-start figures or fixed GPU rankings.

5. Promote only after the agreed quality and latency guardrails pass. Restore the prior version on regression, and preserve aggregate measurements without prompts or model outputs.

## Examples

Set `CW_CONTEXT` and `CW_NAMESPACE` from the approved access request. Set each referenced resource variable to the exact owner-selected resource, not a wildcard or the first matching Pod.

```bash
: "${CW_CONTEXT:?approved context required}" "${CW_NAMESPACE:?approved namespace required}"
kubectl --context="$CW_CONTEXT" --namespace="$CW_NAMESPACE" get "deployment/$CW_DEPLOYMENT" -o wide
kubectl --context="$CW_CONTEXT" --namespace="$CW_NAMESPACE" get hpa
kubectl --context="$CW_CONTEXT" --namespace="$CW_NAMESPACE" get events --sort-by=.metadata.creationTimestamp
kubectl --context="$CW_CONTEXT" --namespace="$CW_NAMESPACE" rollout history "deployment/$CW_DEPLOYMENT"
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
- [Primary reference 1](https://docs.coreweave.com/products/inference/scaling)
- [Primary reference 2](https://docs.coreweave.com/observability/usage-monitoring)
- [Primary reference 3](https://docs.vllm.ai/en/latest/)

## Evidence status

Source-reviewed guidance with offline repository checks. No live CoreWeave account, paid GPU workload or provider-backed behavioral evaluation was used to validate this guide. Record live results separately before claiming workload success.
