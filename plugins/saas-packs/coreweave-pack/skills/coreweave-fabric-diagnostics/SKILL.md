---
name: coreweave-fabric-diagnostics
description: |
  Diagnose CoreWeave NCCL transport and RDMA configuration from supplied logs,
  Pod resources and ibstat output. Use when multi-node training is slow, NET/Socket
  appears, or checking whether InfiniBand and GPU Direct RDMA are engaged.
  Trigger with "coreweave slow training", "is RDMA working", "NCCL fell back to TCP",
  "GPUDirect RDMA", or "infiniband not used".
allowed-tools: Read, Write, Edit, Glob, Bash(kubectl get:*), Bash(python3:*)
version: 1.14.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Designed for Claude Code
tags: [saas, coreweave, gpu-cloud, rdma, nccl]
---
# CoreWeave Fabric Diagnostics

> **Community-contributed.** Not affiliated with, endorsed by, or sponsored by CoreWeave, Inc. CoreWeave is a registered trademark of CoreWeave, Inc.

## Overview

Review positive NCCL transport evidence without guessing a slowdown or billing impact.
The offline script distinguishes an InfiniBand transport selection from positive GPU Direct RDMA evidence.
A warning mentioning NET/IB, a bootstrap socket or an isolated bandwidth figure cannot establish a healthy data path.
Use Read for supplied diagnostics, Glob for owner-selected rank logs, Write the report and Edit the proposed local correction; do not mutate the cluster.

## Prerequisites

- Sanitized NCCL_DEBUG=INFO output from one known run, with rank/time identity preserved.
- Optional admitted Pod resource blocks and ibstat output from the same scope; Pod YAML may contain secrets and must be reviewed before sharing.
- Python 3 and the pinned PyYAML dependency from `scripts/requirements.txt`, installed in a local isolated environment.
- Owner authorization before any cluster query, rerun, benchmark or resource change; those may access data or spend compute.

## Instructions

1. Separate runs and ranks. Read `references/nccl-debug-reading.md` to distinguish bootstrap, transport selection, warnings and GDR evidence.
2. Run the bundled checker on the supplied diagnostic file. Treat `unknown` as missing evidence and `mixed` as requiring rank/run correlation, not a guaranteed broken fabric.
3. Review each communicating container’s resource block independently. `rdma/ib: 1` in limits can supply an omitted request through Kubernetes defaulting; an explicit request must match. Requests-only, zero and mismatched values need correction.
4. Confirm the Node Pool supports InfiniBand, the image has the appropriate NCCL/OFED userspace, and effective environment settings match the current platform guidance. A missing environment line in a paste does not prove the variable is unset.
5. Have the platform owner review the proposed manifest change, then collect fresh evidence from the same workload. Do not install host drivers, reset GPUs or override managed health cordons.
6. Compare busbw with an equivalent measured baseline including topology, GPU count, image, driver/NCCL versions and message size. No fixed speedup, slowdown or dollar saving is inferred.

## Examples

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/fabric-check.py" --in diagnostics.txt --json
python3 "${CLAUDE_SKILL_DIR}/scripts/fabric-check.py" --self-test
```

For an owner-approved read of the exact Pod, use an explicit context and namespace, and review its output before retaining it:

```bash
kubectl --context="$CW_CONTEXT" --namespace="$CW_NAMESPACE" get "pod/$CW_POD" -o yaml
```

A positive `Using network IB` observation sets transport to IB; without a GDR marker, `gpu_direct_rdma_confirmed` stays false.
The compatibility field `rdma_engaged` describes the observed transport category, not complete fabric health or GPU-direct verification.

## Output

- Transport, separate GDR evidence, resource findings and port observations.
- Observed bandwidth labeled unverified against a baseline, with no invented pass/fail threshold.
- A bounded proposed next step and explicit incomplete evidence; no automatic cluster action.

## Error Handling

| Observation | Response |
|---|---|
| Only an IB failure warning | Transport remains unknown; obtain positive selection/data-path evidence. |
| Limits-only rdma/ib: 1 | Accept request defaulting; investigate the effective Pod and transport instead of demanding duplicate YAML. |
| Multiple container blocks | Review each independently; do not combine a sidecar request with another container’s limit. |
| Inactive/Down port | Report the port observation to the platform owner; it does not establish the root cause of every Node event. |
| No complete log | Preserve unknown; a keyword count is not proof of success. |

## Resources

- [Resource and device checks](references/rdma-engagement-checklist.md)
- [NCCL evidence interpretation](references/nccl-debug-reading.md)
- [Bandwidth comparison](references/allreduce-baseline.md)
- [CoreWeave RDMA guidance](https://docs.coreweave.com/products/networking/hpc-interconnect/use-gpudirect-rdma)

## Evidence status

Deterministic offline fixtures cover parsing and refusal cases. No live NCCL, GPU benchmark or CoreWeave account was used for this package review.
