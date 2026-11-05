---
name: coreweave-install-auth
description: 'Configure CoreWeave Kubernetes Service (CKS) access with kubeconfig
  and API tokens.

  Use when setting up kubectl access to CoreWeave, configuring CKS clusters,

  or authenticating with CoreWeave cloud services.

  Trigger with phrases like "install coreweave", "setup coreweave",

  "coreweave kubeconfig", "coreweave auth", "connect to coreweave".

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
# CoreWeave Install & Auth

> **Community-contributed.** Not affiliated with, endorsed by, or sponsored by CoreWeave, Inc. CoreWeave is a registered trademark of CoreWeave, Inc.

## Overview

Set up access to CoreWeave Kubernetes Service (CKS). CKS runs bare-metal Kubernetes with NVIDIA GPUs -- no hypervisor overhead. Access is via standard kubeconfig with CoreWeave-issued credentials.

## Prerequisites

- CoreWeave account at https://cloud.coreweave.com
- `kubectl` v1.28+ installed
- Kubernetes namespace provisioned by CoreWeave

## Instructions

### Step 1: Download Kubeconfig

1. Log in to https://cloud.coreweave.com
2. Navigate to **API Access** > **Kubeconfig**
3. Download the kubeconfig file

```bash
# Save kubeconfig
mkdir -p ~/.kube
cp ~/Downloads/coreweave-kubeconfig.yaml ~/.kube/coreweave

# Set as active context
export KUBECONFIG=~/.kube/coreweave

# Verify connection
kubectl get nodes
kubectl get namespaces
```

### Step 2: Configure API Token

```bash
# CoreWeave API token for programmatic access
export COREWEAVE_API_TOKEN="your-api-token"

# Store securely
echo "COREWEAVE_API_TOKEN=${COREWEAVE_API_TOKEN}" >> .env
echo "KUBECONFIG=~/.kube/coreweave" >> .env
```

### Step 3: Verify GPU Access

```bash
# List available GPU nodes
kubectl get nodes -l gpu.nvidia.com/class -o custom-columns=\
NAME:.metadata.name,GPU:.metadata.labels.gpu\.nvidia\.com/class,\
STATUS:.status.conditions[-1].type

# Check GPU allocatable resources
kubectl describe nodes | grep -A5 "Allocatable:" | grep nvidia
```

### Step 4: Test with a Simple GPU Pod

```yaml
# test-gpu.yaml
apiVersion: v1
kind: Pod
metadata:
  name: gpu-test
spec:
  restartPolicy: Never
  containers:
    - name: cuda-test
      image: nvidia/cuda:12.2.0-base-ubuntu22.04
      command: ["nvidia-smi"]
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
kubectl apply -f test-gpu.yaml
kubectl logs gpu-test  # Should show nvidia-smi output
kubectl delete pod gpu-test
```

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `Unable to connect to the server` | Wrong kubeconfig | Verify KUBECONFIG path |
| `Forbidden` | Missing namespace permissions | Contact CoreWeave support |
| No GPU nodes found | Wrong node labels | Check `gpu.nvidia.com/class` labels |
| Pod stuck Pending | GPU capacity exhausted | Try different GPU type or region |

## Output

- A namespace-scoped Kubernetes context and a verified GPU scheduling result.
- A credential setup that references the approved secret manager and never commits or prints live values.
- A deleted smoke-test Pod after its redacted result is recorded.

## Examples

Configure a temporary shell session from your secret manager, then run the smallest GPU smoke test in a sandbox namespace:

```bash
export KUBECONFIG="$HOME/.kube/coreweave-sandbox"
kubectl -n sandbox apply -f test-gpu.yaml
kubectl -n sandbox wait --for=condition=Ready pod/gpu-test --timeout=10m
kubectl -n sandbox logs gpu-test
kubectl -n sandbox delete -f test-gpu.yaml
```

If access is denied or capacity is unavailable, retain the redacted status and contact the namespace owner. Do not put a token in `.env`, a manifest, shell history, or support tickets.

## Resources

- [CoreWeave Documentation](https://docs.coreweave.com)
- [CKS Introduction](https://docs.coreweave.com/docs/products/cks)
- [GPU Instance Types](https://docs.coreweave.com/docs/platform/instances/gpu-instances)

## Next Steps

Proceed to `coreweave-hello-world` to deploy your first inference service.
