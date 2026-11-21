---
name: coreweave-upgrade-migration
description: 'Upgrade CoreWeave deployments and migrate between GPU types.

  Use when migrating from A100 to H100, upgrading CUDA versions,

  or updating inference server versions.

  Trigger with phrases like "upgrade coreweave", "coreweave gpu migration",

  "coreweave cuda upgrade", "migrate coreweave".

  '
allowed-tools: Read, Write, Edit, Bash(kubectl:*), Bash(python3:*), Grep
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
# CoreWeave Migration and rollback planning

> **Community-contributed.** Not affiliated with, endorsed by, or sponsored by CoreWeave, Inc. CoreWeave is a registered trademark of CoreWeave, Inc.

## Overview

Review GPU, image, storage and deployment changes with a real recovery path.
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

1. Inventory the actual instance IDs, driver/runtime compatibility, workload manifests, replicas, PVCs and application state. Do not infer that a GPU SKU is deprecated from a hardcoded list.

2. Choose a target supported by current platform and image documentation. Benchmark representative workload quality, memory, throughput and latency; an A100-to-H100 move is not a Kubernetes schema migration.

3. Validate a reviewed staging manifest and observe a bounded canary. Keep the prior immutable image and deployment revision available. Do not overwrite the only checkpoint or detach/delete a production PVC as a shortcut.

4. Review rollout history and choose an explicit previous revision. A rollout restart changes the Pod template timestamp; it does not restore a prior image or configuration.

5. After rollback approval, use rollout undo with the selected revision and wait for readiness. Recover external data/configuration separately according to their own reviewed procedures.

## Examples

Set `CW_CONTEXT` and `CW_NAMESPACE` from the approved access request. Set each referenced resource variable to the exact owner-selected resource, not a wildcard or the first matching Pod.

```bash
: "${CW_CONTEXT:?approved context required}" "${CW_NAMESPACE:?approved namespace required}"
kubectl --context="$CW_CONTEXT" --namespace="$CW_NAMESPACE" rollout history "deployment/$CW_DEPLOYMENT"
kubectl --context="$CW_CONTEXT" --namespace="$CW_NAMESPACE" apply --dry-run=server -f migration-reviewed.yaml
# Recovery only after the owner approves the selected revision:
kubectl --context="$CW_CONTEXT" --namespace="$CW_NAMESPACE" rollout undo "deployment/$CW_DEPLOYMENT" --to-revision="$CW_PREVIOUS_REVISION"
kubectl --context="$CW_CONTEXT" --namespace="$CW_NAMESPACE" rollout status "deployment/$CW_DEPLOYMENT" --timeout=10m
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
- [Primary reference 2](https://docs.coreweave.com/platform/fleet-management/node-lifecycle/state-transitions)
- [Primary reference 3](https://kubernetes.io/docs/reference/kubectl/)

## Evidence status

Source-reviewed guidance with offline repository checks. No live CoreWeave account, paid GPU workload or provider-backed behavioral evaluation was used to validate this guide. Record live results separately before claiming workload success.
