---
name: coreweave-local-dev-loop
description: 'Set up local development workflow for CoreWeave GPU deployments.

  Use when building containers locally, testing YAML manifests,

  or iterating on model serving configurations before deploying.

  Trigger with phrases like "coreweave dev setup", "coreweave local testing",

  "develop for coreweave", "coreweave container build".

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
# CoreWeave Local-to-staging review

> **Community-contributed.** Not affiliated with, endorsed by, or sponsored by CoreWeave, Inc. CoreWeave is a registered trademark of CoreWeave, Inc.

## Overview

Iterate on a reviewed image and manifest without borrowing production credentials.
Use Read to inspect the approved input files, Write the evidence report, and Edit only the proposed local artifact before review.
These procedures complement [CoreWeave’s official skills](https://github.com/coreweave/skills); they do not redistribute or replace that upstream distribution.

## Prerequisites

- The owner-approved organization, cluster context, namespace and resource names.
- A trusted kubeconfig from the approved secret location; no raw credentials in source, logs or terminal history.
- Installed kubectl compatible with the cluster, and authority for each proposed read or change.
- An agreed success criterion, resource budget, evidence destination and recovery owner.

## Instructions

1. Use fixtures and local unit tests before contacting CKS. Keep model tokens, kubeconfigs and datasets outside the build context and include a reviewed .dockerignore.

2. Build the owner-selected Dockerfile with locked dependencies. Scan the resulting image and record its registry digest; do not deploy a moving latest tag.

3. Render the selected staging overlay locally. Inspect namespace, image digest, secret references, resource bounds, volume mounts, service exposure and actual Node Pool labels.

4. Use server dry-run and diff with the staging context. Treat diff exit 1 as changes to review; exit greater than 1 is an error. Do not pipe unreviewed remote templates into apply.

5. After approval, apply the exact reviewed file, observe the rollout and save aggregate results. Restore the prior manifest if the staging acceptance check fails.

## Examples

Set `CW_CONTEXT` and `CW_NAMESPACE` from the approved access request. Set each referenced resource variable to the exact owner-selected resource, not a wildcard or the first matching Pod.

```bash
: "${CW_CONTEXT:?approved context required}" "${CW_NAMESPACE:?approved namespace required}"
kubectl --context="$CW_CONTEXT" --namespace="$CW_NAMESPACE" apply --dry-run=server -f reviewed-deployment.yaml
kubectl --context="$CW_CONTEXT" --namespace="$CW_NAMESPACE" diff -f reviewed-deployment.yaml
# Approval follows review of the diff, image digest and capacity:
kubectl --context="$CW_CONTEXT" --namespace="$CW_NAMESPACE" apply -f reviewed-deployment.yaml
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
