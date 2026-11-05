---
name: coreweave-deploy-integration
description: 'Deploy inference services on CoreWeave with Helm charts and Kustomize.

  Use when deploying multi-model inference, managing GPU deployments at scale,

  or templating CoreWeave manifests.

  Trigger with phrases like "deploy coreweave", "coreweave helm",

  "coreweave kustomize", "coreweave deployment patterns".

  '
allowed-tools: Read, Write, Edit, Bash(helm:*), Bash(kubectl:*), Bash(kustomize:*)
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
# CoreWeave Deploy Integration

> **Community-contributed.** Not affiliated with, endorsed by, or sponsored by CoreWeave, Inc. CoreWeave is a registered trademark of CoreWeave, Inc.

## Overview

Deploy GPU-accelerated inference services on CoreWeave Kubernetes (CKS). This skill covers containerizing inference workloads with NVIDIA CUDA base images, configuring GPU resource limits and node affinity for A100/H100 scheduling, setting up health checks that validate GPU availability and model loading, and executing rolling updates that respect GPU node draining. CoreWeave's scheduler requires explicit GPU resource requests to place pods on the correct hardware tier.

## Docker Configuration

## Prerequisites

- A reviewed image digest in an approved registry and a namespace-scoped image pull secret.
- A production deployment manifest with resource limits, health checks, SLO, and rollback revision.
- Approval for the target namespace, GPU capacity, and service exposure.

## Instructions

1. Build and scan the image, then deploy the immutable digest to staging first.
2. Verify readiness, health, GPU allocation, and baseline request behavior before promotion.
3. Use a controlled rolling update with a timeout and named observer.
4. Roll back immediately if readiness, error rate, latency, or security verification fails.

```dockerfile
FROM nvidia/cuda:12.4.0-runtime-ubuntu22.04 AS base
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip curl && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

FROM base
RUN groupadd -r app && useradd -r -g app app
COPY --chown=app:app src/ ./src/
COPY --chown=app:app models/ ./models/
USER app
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1
CMD ["python3", "src/server.py"]
```

## Environment Variables

```bash
export COREWEAVE_API_KEY="cw_xxxxxxxxxxxx"
export COREWEAVE_NAMESPACE="tenant-my-org"
export MODEL_NAME="meta-llama/Llama-3.1-8B-Instruct"
export GPU_TYPE="A100_PCIE_80GB"
export GPU_COUNT="1"
export LOG_LEVEL="info"
export PORT="8080"
```

## Health Check Endpoint

```typescript
import express from 'express';
import { execSync } from 'child_process';

const app = express();

app.get('/health', async (req, res) => {
  try {
    const gpuInfo = execSync('nvidia-smi --query-gpu=name,memory.used --format=csv,noheader').toString().trim();
    const modelLoaded = globalThis.modelReady === true;
    if (!modelLoaded) throw new Error('Model not loaded');
    res.json({ status: 'healthy', gpu: gpuInfo, model: process.env.MODEL_NAME, timestamp: new Date().toISOString() });
  } catch (error) {
    res.status(503).json({ status: 'unhealthy', error: (error as Error).message });
  }
});
```

## Deployment Steps

### Step 1: Build

```bash
docker build -t registry.coreweave.com/my-org/inference-svc:latest .
docker push registry.coreweave.com/my-org/inference-svc:latest
```

### Step 2: Run

```yaml
# k8s/deployment.yaml
resources:
  limits:
    nvidia.com/gpu: 1
    cpu: "4"
    memory: "48Gi"
nodeSelector:
  gpu.nvidia.com/class: A100_PCIE_80GB
```

```bash
kubectl apply -f k8s/deployment.yaml -n tenant-my-org
```

### Step 3: Verify

```bash
kubectl get pods -n tenant-my-org -l app=inference-svc
curl -s http://inference-svc.tenant-my-org.svc.cluster.local:8080/health | jq .
```

### Step 4: Rolling Update

```bash
kubectl set image deployment/inference-svc \
  inference=registry.coreweave.com/my-org/inference-svc:v2 \
  -n tenant-my-org
kubectl rollout status deployment/inference-svc -n tenant-my-org --timeout=600s
```

## Error Handling

| Issue | Cause | Fix |
|-------|-------|-----|
| `Pending` pod stuck | No GPU nodes available for requested type | Check `kubectl describe node` for allocatable GPUs or switch GPU tier |
| `OOMKilled` | Model exceeds GPU memory | Reduce model size, enable quantization, or request larger GPU |
| `nvidia-smi` not found | Missing NVIDIA device plugin | Verify CoreWeave namespace has GPU operator installed |
| `401 Unauthorized` | Invalid API key or expired credentials | Regenerate key in CoreWeave dashboard |
| Slow rolling update | GPU nodes take time to drain | Set `terminationGracePeriodSeconds: 300` in deployment spec |

## Output

- A versioned, health-checked GPU deployment with declared capacity and ownership.
- A rollout receipt containing image digest, readiness result, and redacted event evidence.
- A known rollback command and threshold for using it.

## Examples

Deploy an immutable staging image and wait for the rollout before sending traffic:

```bash
kubectl -n tenant-staging set image deployment/inference-svc \
  inference=registry.coreweave.com/my-org/inference-svc@sha256:REVIEWED_DIGEST
kubectl -n tenant-staging rollout status deployment/inference-svc --timeout=10m
```

If the rollout fails, use `kubectl rollout undo` for the same deployment and record the redacted events. Do not retag `latest`, bypass health checks, or substitute plaintext credentials.

## Resources

- [CoreWeave CKS Docs](https://docs.coreweave.com/docs/products/cks)
- CoreWeave GPU Types

## Next Steps

See `coreweave-webhooks-events`.
