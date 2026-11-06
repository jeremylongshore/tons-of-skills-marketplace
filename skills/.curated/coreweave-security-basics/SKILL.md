---
name: coreweave-security-basics
description: 'Secure CoreWeave deployments with RBAC, network policies, and secrets
  management.

  Use when hardening GPU workloads, managing model access,

  or configuring namespace isolation.

  Trigger with phrases like "coreweave security", "coreweave rbac",

  "secure coreweave", "coreweave secrets".

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
# CoreWeave Workload security review

> **Community-contributed.** Not affiliated with, endorsed by, or sponsored by CoreWeave, Inc. CoreWeave is a registered trademark of CoreWeave, Inc.

## Overview

Review CKS identity, credential, network and data boundaries before release.
Use Read to inspect the approved input files, Write the evidence report, and Edit only the proposed local artifact before review.
These procedures complement [CoreWeave’s official skills](https://github.com/coreweave/skills); they do not redistribute or replace that upstream distribution.

## Prerequisites

- The owner-approved organization, cluster context, namespace and resource names.
- A trusted kubeconfig from the approved secret location; no raw credentials in source, logs or terminal history.
- Installed kubectl compatible with the cluster, and authority for each proposed read or change.
- An agreed success criterion, resource budget, evidence destination and recovery owner.

## Instructions

1. Map the kubeconfig, platform token, registry credential and model token to their actual audiences and principals. Use least privilege and managed secret injection; a Kubernetes Secret is not proof of encryption or limited exposure.

2. Review RBAC, service-account token mounting, allowed workload images/digests, container security contexts and namespace access. Anyone allowed to create Pods may be able to mount same-namespace Secrets/PVCs; a PVC Role alone is not a mount isolation boundary.

3. Review NetworkPolicy with the installed enforcement backend. Namespace separation alone does not isolate traffic, and a policy object alone does not prove enforcement; test allowed and denied paths in staging.

4. Validate externally supplied URLs, image references and artifact checksums. Do not insert them into shell commands or generated Python/TypeScript source. Avoid unsafe deserialization of untrusted model files.

5. Use a documented service-specific authentication/signature protocol. Do not invent x-coreweave-signature or an HMAC scheme; current Alerts integrations must follow their actual contract.

## Examples

Set `CW_CONTEXT` and `CW_NAMESPACE` from the approved access request. Set each referenced resource variable to the exact owner-selected resource, not a wildcard or the first matching Pod.

```bash
: "${CW_CONTEXT:?approved context required}" "${CW_NAMESPACE:?approved namespace required}"
kubectl --context="$CW_CONTEXT" --namespace="$CW_NAMESPACE" auth can-i create pods
kubectl --context="$CW_CONTEXT" --namespace="$CW_NAMESPACE" get serviceaccount,rolebinding,networkpolicy
kubectl --context="$CW_CONTEXT" --namespace="$CW_NAMESPACE" get "deployment/$CW_DEPLOYMENT" \
  -o 'jsonpath={.spec.template.spec.serviceAccountName}{"\n"}{.spec.template.spec.automountServiceAccountToken}{"\n"}'
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
- [Primary reference 2](https://kubernetes.io/docs/concepts/security/secrets-good-practices/)
- [Primary reference 3](https://kubernetes.io/docs/concepts/services-networking/network-policies/)

## Evidence status

Source-reviewed guidance with offline repository checks. No live CoreWeave account, paid GPU workload or provider-backed behavioral evaluation was used to validate this guide. Record live results separately before claiming workload success.
