---
name: cohere-cost-tuning
description: >-
  Model and reduce Cohere usage cost with current pricing, measured token or search units, quality gates, caching, and budget controls. Use when forecasting or optimizing Cohere spend. Trigger with "Cohere cost", "Cohere pricing", or "Cohere budget".
argument-hint: "[workload] [monthly-volume] [currency]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- cohere
- cost
model: inherit
effort: high
compatibility: Designed for Claude Code; live verification requires network access and an approved Cohere API key
---
# Cohere Cost and Usage Tuning

## Overview

Build a reproducible cost model from live prices and measured workload units, then optimize only within approved quality and safety thresholds.

## Prerequisites

- The target repository, runtime, environment, and accountable owner
- An approved Cohere team and key for any live verification
- Current quality, security, privacy, capacity, and change-control requirements

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect code, configuration, and evidence. Use `WebFetch` only for current Cohere primary documentation. Use `Write` or `Edit` only when the user requested implementation and the exact target files are known; never write credentials or customer content.

## Current Contract

- Do not embed a permanent price table; capture the pricing page date and applicable commercial terms.
- Separate Chat input/output, Embed input, Rerank search, and platform infrastructure costs.
- Newer model access and production capacity can have account-specific terms.
- A cheaper model or smaller context is acceptable only after representative evaluation passes.

## Authentication

Use an environment-specific key injected from an approved secret manager. Never print, persist, commit, or place `CO_API_KEY` in an example. Confirm access with the least costly bounded operation appropriate to the task, and treat key creation, rotation, revocation, role changes, and production-capacity requests as owner-approved actions.

## Instructions

1. Collect current public prices or contracted rates with effective date and currency.
2. Measure per-request input, output, Embed, Rerank, retry, cache, and failure units by workload class.
3. Forecast baseline, expected, and peak volume with capacity and retry assumptions.
4. Evaluate model routing, context reduction, retrieval pruning, batching, caching, and duplicate suppression.
5. Set per-tenant and global budgets, alerts, admission controls, and an owner-approved degradation path.
6. Reconcile forecast with actual billing regularly and investigate material variance.

## Approval Boundaries

Do not expose or rotate keys, change Cohere Team roles, accept commercial terms, enable sensitive production data, increase spend or capacity, switch production models, send a support bundle, or execute model-proposed side effects without the accountable owner's approval. Keep diagnosis read-only unless implementation was requested.

## Output

Return the resolved API and model contract, files or settings inspected, evidence collected, validation result, remaining risk, owner, and rollback or next action. Redact keys, authorization headers, prompts, retrieved documents, embeddings, customer identifiers, and unrestricted environment output.

## Error Handling

| Condition | Response |
|---|---|
| Unknown contract rate | Mark the forecast incomplete and obtain the governing rate. |
| Quality below floor | Reject the savings change. |
| Retry amplification | Fix failure handling and include wasted units in the model. |
| Budget exceeded | Apply approved admission control; do not silently weaken safety. |

## Examples

Use this compact handoff shape to keep the selected scope, validation evidence, and operational result reviewable.

Input:

```text
workload=rag-chat; monthly-requests=100000; prices=effective-date-snapshot
```

Expected handoff:

```text
forecast=three-scenarios; unit-cost=measured; controls=enabled; quality=pass
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Pricing](https://cohere.com/pricing)
- [Rate limits](https://docs.cohere.com/docs/rate-limits)
