---
name: together-rate-limits
description: >-
  Analyze and control Together AI serverless concurrency from dynamic per-model request/token headers, bounded queues, jittered retries, and batch or dedicated alternatives. Use when preventing throttling or sizing inference traffic. Trigger with "Together rate limit", "Together 429", or "Together concurrency control".
argument-hint: "[repository-path] [model-id] [traffic-profile]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.9.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- together-ai
- rate-limits
model: inherit
effort: high
compatibility: Designed for Claude Code; measurement requires authorized Together AI serverless responses
---
# Together AI Dynamic Rate Limits

## Overview

This skill replaces fixed quota tables with adaptive control driven by Together's current response headers and observed workload demand.

## Prerequisites

- The exact model IDs and traffic profile by request and token volume
- Access to response headers from the HTTP or SDK transport
- Queue-latency, retry, spend, and failure budgets
- A decision owner for batch, provisioned, or dedicated capacity

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to locate concurrency, queue, retry, and telemetry code. Use `WebFetch` for the current dynamic-limit header contract. Use `Write` or `Edit` only after the target limiter and tests are identified.

## Current Contract

- Serverless limits are dynamic per organization and model; historical account tiers are retired.
- Read request and token limit/remaining/reset headers on every response and maintain state per model.
- Treat displayed RPM as a per-second enforcement budget when Together documents that conversion.
- Use batch for delay-tolerant bursts and dedicated capacity for predictable reserved throughput.

## Authentication

Limit headers arrive on authenticated serverless inference responses using the project-scoped Bearer key. Record numeric headers and model alias only; never retain the credential or sensitive body.

## Instructions

1. Inventory callers, models, concurrency, token sizes, queue depth, and existing retries.
2. Capture the current `x-ratelimit-*` and `x-tokenlimit-*` fields from redacted responses.
3. Build independent request and token budgets keyed by model and organization context.
4. Admit work through a bounded queue; reserve headroom for retries and interactive traffic.
5. On `429`, honor reset evidence, apply jitter, and stop at the request deadline.
6. Load-test below approval bounds, then choose serverless, batch, or dedicated capacity from measured demand.

## Approval Boundaries

Do not manufacture fixed limits, increase retry concurrency after throttling, or move to paid reserved hardware without explicit cost and capacity approval.

## Output

Return observed headers, per-model limiter settings, queue/retry budgets, load-test evidence, dropped/deferred work, and capacity recommendation.

## Error Handling

| Condition | Response |
|---|---|
| Limit headers missing | Fall back conservatively and surface transport visibility as a blocker. |
| `429` persists | Reduce concurrency; do not multiply retries. |
| Queue deadline exceeded | Fail or defer according to workload policy. |
| Bursts dominate | Evaluate Batch API rather than chasing serverless limits. |

## Examples

The example below shows the minimum redacted evidence expected from a successful invocation of this operator workflow.

```text
model=catalog-id; limits=header-derived; queue=bounded; retry=jittered; overflow=batch-candidate
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Serverless rate limits](https://docs.together.ai/docs/serverless/rate-limits)
- [Usage limits and analytics](https://docs.together.ai/docs/billing-usage-limits)
- [Batch overview](https://docs.together.ai/docs/inference/batch/overview)
