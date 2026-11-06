---
name: coreweave-install-auth
description: 'Configure CoreWeave Kubernetes Service (CKS) access with kubeconfig
  and API tokens.

  Use when setting up kubectl access to CoreWeave, configuring CKS clusters,

  or authenticating with CoreWeave cloud services.

  Trigger with phrases like "install coreweave", "setup coreweave",

  "coreweave kubeconfig", "coreweave auth", "connect to coreweave".

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
# CoreWeave Access and identity verification

> **Community-contributed.** Not affiliated with, endorsed by, or sponsored by CoreWeave, Inc. CoreWeave is a registered trademark of CoreWeave, Inc.

## Overview

Verify an approved CKS kubeconfig and namespace before any workload operation.
Use Read to inspect the approved input files, Write the evidence report, and Edit only the proposed local artifact before review.
These procedures complement [CoreWeave’s official skills](https://github.com/coreweave/skills); they do not redistribute or replace that upstream distribution.

## Prerequisites

- The owner-approved organization, cluster context, namespace and resource names.
- A trusted kubeconfig from the approved secret location; no raw credentials in source, logs or terminal history.
- Installed kubectl compatible with the cluster, and authority for each proposed read or change.
- An agreed success criterion, resource budget, evidence destination and recovery owner.

## Instructions

1. Obtain the cluster-specific kubeconfig through the Cloud Console and current Managed Auth instructions. Treat the entire file as a secret; it embeds a token. Store it in the approved private credential location, not .env, Git or a support bundle.

2. Read the intended organization, cluster, context, namespace and token expiry from the access request. Review any exec-based credential plugin in an externally supplied kubeconfig before using it.

3. Check namespace read permission and record the result. A successful client-version command does not prove server connectivity. Distinguish authentication failure from Kubernetes authorization denial.

4. If access to Nodes is approved, inspect current instance-type labels and allocatable GPUs. A denied Node listing does not mean the organization has no GPUs.

5. For Mission Control MCP, use the official configuration guide and discover read-only tools. Do not infer that an API token and a Kubernetes service-account token are interchangeable.

## Examples

Set `CW_CONTEXT` and `CW_NAMESPACE` from the approved access request. Set each referenced resource variable to the exact owner-selected resource, not a wildcard or the first matching Pod.

```bash
: "${CW_CONTEXT:?approved context required}" "${CW_NAMESPACE:?approved namespace required}"
kubectl --context="$CW_CONTEXT" --namespace="$CW_NAMESPACE" auth can-i get pods
kubectl --context="$CW_CONTEXT" --namespace="$CW_NAMESPACE" get pods --request-timeout=20s
# Only with approved cluster-level read access:
kubectl --context="$CW_CONTEXT" get nodes -L node.kubernetes.io/instance-type --request-timeout=20s
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
- [Primary reference 2](https://docs.coreweave.com/observability/mission-control-mcp/reference/tools)

## Evidence status

Source-reviewed guidance with offline repository checks. No live CoreWeave account, paid GPU workload or provider-backed behavioral evaluation was used to validate this guide. Record live results separately before claiming workload success.
