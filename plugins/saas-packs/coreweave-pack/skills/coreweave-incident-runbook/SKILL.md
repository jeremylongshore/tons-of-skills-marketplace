---
name: coreweave-incident-runbook
description: 'Incident response runbook for CoreWeave GPU workload failures.

  Use when inference services are down, GPUs are unavailable,

  or responding to production incidents on CoreWeave.

  Trigger with phrases like "coreweave incident", "coreweave outage",

  "coreweave runbook", "coreweave service down".

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
# CoreWeave Incident stabilization review

> **Community-contributed.** Not affiliated with, endorsed by, or sponsored by CoreWeave, Inc. CoreWeave is a registered trademark of CoreWeave, Inc.

## Overview

Stabilize an affected workload using evidence, an approved recovery path and clear ownership.
Use Read to inspect the approved input files, Write the evidence report, and Edit only the proposed local artifact before review.
These procedures complement [CoreWeave’s official skills](https://github.com/coreweave/skills); they do not redistribute or replace that upstream distribution.

## Prerequisites

- The owner-approved organization, cluster context, namespace and resource names.
- A trusted kubeconfig from the approved secret location; no raw credentials in source, logs or terminal history.
- Installed kubectl compatible with the cluster, and authority for each proposed read or change.
- An agreed success criterion, resource budget, evidence destination and recovery owner.

## Instructions

1. Record the incident commander, affected service, context, namespace, start time, impact and next update. Check CoreWeave status and distinguish platform impact from an application rollout failure.

2. Collect bounded operational status and events. Review Pod/container termination reasons, current replicas, quota, PVC binding and model readiness; do not execute commands in an arbitrary first matching Pod.

3. Choose an approved rollback, traffic failover or workload-priority change. Confirm the retained image and application/data compatibility. Rescheduling is not guaranteed when capacity, affinity or disruption constraints block it.

4. For hardware or fabric events, use the offline forensics tools and inspect managed lifecycle state. Do not manually uncordon health-cordoned Nodes, reinstall drivers, or reboot managed hardware without the lifecycle owner.

5. Verify recovery against service-specific success/latency/quality targets, record residual impact and preserve sanitized evidence. If recovery fails, escalate rather than retrying destructive operations.

## Examples

Set `CW_CONTEXT` and `CW_NAMESPACE` from the approved access request. Set each referenced resource variable to the exact owner-selected resource, not a wildcard or the first matching Pod.

```bash
: "${CW_CONTEXT:?approved context required}" "${CW_NAMESPACE:?approved namespace required}"
kubectl --context="$CW_CONTEXT" --namespace="$CW_NAMESPACE" get "deployment/$CW_DEPLOYMENT" -o wide
kubectl --context="$CW_CONTEXT" --namespace="$CW_NAMESPACE" get "pod/$CW_POD" -o wide
kubectl --context="$CW_CONTEXT" --namespace="$CW_NAMESPACE" get events --field-selector="involvedObject.name=$CW_POD" --sort-by=.metadata.creationTimestamp
kubectl --context="$CW_CONTEXT" --namespace="$CW_NAMESPACE" rollout history "deployment/$CW_DEPLOYMENT"
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
- [Primary reference 1](https://docs.coreweave.com/platform/fleet-management/node-lifecycle/state-transitions)
- [Primary reference 2](https://status.coreweave.com)
- [Primary reference 3](https://docs.coreweave.com/observability/mission-control-mcp/reference/tools)

## Evidence status

Source-reviewed guidance with offline repository checks. No live CoreWeave account, paid GPU workload or provider-backed behavioral evaluation was used to validate this guide. Record live results separately before claiming workload success.

## Offline verification

Supply ordered `timeline` timestamps, `affected_resources`, `incident_owner`, `state`, `escalation_route` and `recovery` with acceptance_passed, resource_scope and at. Containment claims also need an approval_reference. The helper rejects a resolution claim without matching, recent recovery evidence. An incident still being investigated returns incomplete intentionally. A passed recovery flag must refer to an actual workload acceptance record; this helper does not run recovery. Keep private support contacts and raw tenant logs outside public fixtures.

From this skill directory, replay the synthetic example (its timestamp is intentionally
fixed; it contains no account data):

```bash
python3 scripts/review-incident.py --input tests/fixtures/example.json --as-of 2026-11-05T12:01:00Z
```

For current evidence, omit `--as-of`; it defaults to current UTC. Required common
fields: `schema: coreweave-evidence/v1`, `captured_at`, `context`, `namespace`,
`expected_context`, `expected_namespace`. The scope must agree and evidence must
be at most five minutes old. Explicit replay time is for testing historical fixtures,
not a way to make stale production evidence current.

Exit 0 / `reviewed` means the supplied assertions satisfy this bounded contract;
2 / `blocked` requires correction; 3 / `incomplete` requires more evidence. Read the
findings rather than relying only on exit status. Scripts never execute text from
inputs, call a cloud API or authorize a change. Fixture and package checks are
separate from model behavior and live compatibility.

- [Input contract and limitations](references/evidence-contract.md)
- [Skill blueprint and acceptance](docs/BLUEPRINT.md)
