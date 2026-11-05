---
name: coreweave-common-errors
description: 'Diagnose and fix CoreWeave GPU scheduling, pod, and networking errors.

  Use when pods are stuck Pending, GPUs are not allocated,

  or experiencing CUDA and NCCL errors.

  Trigger with phrases like "coreweave error", "coreweave pod pending",

  "coreweave gpu not found", "coreweave debug", "fix coreweave".

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
# CoreWeave Common Errors

## Overview

Use this triage guide to classify common GPU, Kubernetes, storage, and connectivity
failures before changing capacity or credentials. Capture the smallest redacted
evidence set and use a reversible fix in the affected namespace.

## Prerequisites

- Read-only access to the affected namespace, pod events, quota, and node labels.
- The workload name, expected GPU class, and a named service or platform owner.

## Instructions

1. Identify the pod, Job, or Service and collect its status plus recent events.
2. Match the symptom to the table below, then validate the proposed cause with the
   listed read-only command before applying a fix.
3. Make the smallest namespace-scoped change, verify recovery, and record the
   redacted event/command outcome in the incident or change record.

> **Community-contributed.** Not affiliated with, endorsed by, or sponsored by CoreWeave, Inc. CoreWeave is a registered trademark of CoreWeave, Inc.

## Error Reference

### 1. Pod Stuck Pending -- No GPU Available

```text
kubectl describe pod <pod-name> | grep -A5 Events
# "0/N nodes are available: insufficient nvidia.com/gpu"
```

**Fix**: Check GPU availability: `kubectl get nodes -l gpu.nvidia.com/class=A100_PCIE_80GB`. Try a different GPU type or region.

### 2. CUDA Out of Memory

```
torch.cuda.OutOfMemoryError: CUDA out of memory
```

**Fix**: Reduce batch size, enable gradient checkpointing, or use a larger GPU (A100-80GB instead of 40GB).

### 3. Image Pull BackOff

**Fix**: Create an imagePullSecret:

```bash
kubectl create secret docker-registry regcred \
  --docker-server=ghcr.io \
  --docker-username=$GH_USER \
  --docker-password=$GH_TOKEN
```

### 4. NCCL Timeout (Multi-GPU)

```
NCCL error: unhandled system error
```

**Fix**: Ensure all GPUs are on the same node (NVLink). For multi-node, use InfiniBand-connected nodes.

### 5. PVC Not Mounting

**Fix**: Check storage class availability: `kubectl get sc`. Use CoreWeave storage classes like `shared-hdd-ord1` or `shared-ssd-ord1`.

### 6. Node Affinity Mismatch

**Fix**: List valid GPU class labels:

```bash
kubectl get nodes -o json | jq -r '.items[].metadata.labels["gpu.nvidia.com/class"]' | sort -u
```

### 7. Service Not Reachable

**Fix**: Check Service and Endpoints:

```text
kubectl get svc,endpoints <service-name>
```

## Output

- A classified failure with supporting redacted events and a bounded recovery action.
- A verified recovery result or a clear escalation to the platform owner.

## Error Handling

| Triage failure | Safe response |
|---|---|
| Root cause remains unclear | Stop speculative changes and collect a redacted debug bundle. |
| Quota or capacity change is required | Obtain the namespace owner approval; do not alter cluster-wide quotas. |
| Credential failure is suspected | Rotate/revoke through the approved secret manager; never print or paste the credential. |
| Data or model artifact may be corrupt | Quarantine it and verify checksum before retrying. |

## Examples

For a Pending GPU pod, collect events and quota before selecting another GPU class:

```bash
kubectl -n research describe pod trainer-0
kubectl -n research describe resourcequota
kubectl get nodes -l gpu.nvidia.com/class=A100_PCIE_80GB
```

If capacity is unavailable, leave the Job unchanged and escalate with the redacted
events. Do not remove affinity or quota controls merely to force scheduling.

## Resources

- [CoreWeave Documentation](https://docs.coreweave.com)
- [GPU Instance Types](https://docs.coreweave.com/docs/platform/instances/gpu-instances)

## Next Steps

For diagnostics, see `coreweave-debug-bundle`.
