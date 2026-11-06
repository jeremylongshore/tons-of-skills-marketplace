---
name: coreweave-observability
description: 'Set up GPU monitoring and observability for CoreWeave workloads.

  Use when implementing GPU metrics dashboards, configuring alerts,

  or tracking inference latency and throughput.

  Trigger with phrases like "coreweave monitoring", "coreweave observability",

  "coreweave gpu metrics", "coreweave grafana".

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
# CoreWeave Signal and alert validation

> **Community-contributed.** Not affiliated with, endorsed by, or sponsored by CoreWeave, Inc. CoreWeave is a registered trademark of CoreWeave, Inc.

## Overview

Correlate GPU, workload, storage and latency signals without claiming universal thresholds.
Use Read to inspect the approved input files, Write the evidence report, and Edit only the proposed local artifact before review.
These procedures complement [CoreWeave’s official skills](https://github.com/coreweave/skills); they do not redistribute or replace that upstream distribution.

## Prerequisites

- The owner-approved organization, cluster context, namespace and resource names.
- A trusted kubeconfig from the approved secret location; no raw credentials in source, logs or terminal history.
- Installed kubectl compatible with the cluster, and authority for each proposed read or change.
- An agreed success criterion, resource budget, evidence destination and recovery owner.

## Instructions

1. Use the official Mission Control MCP read-only tool catalog or approved Grafana access. Discover datasources, metric metadata and labels before querying; do not assume a metric or reservation label exists.

2. Bind queries to the cluster, namespace, time range and step. Record coverage and freshness. Distinguish no samples, an empty result, denied access and a valid measured zero.

3. Build workload-specific dashboards for utilization, memory, queue delay, tail latency, successful work and failures. Correlate checkpoint/storage phases; a global average can hide one stalled GPU or rank.

4. Choose alert thresholds and routes with the service owner from measured baselines. Test one synthetic/non-sensitive incident in staging and verify delivery and restoration; do not scale production to zero to test an alert.

5. For Xid or transport failures, pass the relevant sanitized evidence to the dedicated offline tool. Preserve the observation and confidence separately from a proposed operational action.

## Examples

Set `CW_CONTEXT` and `CW_NAMESPACE` from the approved access request. Set each referenced resource variable to the exact owner-selected resource, not a wildcard or the first matching Pod.

```bash
: "${CW_CONTEXT:?approved context required}" "${CW_NAMESPACE:?approved namespace required}"
kubectl --context="$CW_CONTEXT" --namespace="$CW_NAMESPACE" get "deployment/$CW_DEPLOYMENT" -o wide
kubectl --context="$CW_CONTEXT" --namespace="$CW_NAMESPACE" get pods
kubectl --context="$CW_CONTEXT" --namespace="$CW_NAMESPACE" get events --sort-by=.metadata.creationTimestamp
kubectl --context="$CW_CONTEXT" --namespace="$CW_NAMESPACE" get hpa
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
- [Primary reference 2](https://docs.coreweave.com/observability/usage-monitoring)
- [Primary reference 3](https://docs.coreweave.com/platform/fleet-management/node-lifecycle/state-transitions)

## Evidence status

Source-reviewed guidance with offline repository checks. No live CoreWeave account, paid GPU workload or provider-backed behavioral evaluation was used to validate this guide. Record live results separately before claiming workload success.
