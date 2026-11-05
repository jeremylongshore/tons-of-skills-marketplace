---
name: coreweave-sdk-patterns
description: 'Production-ready patterns for CoreWeave GPU workload management with
  kubectl and Python.

  Use when building inference clients, managing GPU deployments programmatically,

  or creating reusable CoreWeave deployment templates.

  Trigger with phrases like "coreweave patterns", "coreweave client",

  "coreweave Python", "coreweave deployment template".

  '
allowed-tools: Read, Write, Edit
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
# CoreWeave SDK Patterns

> **Community-contributed.** Not affiliated with, endorsed by, or sponsored by CoreWeave, Inc. CoreWeave is a registered trademark of CoreWeave, Inc.

## Overview

CoreWeave is Kubernetes-native -- use kubectl, Kubernetes Python client, or Helm for programmatic management. These patterns cover GPU-aware deployment templates, inference client wrappers, and node affinity configurations.

## Instructions

### GPU Affinity Helper

```python
# coreweave_helpers.py
from dataclasses import dataclass

@dataclass
class GPUConfig:
    gpu_class: str        # A100_PCIE_80GB, H100_SXM5, L40, etc.
    gpu_count: int = 1
    memory_gb: int = 32
    cpu_cores: int = 4

GPU_CATALOG = {
    "a100-80gb": GPUConfig("A100_PCIE_80GB", memory_gb=48, cpu_cores=8),
    "h100-80gb": GPUConfig("H100_SXM5", memory_gb=64, cpu_cores=12),
    "l40":       GPUConfig("L40", memory_gb=24, cpu_cores=4),
    "a100-8x":   GPUConfig("A100_NVLINK_A100_SXM4_80GB", gpu_count=8, memory_gb=256, cpu_cores=64),
}

def gpu_affinity_block(gpu_class: str) -> dict:
    return {
        "nodeAffinity": {
            "requiredDuringSchedulingIgnoredDuringExecution": {
                "nodeSelectorTerms": [{
                    "matchExpressions": [{
                        "key": "gpu.nvidia.com/class",
                        "operator": "In",
                        "values": [gpu_class],
                    }]
                }]
            }
        }
    }

def gpu_resources(config: GPUConfig) -> dict:
    return {
        "limits": {
            "nvidia.com/gpu": str(config.gpu_count),
            "memory": f"{config.memory_gb}Gi",
            "cpu": str(config.cpu_cores),
        },
        "requests": {
            "nvidia.com/gpu": str(config.gpu_count),
            "memory": f"{config.memory_gb // 2}Gi",
            "cpu": str(config.cpu_cores // 2),
        },
    }
```

### Inference Client Wrapper

```python
# inference_client.py
import requests
from typing import Optional

class CoreWeaveInferenceClient:
    def __init__(self, endpoint: str, timeout: int = 30):
        self.endpoint = endpoint.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()

    def generate(self, prompt: str, max_tokens: int = 256, **kwargs) -> str:
        resp = self.session.post(
            f"{self.endpoint}/v1/completions",
            json={"prompt": prompt, "max_tokens": max_tokens, **kwargs},
            timeout=self.timeout,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["text"]

    def chat(self, messages: list[dict], **kwargs) -> str:
        resp = self.session.post(
            f"{self.endpoint}/v1/chat/completions",
            json={"messages": messages, **kwargs},
            timeout=self.timeout,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]

    def health(self) -> bool:
        try:
            resp = self.session.get(f"{self.endpoint}/health", timeout=5)
            return resp.status_code == 200
        except Exception:
            return False
```

### Deployment Template Generator

```python
import yaml

def generate_inference_deployment(
    name: str,
    image: str,
    gpu_type: str = "a100-80gb",
    replicas: int = 1,
    port: int = 8000,
) -> str:
    config = GPU_CATALOG[gpu_type]
    return yaml.dump({
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": {"name": name},
        "spec": {
            "replicas": replicas,
            "selector": {"matchLabels": {"app": name}},
            "template": {
                "metadata": {"labels": {"app": name}},
                "spec": {
                    "containers": [{
                        "name": name,
                        "image": image,
                        "ports": [{"containerPort": port}],
                        "resources": gpu_resources(config),
                    }],
                    "affinity": gpu_affinity_block(config.gpu_class),
                },
            },
        },
    })
```

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| GPU class not found | Typo in node label | Use exact values from `gpu.nvidia.com/class` |
| OOM on inference | Model too large for GPU | Use larger GPU or quantized model |
| Connection refused | Service not ready | Check pod readiness probe |

## Prerequisites

- A namespace-scoped Kubernetes credential and endpoint from the approved environment.
- An image, GPU class, and resource budget reviewed for the target workload.
- A secret-manager reference for private registry or model access; never pass tokens
  into generated YAML or application logs.

## Output

- A reusable client or deployment manifest pattern with explicit GPU resources and
  affinity constraints.
- A readiness-aware request path that distinguishes unavailable services from a
  valid application response.
- A generated manifest that can be reviewed, versioned, and rolled back before apply.

## Examples

Generate a manifest, inspect it for the expected namespace and GPU resource limit,
then apply it first in staging:

```python
manifest = generate_inference_deployment('summarizer', 'registry.example/summarizer:v1')
open('summarizer.yaml', 'w').write(manifest)
```

```bash
kubectl -n inference-staging apply --dry-run=server -f summarizer.yaml
kubectl -n inference-staging apply -f summarizer.yaml
kubectl -n inference-staging rollout status deployment/summarizer --timeout=10m
```

If validation or rollout fails, retain the reviewed manifest and redacted events;
do not broaden the client credential or bypass the admission policy.

## Resources

- [CoreWeave GPU Instances](https://docs.coreweave.com/docs/platform/instances/gpu-instances)
- [Kubernetes Python Client](https://github.com/kubernetes-client/python)

## Next Steps

Apply patterns in `coreweave-core-workflow-a` for KServe inference deployments.
