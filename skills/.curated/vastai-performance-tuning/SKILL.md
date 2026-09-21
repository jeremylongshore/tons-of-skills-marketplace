---
name: vastai-performance-tuning
description: >-
  Tune Vast.ai offer selection, startup, data feeding, GPU memory, and scaling from measured useful-work throughput. Use when jobs are slow, GPUs are underutilized, or faster offers cost more. Trigger with: "tune Vast.ai performance", "improve GPU utilization", "compare Vast.ai throughput".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[workload-benchmark-and-slo]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - vastai
  - performance
  - gpu
  - benchmarking
compatibility: 'Requires a representative benchmark, structured offer data, GPU telemetry, immutable images, and a cost objective.'
---

# Vast.ai Useful-Work Performance Tuning

## Overview

Provider benchmark fields help shortlist offers but do not replace workload measurement. Tune one bottleneck at a time and compare completed-work latency, throughput, reliability, and total cost on immutable workload bytes.

## Prerequisites

- Representative input, warm-up, sample count, correctness assertion, and target SLO
- Pinned code/image/model plus candidate GPU, VRAM, host, network, and disk profiles
- Baseline throughput, utilization, memory, startup time, and useful-work cost

## Instructions

### Step 1: Build the baseline

Measure end-to-end completion, startup, data wait, GPU utilization, memory, errors, and cost on the current profile.

### Step 2: Shortlist offers

Use verified, rentable, reliability, CUDA, network, `dlperf`, and `dlperf_usd` fields to select comparable candidates without weakening workload constraints.

### Step 3: Remove startup waste

Pin a smaller prebuilt image, avoid runtime package installs, and measure pull plus readiness separately from execution.

### Step 4: Tune the data path

Stage hot data on suitable local storage, increase loaders or prefetch only from evidence, and watch bandwidth and disk cost.

### Step 5: Tune compute and memory

Adjust batch, precision, accumulation, kernel, and multi-GPU strategy one variable at a time while preserving output correctness.

### Step 6: Choose by useful work

Select the profile that meets the SLO at the best total cost per accepted unit, then destroy all benchmark instances.

## Authentication

Benchmark automation needs search and instance permissions only. Keep datasets, model tokens, and registry credentials separate and scoped to the benchmark.

## Tool Discipline

Use Read and Grep to inspect manifests, configuration, provider output, and existing tests before proposing a mutation. Use Write or Edit only for the approved plan, implementation, test, or redacted receipt; do not create, update, destroy, or fund Vast.ai resources without explicit operator approval.

## Output

- Reproducible baseline and candidate benchmark manifest
- Bottleneck attribution and one-variable experiment results
- Selected profile with SLO, cost, correctness, and cleanup evidence

Return workload identity, candidates, sample counts, throughput, latency, utilization, cost per accepted unit, decision, and destroyed instance IDs.

## Examples

Two RTX 4090 offers with different `dlperf_usd` are tested on the same digest and dataset sample; the faster headline offer is rejected when startup and bandwidth make completed-batch cost worse.

## Error Handling

| Failure | Response |
| --- | --- |
| Outputs differ across candidates | Treat the benchmark as invalid until correctness is restored. |
| Only provider `dlperf` is available | Label the decision provisional and run the workload benchmark. |
| GPU utilization is low but data wait is high | Fix the input path before buying a faster GPU. |
| Benchmark instances remain | Stop analysis and close the active cost leak. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Search offers](https://docs.vast.ai/cli/reference/search-offers)
- [Instance pricing](https://docs.vast.ai/guides/instances/pricing)
- [Serverless automated performance testing](https://docs.vast.ai/guides/serverless/automated-performance-testing)
