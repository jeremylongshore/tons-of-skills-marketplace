---
name: coreweave-multi-env-setup
description: 'Configure CoreWeave across development, staging, and production environments.

  Use when setting up multi-environment GPU infrastructure, separating namespaces,

  or managing per-environment GPU quotas.

  Trigger with phrases like "coreweave environments", "coreweave staging",

  "coreweave multi-env", "coreweave namespace setup".

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
# CoreWeave Environment promotion boundaries

> **Community-contributed.** Not affiliated with, endorsed by, or sponsored by CoreWeave, Inc. CoreWeave is a registered trademark of CoreWeave, Inc.

## Overview

Keep identities, manifests, budgets and data separate across development, staging and production.
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

1. List each environment’s approved context, namespace, identity, data classification, secret source, registry and capacity budget. A namespace is an organizational boundary, not proof of full tenant isolation.

2. Use context/namespace explicitly for every command. Select credentials for one environment at a time; do not load every production token into a shared configuration object.

3. Render overlays from the same pinned base. Review every namespace, image digest, volume, secret reference, exposure and resource difference. Do not guess regional API hostnames or encode live tokens in .env files.

4. Test staging with representative runtime/topology where the experiment needs comparability. Choose replica and interruption policies from the SLO and capacity contract, not a universal dev/staging/prod GPU matrix.

5. Promote the exact reviewed artifact with owner approval, then verify readiness and acceptance. Moving a manifest between namespaces does not automatically move traffic or implement blue/green deployment.

## Examples

Set `CW_CONTEXT` and `CW_NAMESPACE` from the approved access request. Set each referenced resource variable to the exact owner-selected resource, not a wildcard or the first matching Pod.

```bash
: "${CW_CONTEXT:?approved context required}" "${CW_NAMESPACE:?approved namespace required}"
kubectl --context="$CW_CONTEXT" --namespace="$CW_NAMESPACE" auth can-i get deployments.apps
kubectl --context="$CW_CONTEXT" --namespace="$CW_NAMESPACE" apply --dry-run=server -f environment-reviewed.yaml
kubectl --context="$CW_CONTEXT" --namespace="$CW_NAMESPACE" diff -f environment-reviewed.yaml
kubectl --context="$CW_CONTEXT" --namespace="$CW_NAMESPACE" get resourcequota,networkpolicy
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
- [Primary reference 1](https://docs.coreweave.com/products/cks/auth-access/managed-auth/kubeconfig)
- [Primary reference 2](https://docs.coreweave.com/products/cks/clusters/scheduling/workload-scheduling)
- [Primary reference 3](https://docs.coreweave.com/platform/capacity-plans)

## Evidence status

Source-reviewed guidance with offline repository checks. No live CoreWeave account, paid GPU workload or provider-backed behavioral evaluation was used to validate this guide. Record live results separately before claiming workload success.
