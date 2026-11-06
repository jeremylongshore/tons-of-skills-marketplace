---
name: coreweave-core-workflow-b
description: 'Run distributed GPU training jobs on CoreWeave with multi-node PyTorch.

  Use when training models across multiple GPUs, setting up distributed training,

  or running fine-tuning jobs on CoreWeave H100 clusters.

  Trigger with phrases like "coreweave training", "coreweave multi-gpu",

  "distributed training coreweave", "fine-tune on coreweave".

  '
allowed-tools: Read, Write, Edit, Bash(kubectl:*), Bash(python3:*), Grep
version: 1.12.0
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
# CoreWeave Training launch and recovery review

> **Community-contributed.** Not affiliated with, endorsed by, or sponsored by CoreWeave, Inc. CoreWeave is a registered trademark of CoreWeave, Inc.

## Overview

Verify distributed training topology, storage and resume evidence before a costly launch.
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

1. Identify the actual launcher: a single-node torchrun Job is not multi-node training. For multi-node work, review rank/world-size, rendezvous, network reachability and the matching MPI, Slurm or operator contract.

2. Confirm current instance IDs, per-rank GPUs, RDMA-capable Node Pools, supported image/driver combination and a shared checkpoint path. Use current DFS documentation and inspect available StorageClasses; do not assume regional shared-hdd/shared-ssd class names.

3. Validate the full workload manifest and approved resource envelope. A minimal smoke run must verify rank discovery and a collective before a full budget is committed.

4. Prove recovery by writing a checkpoint to a temporary artifact path, verifying all required shards/checksums and resuming in staging. A mounted PVC alone does not establish checkpoint validity.

5. Use bounded logs and the fabric diagnostic skill for observed transport. Never relabel stateful distributed training as interruptible merely to clear a maintenance block; agree the checkpoint-aware interruption policy.

## Examples

Set `CW_CONTEXT` and `CW_NAMESPACE` from the approved access request. Set each referenced resource variable to the exact owner-selected resource, not a wildcard or the first matching Pod.

```bash
: "${CW_CONTEXT:?approved context required}" "${CW_NAMESPACE:?approved namespace required}"
kubectl --context="$CW_CONTEXT" --namespace="$CW_NAMESPACE" get "job/$CW_JOB" -o wide
kubectl --context="$CW_CONTEXT" --namespace="$CW_NAMESPACE" get pvc
kubectl --context="$CW_CONTEXT" --namespace="$CW_NAMESPACE" get pods -l "job-name=$CW_JOB" -o wide
kubectl --context="$CW_CONTEXT" --namespace="$CW_NAMESPACE" get events --field-selector="involvedObject.name=$CW_JOB" --sort-by=.metadata.creationTimestamp
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
- [Primary reference 2](https://docs.coreweave.com/products/storage/distributed-file-storage/create-volumes)
- [Primary reference 3](https://github.com/coreweave/nccl-tests)

## Evidence status

Source-reviewed guidance with offline repository checks. No live CoreWeave account, paid GPU workload or provider-backed behavioral evaluation was used to validate this guide. Record live results separately before claiming workload success.
