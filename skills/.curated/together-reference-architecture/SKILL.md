---
name: together-reference-architecture
description: >-
  Design a production Together AI service with a typed provider boundary, policy-based model routing, serverless and dedicated lanes, batch workers, telemetry, budgets, and reversible degradation. Use when defining the integration topology. Trigger with "Together architecture", "Together model gateway", or "design Together service".
argument-hint: "[repository-path] [workload-profile]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.9.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- together-ai
- architecture
model: inherit
effort: high
compatibility: Designed for Claude Code; implementation may require cloud, queue, secret-store, and Together AI access
---
# Together AI Reference Architecture

## Overview

This skill turns workload requirements into explicit real-time, batch, and dedicated paths with one governed provider boundary and observable cost/quality behavior.

## Prerequisites

- Workload classes, modalities, volumes, latency objectives, and data classifications
- Model-quality evaluations and fallback constraints
- Availability, cost, retention, residency, and recovery objectives
- Existing gateway, queue, telemetry, and secret-management topology

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to map callers, trust boundaries, queues, storage, and observability. Use `WebFetch` for current Together capabilities and limits. Use `Write` or `Edit` only for approved diagrams, ADRs, interfaces, or configuration.

## Current Contract

- Interactive serverless and dedicated models share inference request shapes, but capacity and billing differ.
- Batch is an asynchronous file/job path with arbitrary result order and separate error artifacts.
- Model IDs, prices, redirects, and availability are runtime policy inputs, not constants scattered through callers.
- Credentials are project-scoped; isolate environments and inject keys at the gateway or worker boundary.

## Authentication

Use separate `TOGETHER_API_KEY` references per environment and workload authority. Keep provider credentials server-side. Internal callers authenticate to the application gateway independently; they never receive the Together key.

## Instructions

1. Partition workloads into interactive, offline batch, training, and reserved-capacity classes.
2. Define a typed provider adapter and policy service for model, bounds, fallback, and deprecation state.
3. Place bounded queues around bursty and asynchronous work with durable IDs and reconciliation.
4. Add per-model request/token control, circuit breaking, usage/cost telemetry, and quality sampling.
5. Define data redaction, retention, tenant isolation, and secret rotation at each trust boundary.
6. Document degradation, model migration, batch recovery, dedicated scale-to-zero, and provider-exit paths.

## Approval Boundaries

Do not introduce provider failover, cross-region data movement, dedicated capacity, or automatic model substitution without security, quality, reliability, and cost owners.

## Output

Return component/flow topology, trust boundaries, provider interfaces, model policy, capacity lanes, observability, budgets, failure modes, rollback, and decision owners.

## Error Handling

| Condition | Response |
|---|---|
| Requirements conflict | Record the tradeoff and seek the named decision owner. |
| Provider unavailable | Apply bounded circuit/degradation policy; do not retry indefinitely. |
| Model deprecated | Route through evaluated migration policy, not an ad hoc replacement. |
| Batch partially fails | Reconcile by ID and retry only approved failed records. |

## Examples

The example below shows the minimum redacted evidence expected from a successful invocation of this operator workflow.

```text
interactive=serverless-gateway; offline=batch-worker; reserved=dedicated-v2; secrets=per-environment
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Inference overview](https://docs.together.ai/docs/inference/overview)
- [Batch overview](https://docs.together.ai/docs/inference/batch/overview)
- [Dedicated Model Inference](https://docs.together.ai/docs/dedicated-endpoints/overview)
