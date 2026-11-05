---
name: coreweave-performance-tuning
description: 'Optimize CoreWeave GPU inference latency and throughput.

  Use when reducing inference latency, maximizing GPU utilization,

  or tuning batch sizes and concurrency.

  Trigger with phrases like "coreweave performance", "coreweave latency",

  "coreweave throughput", "optimize coreweave inference".

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
# CoreWeave Performance Tuning

> **Community-contributed.** Not affiliated with, endorsed by, or sponsored by CoreWeave, Inc. CoreWeave is a registered trademark of CoreWeave, Inc.

## Overview

Tune GPU inference or training only against measured throughput, latency, quality,
availability, and cost targets. A higher utilization figure is not a success if it
causes queueing, memory pressure, or a customer-facing SLO regression.

## Prerequisites

- A baseline for p95/p99 latency, throughput, error rate, GPU memory, and utilization.
- A representative non-sensitive evaluation set and a named owner for the SLO.
- A staging lane and a rollback manifest for every resource or serving change.

## Instructions

1. Change one variable at a time—batching, GPU class, replicas, or memory target.
2. Run the agreed load and quality evaluation in staging, then compare with baseline.
3. Promote a canary only when all SLO and quality thresholds pass for the observation window.
4. Revert to the prior manifest when latency, errors, or quality crosses the agreed limit.

## GPU Selection by Workload

| Workload | Recommended GPU | Why |
|----------|----------------|-----|
| LLM inference (7-13B) | A100 80GB | Good balance of memory and cost |
| LLM inference (70B+) | 8xH100 | NVLink for tensor parallelism |
| Image generation | L40 | Good for diffusion models |
| Training (large models) | 8xH100 SXM5 | Fastest interconnect |
| Batch processing | A100 40GB | Cost-effective |

## Inference Optimization

```yaml
# Continuous batching with vLLM
containers:
  - name: vllm
    args:
      - "--model=meta-llama/Llama-3.1-8B-Instruct"
      - "--max-num-batched-tokens=8192"
      - "--max-num-seqs=256"
      - "--gpu-memory-utilization=0.90"
      - "--enable-prefix-caching"
      - "--dtype=float16"
```

## Autoscaling Tuning

```yaml
# HPA based on GPU utilization
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: inference-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: inference-server
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Pods
      pods:
        metric:
          name: DCGM_FI_DEV_GPU_UTIL
        target:
          type: AverageValue
          averageValue: "70"
```

## Performance Benchmarks

| Metric | A100-80GB | H100-80GB |
|--------|-----------|-----------|
| Llama-8B tokens/sec | ~2,000 | ~4,500 |
| Llama-70B tokens/sec | ~200 (4x) | ~500 (4x) |
| Cold start (vLLM) | 30-60s | 20-40s |

## Output

- A measured performance baseline and a single reviewed tuning recommendation.
- A canary result covering throughput, latency, error rate, GPU memory, and quality.
- A versioned rollback manifest with a named decision owner.

## Error Handling

| Condition | Safe response |
|---|---|
| GPU memory exceeds the guardrail | Restore the previous batch or memory setting and investigate the request distribution. |
| Latency rises after batching | Reduce concurrency or restore replica count; do not raise timeouts to hide the regression. |
| Evaluation quality drops | Route the canary back to the baseline configuration and preserve aggregate results. |
| Autoscaler oscillates | Restore stable bounds and tune from a longer measured window. |

## Examples

Run a staging canary and save only aggregate measurements for review:

```bash
kubectl -n inference-staging apply -f inference-tuned.yaml
kubectl -n inference-staging rollout status deployment/inference-server --timeout=10m
./scripts/load-test --target staging --duration 15m --report aggregate.json
```

If the report breaches the signed SLO or quality threshold, apply the previous
manifest immediately and attach `aggregate.json` to the change record.

## Resources

- [CoreWeave Inference](https://www.coreweave.com/solutions/ai-inference)
- [vLLM Documentation](https://docs.vllm.ai)

## Next Steps

For cost optimization, see `coreweave-cost-tuning`.
