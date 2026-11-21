---
name: coreweave-debug-bundle
description: 'Collect CoreWeave cluster diagnostics for support tickets.

  Use when preparing a support case, collecting GPU node status,

  or documenting pod failures.

  Trigger with phrases like "coreweave debug", "coreweave support",

  "coreweave diagnostics", "collect coreweave logs".

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
# CoreWeave Scoped support evidence

> **Community-contributed.** Not affiliated with, endorsed by, or sponsored by CoreWeave, Inc. CoreWeave is a registered trademark of CoreWeave, Inc.

## Overview

Collect minimal operational status without inventing API probes or exporting raw secrets.
Use Read to inspect the approved input files, Write the evidence report, and Edit only the proposed local artifact before review.
These procedures complement [CoreWeave’s official skills](https://github.com/coreweave/skills); they do not redistribute or replace that upstream distribution.

## Prerequisites

- The owner-approved organization, cluster context, namespace and resource names.
- A trusted kubeconfig from the approved secret location; no raw credentials in source, logs or terminal history.
- Installed kubectl compatible with the cluster, and authority for each proposed read or change.
- An agreed success criterion, resource budget, evidence destination and recovery owner.

## Instructions

1. Agree the incident, namespace, workload, time range, retention destination and allowed fields. Create a private local workspace; never archive the project directory or kubeconfig.

2. Prefer allowlisted status fields from the affected Pod and deployment. Do not collect all namespaces, raw Pod YAML, Secret objects, environment variables or request/response bodies by default.

3. Collect bounded namespace events after reviewing their sensitivity. Raw application logs require separate approval and human redaction because neither regexes nor this guide can guarantee removal of secrets or customer data.

4. Where authorized, use Mission Control MCP read-only cluster, metric and log tools with an explicit time range and pagination. Review tool output before sharing; the tool catalog also contains write actions, which this collection must not invoke.

5. Assemble only reviewed files, inspect the manifest, and use the approved support channel. Keep the local copy until upload is verified, then apply the owner-approved retention rule. Record collection failures rather than silently treating them as clean results.

## Examples

Set `CW_CONTEXT` and `CW_NAMESPACE` from the approved access request. Set each referenced resource variable to the exact owner-selected resource, not a wildcard or the first matching Pod.

```bash
: "${CW_CONTEXT:?approved context required}" "${CW_NAMESPACE:?approved namespace required}"
# Redirect only allowlisted fields into the approved private workspace.
kubectl --context="$CW_CONTEXT" --namespace="$CW_NAMESPACE" get "pod/$CW_POD" \
  -o 'jsonpath={.metadata.name}{"\n"}{.spec.nodeName}{"\n"}{.status.phase}{"\n"}'
kubectl --context="$CW_CONTEXT" --namespace="$CW_NAMESPACE" get "deployment/$CW_DEPLOYMENT" \
  -o 'jsonpath={.status.replicas}{"\n"}{.status.readyReplicas}{"\n"}'
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
- [Primary reference 2](https://docs.coreweave.com/platform/fleet-management/node-lifecycle/state-transitions)
- [Primary reference 3](https://status.coreweave.com)

## Evidence status

Source-reviewed guidance with offline repository checks. No live CoreWeave account, paid GPU workload or provider-backed behavioral evaluation was used to validate this guide. Record live results separately before claiming workload success.
