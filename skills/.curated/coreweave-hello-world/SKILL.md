---
name: coreweave-hello-world
description: 'Deploy a GPU workload on CoreWeave with kubectl.

  Use when running your first GPU job, testing inference,

  or verifying CoreWeave cluster access.

  Trigger with phrases like "coreweave hello world", "coreweave first deploy",

  "coreweave gpu test", "run on coreweave".

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
# CoreWeave GPU smoke-test review

> **Community-contributed.** Not affiliated with, endorsed by, or sponsored by CoreWeave, Inc. CoreWeave is a registered trademark of CoreWeave, Inc.

## Overview

Check a small, owner-approved GPU Job and its cleanup before scaling a workload.
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

1. For first-time cluster, Node Pool, or self-managed inference provisioning, start with the official CoreWeave skills. This compatibility entry adds a bounded GPU runtime smoke-test review.

2. Choose an existing sandbox namespace, one GPU, an approved image digest and a short activeDeadlineSeconds. Agree the GPU-hour budget and exact Job name before scheduling.

3. Validate the supplied Job with server dry-run. Confirm limits.nvidia.com/gpu, CPU/memory, service account, backoffLimit and ttlSecondsAfterFinished. Discover the current instance ID rather than copying a legacy GPU label.

4. After explicit workload approval, apply only that Job. Wait for Complete or Failed with a timeout; a one-shot Job may finish before a Pod ever has an observable Ready condition.

5. Review a non-sensitive result such as CUDA availability and GPU enumeration. Record failure states separately from a successful test. Delete only the approved Job after evidence is retained; never its dataset PVC.

## Examples

Set `CW_CONTEXT` and `CW_NAMESPACE` from the approved access request. Set each referenced resource variable to the exact owner-selected resource, not a wildcard or the first matching Pod.

```bash
: "${CW_CONTEXT:?approved context required}" "${CW_NAMESPACE:?approved namespace required}"
kubectl --context="$CW_CONTEXT" --namespace="$CW_NAMESPACE" apply --dry-run=server -f smoke-job.yaml
# After the owner approves this exact Job and budget:
kubectl --context="$CW_CONTEXT" --namespace="$CW_NAMESPACE" apply -f smoke-job.yaml
kubectl --context="$CW_CONTEXT" --namespace="$CW_NAMESPACE" wait --for=condition=complete "job/$CW_JOB" --timeout=5m
kubectl --context="$CW_CONTEXT" --namespace="$CW_NAMESPACE" get "job/$CW_JOB"
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
- [Primary reference 1](https://docs.coreweave.com/products/cks/clusters/scheduling/workload-scheduling)
- [Primary reference 2](https://kubernetes.io/docs/reference/kubectl/)

## Evidence status

Source-reviewed guidance with offline repository checks. No live CoreWeave account, paid GPU workload or provider-backed behavioral evaluation was used to validate this guide. Record live results separately before claiming workload success.
