---
name: coreweave-prod-checklist
description: 'Production readiness checklist for CoreWeave GPU workloads.

  Use when launching inference services, preparing GPU training for production,

  or validating deployment configurations.

  Trigger with phrases like "coreweave production", "coreweave go-live",

  "coreweave checklist", "coreweave launch".

  '
allowed-tools: Read, Write, Edit, Bash(kubectl:*), Grep
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
# CoreWeave Release evidence review

> **Community-contributed.** Not affiliated with, endorsed by, or sponsored by CoreWeave, Inc. CoreWeave is a registered trademark of CoreWeave, Inc.

## Overview

Produce a go/no-go decision from actual readiness, quality, security and recovery evidence.
Use Read to inspect the approved input files, Write the evidence report, and Edit only the proposed local artifact before review.
These procedures complement [CoreWeave’s official skills](https://github.com/coreweave/skills); they do not redistribute or replace that upstream distribution.

## Prerequisites

- The owner-approved organization, cluster context, namespace and resource names.
- A trusted kubeconfig from the approved secret location; no raw credentials in source, logs or terminal history.
- Installed kubectl compatible with the cluster, and authority for each proposed read or change.
- An agreed success criterion, resource budget, evidence destination and recovery owner.

## Instructions

1. Bind the release to an approved context, namespace, image digest, model version, capacity plan, owner and change window. Review staging results for the actual workload shape.

2. Check model readiness, bounded autoscaling, CPU/host-memory/GPU budgets, storage integrity, private endpoint authentication and quota/capacity evidence. Minimum replicas alone do not eliminate cold starts or guarantee an SLO.

3. Attach proof of least-privilege identity, secret handling, effective network controls, alert delivery and data-retention decisions. Mark any untested control as unknown.

4. Inspect the retained rollback revision, image availability, external configuration and checkpoint compatibility. Kubernetes Deployment history does not restore separately changed Secrets, PVC contents or database schemas.

5. Issue a no-go for a missing critical gate. Publishing a checklist or passing syntax validation is not production certification; the owner makes the release decision from the evidence.

## Examples

Set `CW_CONTEXT` and `CW_NAMESPACE` from the approved access request. Set each referenced resource variable to the exact owner-selected resource, not a wildcard or the first matching Pod.

```bash
: "${CW_CONTEXT:?approved context required}" "${CW_NAMESPACE:?approved namespace required}"
kubectl --context="$CW_CONTEXT" --namespace="$CW_NAMESPACE" get "deployment/$CW_DEPLOYMENT" "service/$CW_SERVICE"
kubectl --context="$CW_CONTEXT" --namespace="$CW_NAMESPACE" rollout history "deployment/$CW_DEPLOYMENT"
kubectl --context="$CW_CONTEXT" --namespace="$CW_NAMESPACE" get resourcequota,pvc
kubectl --context="$CW_CONTEXT" --namespace="$CW_NAMESPACE" get events --sort-by=.metadata.creationTimestamp
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
- [Primary reference 2](https://docs.coreweave.com/platform/capacity-plans)
- [Primary reference 3](https://kubernetes.io/docs/reference/kubectl/)

## Evidence status

Source-reviewed guidance with offline repository checks. No live CoreWeave account, paid GPU workload or provider-backed behavioral evaluation was used to validate this guide. Record live results separately before claiming workload success.
