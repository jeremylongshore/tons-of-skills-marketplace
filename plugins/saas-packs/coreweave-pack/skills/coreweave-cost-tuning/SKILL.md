---
name: coreweave-cost-tuning
description: 'Optimize CoreWeave GPU cloud costs with right-sizing and scheduling.

  Use when reducing GPU spend, selecting cost-effective instances,

  or implementing scale-to-zero for dev workloads.

  Trigger with phrases like "coreweave cost", "coreweave pricing",

  "reduce coreweave spend", "coreweave budget".

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
# CoreWeave Cost Tuning

> **Community-contributed.** Not affiliated with, endorsed by, or sponsored by CoreWeave, Inc. CoreWeave is a registered trademark of CoreWeave, Inc.

## Overview

Reduce GPU spend by matching a workload's memory, throughput, availability, and
latency requirements to the smallest approved capacity. Cost changes must preserve
the service SLO and retain a measured rollback path; approximate public prices are
planning inputs, not a billing source of truth.

## Prerequisites

- Read-only access to workload utilization, namespace quota, and billing allocation data.
- A named service owner and target SLO for the workload being resized.
- Approval for any change that can reduce production capacity or alter availability.

## GPU Pricing Reference (approximate)

| GPU | Per GPU/hour | Best For |
|-----|-------------|----------|
| A100 40GB PCIe | ~$1.50 | Development, smaller models |
| A100 80GB PCIe | ~$2.21 | Production inference |
| H100 80GB PCIe | ~$4.76 | High-throughput inference |
| H100 SXM5 (8x) | ~$6.15/GPU | Training, multi-GPU |
| L40 | ~$1.10 | Image generation, light inference |

## Cost Optimization Strategies

### Scale-to-Zero for Dev/Staging

```yaml
autoscaling.knative.dev/minScale: "0"
autoscaling.knative.dev/scaleDownDelay: "5m"
```

### Right-Size GPU Selection

```python
def recommend_gpu(model_size_b: float, inference_only: bool = True) -> str:
    if model_size_b <= 7:
        return "L40" if inference_only else "A100_PCIE_80GB"
    elif model_size_b <= 13:
        return "A100_PCIE_80GB"
    elif model_size_b <= 70:
        return "A100_PCIE_80GB (4x tensor parallel)"
    else:
        return "H100_SXM5 (8x tensor parallel)"
```

### Quantization to Use Smaller GPUs

Use AWQ or GPTQ quantization to fit larger models on smaller GPUs:

```bash
# 70B model at 4-bit fits on single A100-80GB instead of 4x
vllm serve meta-llama/Llama-3.1-70B-Instruct-AWQ --quantization awq
```

## Instructions

1. Baseline seven days of GPU utilization, queue time, request latency, error rate,
   and allocated cost by namespace; do not decide from a single peak.
2. Propose one reversible change—right-size a non-production workload, set a
   conservative scale-down delay, or run a quantized canary.
3. Compare the canary against its SLO and budget for an agreed observation window.
   Promote only if quality, latency, and error rate remain within the published limit.
4. Record the instance choice, owner, forecast, and rollback trigger in the
   change record. Revert capacity immediately if the workload breaches its SLO.

## Output

- A documented utilization baseline and cost allocation for the selected workload.
- A right-sizing or scale-to-zero recommendation with its performance guardrails.
- A reversible change record containing owner, observation window, and rollback threshold.

## Error Handling

| Condition | Likely cause | Safe response |
|---|---|---|
| Latency rises after downsizing | Insufficient GPU capacity or queueing | Restore the previous resource request and investigate with the service owner. |
| Cost data is incomplete | Labels or billing export are missing | Stop the optimization; repair allocation labels before making a pricing decision. |
| Quantized canary loses quality | Model or quantization setting is unsuitable | Route traffic back to the baseline model and retain the evaluation result. |
| Scale-to-zero causes cold-start failures | Delay or startup budget is too small | Restore minimum replicas for the affected service and tune in a non-production lane. |

## Examples

Run an approved staging canary with an explicit resource limit, then compare it to
the baseline before touching production:

```bash
kubectl -n inference-staging patch deployment summarizer \
  --type merge -p '{"spec":{"template":{"spec":{"containers":[{"name":"server","resources":{"limits":{"nvidia.com/gpu":1}}}]}}}}'
kubectl -n inference-staging rollout status deployment/summarizer --timeout=10m
```

If p95 latency, error rate, or evaluation quality crosses the signed threshold,
restore the prior manifest and attach the redacted measurements to the change record.

## Resources

- [CoreWeave Pricing](https://www.coreweave.com/pricing)
- [CoreWeave GPU Instances](https://docs.coreweave.com/docs/platform/instances/gpu-instances)

## Next Steps

For architecture patterns, see `coreweave-reference-architecture`.
