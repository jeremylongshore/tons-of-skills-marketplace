---
name: together-cost-tuning
description: >-
  Reduce Together AI spend using measured token usage, live per-model prices, cached-input evidence, batch discounts, model evaluation, and dedicated break-even analysis. Use when forecasting or optimizing Together workloads. Trigger with "Together cost", "optimize Together spend", or "Together batch savings".
argument-hint: "[repository-path] [usage-window] [budget]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.9.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- together-ai
- cost-optimization
model: inherit
effort: high
compatibility: Designed for Claude Code; current estimates require Together AI pricing and usage data
---
# Together AI Cost Tuning

## Overview

This skill builds a reproducible cost model from actual usage and current pricing rather than embedding a price table that will drift.

## Prerequisites

- A representative usage window with input, cached-input, output, and request counts
- Current model catalog/pricing and billing analytics access
- Quality, latency, context, and availability requirements
- A monthly budget and an owner for model or capacity changes

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to find model selection, token bounds, caching, batch, and telemetry logic. Use `WebFetch` only for current official pricing and eligibility. Use `Write` or `Edit` for an approved cost model, instrumentation, or configuration change.

## Current Contract

- Serverless models bill from current per-model input/output rates; some expose discounted cached input.
- Eligible batch work can cost up to 50% less, but eligibility and discount vary by model.
- Dedicated Model Inference bills per minute per running replica and hardware, not per token.
- Usage and prices change; snapshot retrieval time and source with every forecast.

## Authentication

Billing and usage views require authorized Together project access. API workloads use `TOGETHER_API_KEY`; record aggregate usage and project alias only, not the credential or sensitive request content.

## Instructions

1. Group measured requests by model, workload, token class, latency, and success state.
2. Fetch current pricing and batch eligibility, recording retrieval time and source.
3. Reconcile calculated cost with Together billing analytics before proposing savings.
4. Evaluate output bounds, prompt reuse/caching, smaller models, and asynchronous batch in that order.
5. Benchmark quality and latency before shifting models or endpoint type.
6. Compare steady utilization with dedicated per-minute capacity, then publish forecast, risk, rollback, and owner.

## Approval Boundaries

Do not change a production model, reduce quality/safety controls, submit batch jobs, or provision dedicated replicas solely from a spreadsheet estimate.

## Output

Return source-stamped prices, usage baseline, reconciled cost, option-by-option savings, quality/latency evidence, break-even assumptions, recommendation, and rollback.

## Error Handling

| Condition | Response |
|---|---|
| Usage lacks token fields | Add measurement before estimating savings. |
| Catalog and invoice diverge | Use billed data for history and current catalog for forward scenarios. |
| Batch model ineligible | Price synchronous or another explicitly tested model. |
| Dedicated utilization uncertain | Run a bounded capacity test; do not provision from peak guesses. |

## Examples

The example below shows the minimum redacted evidence expected from a successful invocation of this operator workflow.

```text
baseline=reconciled; prices=live-snapshot; option=batch; savings=modeled; quality=gate-required
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Serverless models and pricing](https://docs.together.ai/docs/serverless/models)
- [Usage and cost analytics](https://docs.together.ai/docs/billing-usage-limits)
- [Batch overview](https://docs.together.ai/docs/inference/batch/overview)
