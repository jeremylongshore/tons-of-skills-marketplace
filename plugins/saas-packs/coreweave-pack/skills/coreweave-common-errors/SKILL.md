---
name: coreweave-common-errors
description: 'Diagnose and fix CoreWeave GPU scheduling, pod, and networking errors.

  Use when pods are stuck Pending, GPUs are not allocated,

  or experiencing CUDA and NCCL errors.

  Trigger with phrases like "coreweave error", "coreweave pod pending",

  "coreweave gpu not found", "coreweave debug", "fix coreweave".

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
# CoreWeave Evidence-first workload triage

> **Community-contributed.** Not affiliated with, endorsed by, or sponsored by CoreWeave, Inc. CoreWeave is a registered trademark of CoreWeave, Inc.

## Overview

Classify scheduling, container, GPU-memory, storage and connectivity failures.
Use Read to inspect the approved input files, Write the evidence report, and Edit only the proposed local artifact before review.
These procedures complement [CoreWeave’s official skills](https://github.com/coreweave/skills); they do not redistribute or replace that upstream distribution.

## Prerequisites

- The owner-approved organization, cluster context, namespace and resource names.
- A trusted kubeconfig from the approved secret location; no raw credentials in source, logs or terminal history.
- Installed kubectl compatible with the cluster, and authority for each proposed read or change.
- An agreed success criterion, resource budget, evidence destination and recovery owner.

## Instructions

1. Identify one affected workload, Pod, container and time range. Read current Pod status and namespace events before suggesting a change.

2. For Pending, distinguish resource quota, insufficient allocatable resources, affinity/taints, PVC binding and unavailable capacity. Use node.kubernetes.io/instance-type only after observing the actual instance ID.

3. Distinguish container OOMKilled from a CUDA allocation error, then correlate host-memory limits, model KV cache, batch shape and GPU memory. Increasing GPU size is not a general host-memory fix.

4. For image pull/authentication errors, check image reference and credential scope without printing Secrets. For PVC errors, inspect binding, StorageClass, access mode, namespace and CSI/file permissions.

5. For NCCL or Xid events, use the dedicated offline fabric/forensics tools. Recommend one bounded change only after the cause is corroborated; escalate managed node failures instead of reinstalling GPU operators.

## Examples

Set `CW_CONTEXT` and `CW_NAMESPACE` from the approved access request. Set each referenced resource variable to the exact owner-selected resource, not a wildcard or the first matching Pod.

```bash
: "${CW_CONTEXT:?approved context required}" "${CW_NAMESPACE:?approved namespace required}"
kubectl --context="$CW_CONTEXT" --namespace="$CW_NAMESPACE" get "pod/$CW_POD" -o wide
kubectl --context="$CW_CONTEXT" --namespace="$CW_NAMESPACE" get events --field-selector="involvedObject.name=$CW_POD" --sort-by=.metadata.creationTimestamp
kubectl --context="$CW_CONTEXT" --namespace="$CW_NAMESPACE" get resourcequota,pvc
# Optional cluster inventory requires separately approved read access:
kubectl --context="$CW_CONTEXT" get storageclass
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
- [Primary reference 3](https://docs.coreweave.com/observability/mission-control-mcp/reference/tools)

## Evidence status

Source-reviewed guidance with offline repository checks. No live CoreWeave account, paid GPU workload or provider-backed behavioral evaluation was used to validate this guide. Record live results separately before claiming workload success.
