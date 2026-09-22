---
name: cohere-performance-tuning
description: >-
  Measure and improve Cohere latency, throughput, retrieval quality, streaming, batching, and vector representation without fabricated benchmarks. Use when optimizing a Cohere workload. Trigger with "Cohere performance", "Cohere latency", or "optimize Cohere".
argument-hint: "[endpoint] [latency|throughput|quality]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- cohere
- performance
model: inherit
effort: high
compatibility: Designed for Claude Code; live verification requires network access and an approved Cohere API key
---
# Cohere Performance Tuning

## Overview

Tune from workload-specific measurements and representative quality thresholds rather than copying universal latency numbers or synthetic benchmark claims.

## Prerequisites

- The target repository, runtime, environment, and accountable owner
- An approved Cohere team and key for any live verification
- Current quality, security, privacy, capacity, and change-control requirements

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect code, configuration, and evidence. Use `WebFetch` only for current Cohere primary documentation. Use `Write` or `Edit` only when the user requested implementation and the exact target files are known; never write credentials or customer content.

## Current Contract

- Resolve models and their current context and output limits from the live catalog.
- Measure Chat time to first event and completion separately from application queue and retrieval time.
- Batch Embed inputs within documented request constraints and track inputs per minute.
- Choose Rerank v4 pro or fast from measured relevance and latency on representative queries.

## Authentication

Use an environment-specific key injected from an approved secret manager. Never print, persist, commit, or place `CO_API_KEY` in an example. Confirm access with the least costly bounded operation appropriate to the task, and treat key creation, rotation, revocation, role changes, and production-capacity requests as owner-approved actions.

## Instructions

1. Define a representative workload, quality floor, latency objective, concurrency, and cost ceiling.
2. Instrument queue, retrieval, provider, first-event, completion, and post-processing durations.
3. Establish a cold and warm baseline with fixed inputs and resolved model IDs.
4. Test one variable at a time: model, context size, output bound, stream mode, Embed batch size, Rerank candidate count, or cache.
5. Reject changes that improve speed while violating quality, citation, safety, or cost thresholds.
6. Record the selected configuration, confidence interval, capacity headroom, and rollback trigger.

## Approval Boundaries

Do not expose or rotate keys, change Cohere Team roles, accept commercial terms, enable sensitive production data, increase spend or capacity, switch production models, send a support bundle, or execute model-proposed side effects without the accountable owner's approval. Keep diagnosis read-only unless implementation was requested.

## Output

Return the resolved API and model contract, files or settings inspected, evidence collected, validation result, remaining risk, owner, and rollback or next action. Redact keys, authorization headers, prompts, retrieved documents, embeddings, customer identifiers, and unrestricted environment output.

## Error Handling

| Condition | Response |
|---|---|
| Benchmark variance | Increase repetitions and separate cold, warm, and throttled samples. |
| Quality loss | Revert the optimization even if latency improves. |
| `429` during test | Lower concurrency and exclude throttled samples from normal latency claims. |
| Cache leak | Include tenant, model, input type, policy, and version in cache keys. |

## Examples

Use this compact handoff shape to keep the selected scope, validation evidence, and operational result reviewable.

Input:

```text
endpoint=rerank; candidates=100; objective=p95; quality=ndcg-threshold
```

Expected handoff:

```text
variant=rerank-v4-fast; quality=pass; p95=measured; headroom=recorded
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Model catalog](https://docs.cohere.com/docs/models)
- [Rerank models](https://docs.cohere.com/docs/rerank)
