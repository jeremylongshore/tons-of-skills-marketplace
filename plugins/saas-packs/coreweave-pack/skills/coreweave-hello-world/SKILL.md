---
name: coreweave-hello-world
description: 'Deploy a GPU workload on CoreWeave with kubectl.

  Use when running your first GPU job, testing inference,

  or verifying CoreWeave cluster access.

  Trigger with phrases like "coreweave hello world", "coreweave first deploy",

  "coreweave gpu test", "run on coreweave".

  '
allowed-tools: Read, Write, Edit, Bash(kubectl:*)
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
# CoreWeave Hello World

> **Community-contributed.** Not affiliated with, endorsed by, or sponsored by CoreWeave, Inc. CoreWeave is a registered trademark of CoreWeave, Inc.

## Overview

Deploy your first GPU workload on CoreWeave: a simple inference service using vLLM or a batch CUDA job. CoreWeave runs Kubernetes on bare-metal GPU nodes with A100, H100, and L40 GPUs.

## Prerequisites

- Completed `coreweave-install-auth` setup
- kubectl configured with CoreWeave kubeconfig
- Namespace with GPU quota

## Instructions

### Step 1: Deploy a vLLM Inference Server

```yaml
# vllm-inference.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vllm-server
spec:
  replicas: 1
  selector:
    matchLabels:
      app: vllm-server
  template:
    metadata:
      labels:
        app: vllm-server
    spec:
      containers:
        - name: vllm
          image: vllm/vllm-openai:latest
          args:
            - "--model"
            - "meta-llama/Llama-3.1-8B-Instruct"
            - "--port"
            - "8000"
          ports:
            - containerPort: 8000
          resources:
            limits:
              nvidia.com/gpu: 1
              memory: 48Gi
              cpu: "8"
            requests:
              nvidia.com/gpu: 1
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
---
apiVersion: v1
kind: Service
metadata:
  name: vllm-server
spec:
  selector:
    app: vllm-server
  ports:
    - port: 8000
      targetPort: 8000
  type: ClusterIP
```

```bash
# Create HuggingFace token secret
kubectl create secret generic hf-token --from-literal=token="${HF_TOKEN}"

# Deploy
kubectl apply -f vllm-inference.yaml
kubectl get pods -w  # Wait for Running state

# Port-forward and test
kubectl port-forward svc/vllm-server 8000:8000 &
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "meta-llama/Llama-3.1-8B-Instruct", "messages": [{"role": "user", "content": "Hello!"}]}'
```

### Step 2: Batch GPU Job

```yaml
# gpu-batch-job.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: gpu-benchmark
spec:
  template:
    spec:
      restartPolicy: Never
      containers:
        - name: benchmark
          image: pytorch/pytorch:2.2.0-cuda12.1-cudnn8-runtime
          command: ["python3", "-c"]
          args:
            - |
              import torch
              print(f"CUDA available: {torch.cuda.is_available()}")
              print(f"GPU: {torch.cuda.get_device_name(0)}")
              x = torch.randn(10000, 10000, device="cuda")
              y = torch.matmul(x, x)
              print(f"Matrix multiply result shape: {y.shape}")
              print("CoreWeave GPU test passed!")
          resources:
            limits:
              nvidia.com/gpu: 1
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
kubectl apply -f gpu-batch-job.yaml
kubectl logs job/gpu-benchmark --follow
```

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Pod stuck Pending | No GPU capacity | Try different GPU type or check quota |
| `nvidia-smi` not found | Wrong base image | Use NVIDIA CUDA images |
| OOMKilled | Insufficient GPU memory | Use larger GPU (80GB A100) |
| Image pull error | Registry auth | Create imagePullSecret |

## Output

- A minimal, namespace-scoped GPU workload or inference endpoint with one declared GPU.
- A visible readiness signal and a bounded smoke-test response that confirms the GPU
  runtime path without placing a model token or customer prompt in source control.

## Examples

Validate the batch path first because it is cheaper and easier to roll back than a
public endpoint:

```bash
kubectl -n sandbox apply -f gpu-batch-job.yaml
kubectl -n sandbox wait --for=condition=complete job/gpu-benchmark --timeout=15m
kubectl -n sandbox logs job/gpu-benchmark
```

Delete the smoke job after recording its redacted result. If it remains Pending,
inspect its events and namespace quota—do not broaden cluster permissions or embed
registry credentials in the manifest to force it through.

## Resources

- [CoreWeave GPU Instances](https://docs.coreweave.com/docs/platform/instances/gpu-instances)
- [Deploy vLLM](https://docs.coreweave.com/docs/products/cks/tutorials/deploy-vllm-inference)
- [CoreWeave Examples](https://github.com/coreweave/kubernetes-cloud)

## Next Steps

Proceed to `coreweave-local-dev-loop` for development workflow setup.
