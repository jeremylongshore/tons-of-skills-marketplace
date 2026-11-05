---
name: coreweave-prod-checklist
description: 'Production readiness checklist for CoreWeave GPU workloads.

  Use when launching inference services, preparing GPU training for production,

  or validating deployment configurations.

  Trigger with phrases like "coreweave production", "coreweave go-live",

  "coreweave checklist", "coreweave launch".

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
# CoreWeave Production Checklist

> **Community-contributed.** Not affiliated with, endorsed by, or sponsored by CoreWeave, Inc. CoreWeave is a registered trademark of CoreWeave, Inc.

## Overview

Use this gate before exposing a CoreWeave inference or training workload to
production. It proves that capacity, data protection, observability, and recovery
are owned and tested; it is not a substitute for a service-specific risk review.

## Prerequisites

- A signed deployment change, named service owner, and approved production namespace.
- Passing staging evaluation, capacity forecast, and rollback manifest.
- On-call routing, secret-manager references, and data classification for the workload.

## Instructions

1. Complete each checklist item with a link to its evidence, not a verbal assertion.
2. Confirm a staged rollout, health check, and rollback command during the change window.
3. Stop the release if any security, data, capacity, or observability gate lacks an owner.
4. Record the final go/no-go decision, time, owner, and redacted verification receipt.

## Inference Services

- [ ] GPU type and count validated for model size
- [ ] Autoscaling configured (KServe or HPA)
- [ ] Health and readiness probes set
- [ ] Resource requests AND limits specified
- [ ] Node affinity targeting correct GPU class
- [ ] `minReplicas >= 1` for production (no cold starts)

## Storage

- [ ] Model weights in PVC (not downloaded at startup)
- [ ] Checkpoints saved to persistent storage
- [ ] Storage class appropriate (SSD for inference, HDD for archival)

## Security

- [ ] Secrets for model tokens and registry access
- [ ] Network policies applied
- [ ] Container images from trusted registries

## Monitoring

- [ ] GPU utilization metrics collected
- [ ] Inference latency and throughput tracked
- [ ] Alert on pod restarts and OOM events
- [ ] Log aggregation configured

## Rollback

```bash
kubectl rollout undo deployment/my-inference
kubectl rollout status deployment/my-inference
```

## Output

- A production-readiness record linking capacity, storage, security, monitoring, and
  rollback evidence to the deployment.
- A clear go/no-go decision with a responsible owner and tested recovery command.

## Error Handling

| Failed gate | Required action |
|---|---|
| Readiness or staging test fails | Hold the release and restore the prior known-good revision. |
| GPU capacity is unconfirmed | Do not launch; resolve quota or capacity with the platform owner. |
| Secret or network policy is missing | Block deployment until the namespace hardening baseline is present. |
| Monitoring route is absent | Block production exposure until alerts reach the on-call owner. |

## Examples

Run the last production checks during the approved change window:

```bash
kubectl -n inference-prod apply -f release.yaml
kubectl -n inference-prod rollout status deployment/my-inference --timeout=15m
kubectl -n inference-prod get pods -l app=my-inference
```

If rollout or the smoke test fails, execute the documented rollback immediately,
capture redacted events, and mark the change no-go rather than retrying with weaker
security or capacity controls.

## Resources

- [CoreWeave CKS](https://docs.coreweave.com/docs/products/cks)

## Next Steps

For upgrades, see `coreweave-upgrade-migration`.
