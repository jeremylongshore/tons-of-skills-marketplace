---
name: coreweave-incident-runbook
description: 'Incident response runbook for CoreWeave GPU workload failures.

  Use when inference services are down, GPUs are unavailable,

  or responding to production incidents on CoreWeave.

  Trigger with phrases like "coreweave incident", "coreweave outage",

  "coreweave runbook", "coreweave service down".

  '
allowed-tools: Read, Bash(kubectl:*), Grep
version: 1.12.0
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
# CoreWeave Incident Runbook

> **Community-contributed.** Not affiliated with, endorsed by, or sponsored by CoreWeave, Inc. CoreWeave is a registered trademark of CoreWeave, Inc.

## Overview

Respond to GPU workload incidents by stabilizing customer impact, preserving
redacted evidence, and restoring a known-good state. The incident commander owns
communications and escalation; responders use only the access required for triage.

## Prerequisites

- An incident ID, named commander, affected namespace/service, and on-call route.
- Authorized read-only cluster access plus a documented production rollback revision.
- A redaction policy for logs, prompts, model artifacts, and credentials.

## Instructions

1. Declare severity and scope, then capture pod, event, node, and service status.
2. Stabilize impact with the documented scale, failover, or rollback action before root-cause work.
3. Collect only redacted, bounded diagnostics and escalate hardware or capacity issues through CoreWeave support.
4. Verify recovery against the service SLO, update stakeholders, and create follow-up work for root cause and prevention.

## Triage Steps

```bash
# 1. Check pod status
kubectl get pods -l app=inference -o wide

# 2. Check recent events
kubectl get events --sort-by=.lastTimestamp | tail -20

# 3. Check node status
kubectl get nodes -l gpu.nvidia.com/class -o wide

# 4. Check GPU health
kubectl exec -it $(kubectl get pod -l app=inference -o name | head -1) -- nvidia-smi
```

## Common Incidents

### Inference Service Down

1. Check pod status and events
2. If OOMKilled: reduce batch size or upgrade GPU
3. If ImagePullBackOff: check registry credentials
4. If Pending: check GPU quota and availability

### GPU Node Failure

1. Pods will be rescheduled automatically
2. If no capacity: scale down non-critical workloads
3. Contact CoreWeave support for extended outages

### Model Loading Failure

1. Check HuggingFace token secret exists
2. Verify model name spelling
3. Check PVC has sufficient storage
4. Review container logs for download errors

## Rollback

```bash
kubectl rollout undo deployment/inference
```

## Output

- A time-stamped incident record with scope, owner, stabilization action, and redacted evidence.
- A verified recovery or an explicit escalation with a safe customer-impact mitigation.

## Error Handling

| Incident complication | Required response |
|---|---|
| Rollback fails | Stop repeated deploy attempts, escalate to the platform owner, and preserve events. |
| Diagnostics include a secret | Restrict distribution, rotate the secret, and recollect redacted evidence. |
| No GPU capacity is available | Prioritize critical services under approved policy; do not remove tenant quotas. |
| Recovery cannot meet SLO | Declare the continuing impact and use the approved fallback or communication path. |

## Examples

For a failing production rollout, stabilize first and capture only the relevant evidence:

```bash
kubectl -n inference-prod rollout undo deployment/inference
kubectl -n inference-prod rollout status deployment/inference --timeout=10m
kubectl -n inference-prod get events --sort-by=.lastTimestamp | tail -30
```

Record the revision, outcome, and redacted events in the incident. Do not retry a broken image or expose a troubleshooting endpoint publicly.

## Resources

- CoreWeave Support
- [CoreWeave Status](https://status.coreweave.com)

## Next Steps

For data handling, see `coreweave-data-handling`.
