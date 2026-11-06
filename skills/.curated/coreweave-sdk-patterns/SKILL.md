---
name: coreweave-sdk-patterns
description: 'Bounded integration patterns for CoreWeave GPU workload management with
  kubectl and Python.

  Use when building inference clients, managing GPU deployments programmatically,

  or creating reusable CoreWeave deployment templates.

  Trigger with phrases like "coreweave patterns", "coreweave client",

  "coreweave Python", "coreweave deployment template".

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
# CoreWeave Client boundary design

> **Community-contributed.** Not affiliated with, endorsed by, or sponsored by CoreWeave, Inc. CoreWeave is a registered trademark of CoreWeave, Inc.

## Overview

Choose the documented CoreWeave or Kubernetes interface and design a bounded adapter.
Use Read to inspect the approved input files, Write the evidence report, and Edit only the proposed local artifact before review.
These procedures complement [CoreWeave’s official skills](https://github.com/coreweave/skills); they do not redistribute or replace that upstream distribution.

## Prerequisites

- The owner-approved organization, cluster context, namespace and resource names.
- A trusted kubeconfig from the approved secret location; no raw credentials in source, logs or terminal history.
- Installed kubectl compatible with the cluster, and authority for each proposed read or change.
- An agreed success criterion, resource budget, evidence destination and recovery owner.

## Instructions

1. Distinguish CKS Kubernetes APIs, Dedicated Inference, Serverless Inference, storage APIs and Mission Control MCP. Their endpoints, authentication and response schemas are different.

2. For CKS, use an explicit kubeconfig context and namespace. Pin the Kubernetes client version and follow its matching generated method signatures; examples from older clients using positional arguments may be incompatible.

3. For inference, obtain the endpoint and supported model identifier from the owner-approved deployment. Confirm the API reference, TLS origin and credential audience before passing any token. Do not guess /v1/namespaces or invent a CoreWeave SDK.

4. Set connect/read deadlines and bounded retries only for idempotent requests. Give write operations an explicit approval and deduplication strategy; do not automatically retry an uncertain create.

5. Test timeout, 401/403, 429, empty, malformed and partial responses with fixtures. Return an unavailable or unknown result rather than a healthy boolean on incomplete evidence.

## Examples

Set `CW_CONTEXT` and `CW_NAMESPACE` from the approved access request. Set each referenced resource variable to the exact owner-selected resource, not a wildcard or the first matching Pod.

```bash
: "${CW_CONTEXT:?approved context required}" "${CW_NAMESPACE:?approved namespace required}"
kubectl --context="$CW_CONTEXT" --namespace="$CW_NAMESPACE" api-resources
kubectl --context="$CW_CONTEXT" --namespace="$CW_NAMESPACE" auth can-i get deployments.apps
kubectl --context="$CW_CONTEXT" --namespace="$CW_NAMESPACE" get "deployment/$CW_DEPLOYMENT" --request-timeout=20s
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
- [Primary reference 1](https://docs.coreweave.com/observability/mission-control-mcp/reference/tools)
- [Primary reference 2](https://docs.coreweave.com/products/inference/reference/api-overview)
- [Primary reference 3](https://github.com/kubernetes-client/python)

## Evidence status

Source-reviewed guidance with offline repository checks. No live CoreWeave account, paid GPU workload or provider-backed behavioral evaluation was used to validate this guide. Record live results separately before claiming workload success.
