---
name: coreweave-core-workflow-a
description: 'Deploy KServe InferenceService on CoreWeave with autoscaling and GPU
  scheduling.

  Use when serving ML models with KServe, configuring scale-to-zero,

  or deploying production inference endpoints on CoreWeave.

  Trigger with phrases like "coreweave inference service", "coreweave kserve",

  "coreweave model serving", "deploy model on coreweave".

  '
allowed-tools: Read, Write, Edit, Bash(kubectl:*), Grep
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
# CoreWeave Core Workflow: KServe Inference

> **Community-contributed.** Not affiliated with, endorsed by, or sponsored by CoreWeave, Inc. CoreWeave is a registered trademark of CoreWeave, Inc.

## Overview

Deploy production inference services on CoreWeave using KServe InferenceService with GPU scheduling, autoscaling, and scale-to-zero. CKS natively integrates with KServe for serverless GPU inference.

## Prerequisites

- Completed `coreweave-install-auth` setup
- KServe available on your CKS cluster
- Model stored in S3, GCS, or HuggingFace

## Instructions

### Step 1: Deploy an InferenceService

```yaml
# inference-service.yaml
apiVersion: serving.kserve.io/v1beta1
kind: InferenceService
metadata:
  name: llama-inference
  annotations:
    autoscaling.knative.dev/class: "kpa.autoscaling.knative.dev"
    autoscaling.knative.dev/metric: "concurrency"
    autoscaling.knative.dev/target: "1"
    autoscaling.knative.dev/minScale: "1"
    autoscaling.knative.dev/maxScale: "5"
spec:
  predictor:
    minReplicas: 1
    maxReplicas: 5
    containers:
      - name: kserve-container
        image: vllm/vllm-openai:latest
        args:
          - "--model"
          - "meta-llama/Llama-3.1-8B-Instruct"
          - "--port"
          - "8080"
        ports:
          - containerPort: 8080
            protocol: TCP
        resources:
          limits:
            nvidia.com/gpu: "1"
            memory: 48Gi
            cpu: "8"
          requests:
            nvidia.com/gpu: "1"
            memory: 32Gi
            cpu: "4"
        env:
          - name: HUGGING_FACE_HUB_TOKEN
            valueFrom:
              secretKeyRef:
                name: hf-token
                key: token
    affinity:
      nodeAffinity:
        requiredDuringSchedulingIgnoredDuringExecution:
          nodeSelectorTerms:
            - matchExpressions:
                - key: gpu.nvidia.com/class
                  operator: In
                  values: ["A100_PCIE_80GB"]
```

```bash
kubectl apply -f inference-service.yaml
kubectl get inferenceservice llama-inference -w
```

### Step 2: Scale-to-Zero Configuration

```yaml
# For dev/staging -- scale down to zero when idle
metadata:
  annotations:
    autoscaling.knative.dev/minScale: "0"    # Scale to zero
    autoscaling.knative.dev/maxScale: "3"
    autoscaling.knative.dev/scaleDownDelay: "5m"
```

### Step 3: Test the Endpoint

```bash
# Get inference URL
INFERENCE_URL=$(kubectl get inferenceservice llama-inference \
  -o jsonpath='{.status.url}')

curl -X POST "${INFERENCE_URL}/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{"model": "meta-llama/Llama-3.1-8B-Instruct", "messages": [{"role": "user", "content": "Hello!"}]}'
```

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| InferenceService not ready | GPU not available | Check node capacity and affinity |
| Scale-to-zero cold start | First request after idle | Set `minScale: 1` for production |
| Model loading timeout | Large model download | Pre-cache model in PVC |
| OOMKilled | Model too large | Use multi-GPU or quantized model |

## Output

- A namespace-scoped inference service with declared compute, GPU, and secret inputs.
- A readiness and endpoint smoke-test result suitable for the deployment record.
- A scale-to-zero configuration limited to appropriate non-production workloads,
  with a documented production availability decision.

## Examples

Deploy to staging and wait for the service readiness condition before sending a
minimal health request:

```bash
kubectl -n inference-staging apply -f inference-service.yaml
kubectl -n inference-staging get inferenceservice llama-inference --watch
kubectl -n inference-staging get pods -l serving.kserve.io/inferenceservice=llama-inference
```

If readiness stalls, inspect events, image pull status, GPU availability, and the
secret reference. Do not expose the endpoint publicly or replace a secret reference
with a plaintext token as a debugging shortcut.

## Resources

- [CoreWeave Inference](https://docs.coreweave.com/docs/products/cks/tutorials/deploy-vllm-inference)
- [KServe Documentation](https://kserve.github.io/website/)

## Next Steps

For GPU training workloads, see `coreweave-core-workflow-b`.
