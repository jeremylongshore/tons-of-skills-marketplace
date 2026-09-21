---
name: quicknode-performance-tuning
description: 'Tune QuickNode RPC performance from endpoint metrics, method mix, payload size, connection reuse, and chain semantics instead of synthetic request counts. Use when tail latency, errors, or credit use regress. Trigger with: "optimize QuickNode latency", "analyze QuickNode p95", "reduce RPC response time".'
allowed-tools: Read, Grep, Write, Edit, Bash(qn:*)
version: 2.0.0
argument-hint: '[endpoint-id-and-slo]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - quicknode
  - performance
  - metrics
  - rpc
compatibility: 'Metrics availability depends on plan; method behavior and safe batching vary by chain'
---

# QuickNode Performance Tuning

## Overview

Optimize against a declared service-level objective and QuickNode's endpoint metrics. Separate provider latency from client queueing, chain execution, payload transfer, and downstream decoding.

## Prerequisites

- Endpoint ID, chain, network, and latency/error SLO
- A representative method and payload workload
- Access to endpoint metrics or an application-side measurement source

## Instructions

### Step 1: Establish a baseline

Use Read and Grep to find timeouts, concurrency, connection pools, retries, batch settings, and method mix. Measure end-to-end and provider-call latency separately.

### Step 2: Read provider metrics

Use Bash(qn:*) for authenticated endpoint metrics, including method calls, response codes, chain errors, and supported percentile views. Keep the time range and percentile explicit.

### Step 3: Segment the workload

Compare method, network, payload size, block age, cacheability, and protocol. Historical traces and large log ranges must not be averaged with a small latest-block read.

### Step 4: Remove avoidable work

Use Write or Edit to reuse connections and configured clients, coalesce identical reads, cache immutable block results, paginate large ranges, and request only necessary fields where the API supports it.

### Step 5: Control concurrency

Set a bounded in-flight limit below measured saturation. Use JSON-RPC batching only where the chain and client contract support it, and cap both batch count and response size.

### Step 6: Validate the change

Replay the same workload and compare p50, p95, p99, error rate, credits, and application queue time. Roll back if tail latency or chain-error rates worsen even when the mean improves.

## Tool Discipline

Use Read and Grep for code and configuration discovery, Bash(qn:*) for read-only metrics, and Write/Edit for bounded performance changes and tests. Do not change production capacity or rate limits implicitly.

## Output

- Layered baseline and SLO
- Method-segmented bottleneck finding
- One controlled optimization
- Before/after percentile, error, and credit receipt

## Examples

A logs query dominates p99 and payload bytes. The service narrows block ranges and paginates that method while leaving fast latest-block reads unchanged.

## Error Handling

| Failure | Response |
| --- | --- |
| Metrics unavailable | Use application timings and document the plan limitation |
| Average improves but p99 worsens | Reject or isolate the change |
| Batch response grows unbounded | Cap batch and payload size |
| Retries increase load | Open the circuit and revisit the root error class |

## Resources

- [Performance evidence and source notes](references/official-docs.md)
- [Endpoint metrics API](https://www.quicknode.com/docs/admin-api/endpoint-metrics/v0-endpoints-id-metrics)
- [QuickNode dashboard metrics](https://www.quicknode.com/guides/quicknode-products/how-to-use-the-quicknode-dashboard)
