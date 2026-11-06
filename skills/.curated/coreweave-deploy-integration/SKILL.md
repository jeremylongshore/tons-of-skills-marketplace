---
name: coreweave-deploy-integration
description: 'Deploy inference services on CoreWeave with Helm charts and Kustomize.

  Use when deploying multi-model inference, managing GPU deployments at scale,

  or templating CoreWeave manifests.

  Trigger with phrases like "deploy coreweave", "coreweave helm",

  "coreweave kustomize", "coreweave deployment patterns".

  '
allowed-tools: Read, Write, Edit, Bash(kubectl:*), Bash(python3:*), Grep
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
# CoreWeave Manifest promotion review

> **Community-contributed.** Not affiliated with, endorsed by, or sponsored by CoreWeave, Inc. CoreWeave is a registered trademark of CoreWeave, Inc.

## Overview

Promote a reviewed Helm/Kustomize deployment while preserving its rollback artifacts.
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

1. Render a locally reviewed chart or overlay from a pinned source. Check namespace, image digest, GPU limits, secret references, volume mounts, health probes and any cluster-scoped objects.

2. Choose one deployment owner and manager. Do not mix Helm release changes with ad-hoc kubectl patches without a reconciliation plan; avoid hook Jobs that run unreviewed code during deployment.

3. Confirm capacity and rollout strategy, including whether surge replicas need more GPUs than available. Use server dry-run and review the diff before apply.

4. After approval, deploy the exact rendered staging manifest and observe readiness and aggregate workload acceptance. A live DNS endpoint from a local shell may require the approved network route; do not invent a public CoreWeave hostname.

5. Retain the previous manifest/chart values and image digest. Use the manager-specific rollback, then verify application state separately from Pod readiness.

## Examples

Set `CW_CONTEXT` and `CW_NAMESPACE` from the approved access request. Set each referenced resource variable to the exact owner-selected resource, not a wildcard or the first matching Pod.

```bash
: "${CW_CONTEXT:?approved context required}" "${CW_NAMESPACE:?approved namespace required}"
kubectl --context="$CW_CONTEXT" --namespace="$CW_NAMESPACE" apply --dry-run=server -f rendered-reviewed.yaml
kubectl --context="$CW_CONTEXT" --namespace="$CW_NAMESPACE" diff -f rendered-reviewed.yaml
# After approval of the rendered staging change:
kubectl --context="$CW_CONTEXT" --namespace="$CW_NAMESPACE" apply -f rendered-reviewed.yaml
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
- [Primary reference 2](https://kubernetes.io/docs/reference/kubectl/)

## Evidence status

Source-reviewed guidance with offline repository checks. No live CoreWeave account, paid GPU workload or provider-backed behavioral evaluation was used to validate this guide. Record live results separately before claiming workload success.
