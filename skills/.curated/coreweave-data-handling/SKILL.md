---
name: coreweave-data-handling
description: 'Handle training data and model artifacts on CoreWeave persistent storage.

  Use when managing large datasets, configuring storage classes,

  or implementing data pipelines for GPU workloads.

  Trigger with phrases like "coreweave data", "coreweave storage",

  "coreweave pvc", "coreweave dataset management".

  '
allowed-tools: Read, Write, Edit, Bash(kubectl:*), Grep
version: 1.14.0
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
# CoreWeave Artifact integrity and storage review

> **Community-contributed.** Not affiliated with, endorsed by, or sponsored by CoreWeave, Inc. CoreWeave is a registered trademark of CoreWeave, Inc.

## Overview

Validate model, dataset and checkpoint provenance, storage permissions and recovery.
Use Read to inspect the approved input files, Write the evidence report, and Edit only the proposed local artifact before review.
These procedures complement [CoreWeave’s official skills](https://github.com/coreweave/skills); they do not redistribute or replace that upstream distribution.

## Prerequisites

- The owner-approved organization, cluster context, namespace and resource names.
- A trusted kubeconfig from the approved secret location; no raw credentials in source, logs or terminal history.
- Installed kubectl compatible with the cluster, and authority for each proposed read or change.
- An agreed success criterion, resource budget, evidence destination and recovery owner.

## Instructions

1. Record artifact source, license, trusted digest, size, classification, approved region, retention and destination. A bucket name substring is not proof of its actual region or ownership.

2. Use current DFS guidance and inspect the available StorageClass and PVC access modes. Confirm encryption and backup guarantees with the actual platform configuration; do not infer AES-256 or a 30-day retention policy from a YAML example.

3. Use an approved transfer tool and allowlisted destination with bounded retries. Pass URLs as data, not interpolated shell or Python code; do not automatically follow credential-bearing redirects to another origin.

4. Stream and compare the digest to a separately trusted expected value before promotion. Printing a newly calculated digest without comparing it is not integrity validation. Quarantine incomplete or mismatched artifacts.

5. Validate checkpoint completeness and restore compatibility in staging. Preserve the last complete copy and require explicit approval for deletion, export or new billable storage.

## Examples

Set `CW_CONTEXT` and `CW_NAMESPACE` from the approved access request. Set each referenced resource variable to the exact owner-selected resource, not a wildcard or the first matching Pod.

```bash
: "${CW_CONTEXT:?approved context required}" "${CW_NAMESPACE:?approved namespace required}"
kubectl --context="$CW_CONTEXT" --namespace="$CW_NAMESPACE" get pvc
kubectl --context="$CW_CONTEXT" --namespace="$CW_NAMESPACE" get "pod/$CW_POD" \
  -o 'jsonpath={.spec.volumes[*].persistentVolumeClaim.claimName}{"\n"}'
# Optional cluster-level read access:
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
- [Primary reference 1](https://docs.coreweave.com/products/storage/distributed-file-storage/create-volumes)
- [Primary reference 2](https://kubernetes.io/docs/concepts/storage/persistent-volumes/)
- [Primary reference 3](https://docs.coreweave.com/products/cks/auth-access/managed-auth/kubeconfig)

## Evidence status

Source-reviewed guidance with offline repository checks. No live CoreWeave account, paid GPU workload or provider-backed behavioral evaluation was used to validate this guide. Record live results separately before claiming workload success.
