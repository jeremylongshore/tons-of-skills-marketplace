---
name: cohere-observability
description: >-
  Instrument Cohere requests, streams, retrieval, tools, limits, quality, and cost with low-cardinality telemetry and safe traces. Use when monitoring a Cohere service. Trigger with "Cohere observability", "Cohere metrics", or "monitor Cohere".
argument-hint: "[service] [telemetry-backend]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- cohere
- observability
model: inherit
effort: high
compatibility: Designed for Claude Code; live verification requires network access and an approved Cohere API key
---
# Cohere Observability

## Overview

Expose enough evidence to separate application, retrieval, model, capacity, and provider failures without logging credentials or customer content.

## Prerequisites

- The target repository, runtime, environment, and accountable owner
- An approved Cohere team and key for any live verification
- Current quality, security, privacy, capacity, and change-control requirements

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect code, configuration, and evidence. Use `WebFetch` only for current Cohere primary documentation. Use `Write` or `Edit` only when the user requested implementation and the exact target files are known; never write credentials or customer content.

## Current Contract

- Measure queue, retrieval, provider, first-event, completion, and tool durations separately.
- Label metrics with bounded dimensions such as endpoint, operation, resolved model, environment, outcome, and retry class.
- Keep prompts, documents, embeddings, keys, and raw tool arguments out of telemetry by default.
- Pair operational metrics with sampled quality, citation, and safety evaluations.

## Authentication

Use an environment-specific key injected from an approved secret manager. Never print, persist, commit, or place `CO_API_KEY` in an example. Confirm access with the least costly bounded operation appropriate to the task, and treat key creation, rotation, revocation, role changes, and production-capacity requests as owner-approved actions.

## Instructions

1. Define service objectives and an allowlist of telemetry fields before instrumenting.
2. Create counters for requests, outcomes, retries, throttles, circuit transitions, and tool decisions.
3. Create histograms for queue, retrieval, provider, first-event, completion, and end-to-end duration.
4. Record usage and cost units without tenant names or unbounded request IDs as metric labels.
5. Build alerts for availability, sustained throttling, queue age, latency, quality, and spend.
6. Test redaction, trace propagation, stream cancellation, and incident correlation.

## Approval Boundaries

Do not expose or rotate keys, change Cohere Team roles, accept commercial terms, enable sensitive production data, increase spend or capacity, switch production models, send a support bundle, or execute model-proposed side effects without the accountable owner's approval. Keep diagnosis read-only unless implementation was requested.

## Output

Return the resolved API and model contract, files or settings inspected, evidence collected, validation result, remaining risk, owner, and rollback or next action. Redact keys, authorization headers, prompts, retrieved documents, embeddings, customer identifiers, and unrestricted environment output.

## Error Handling

| Condition | Response |
|---|---|
| Cardinality spike | Remove unbounded labels and aggregate request identifiers in logs only. |
| Prompt in trace | Redact it and review retained telemetry as a data incident. |
| Missing terminal event | Mark the stream incomplete and count a distinct outcome. |
| False provider alert | Split local queue/retrieval time from Cohere duration. |

## Examples

Use this compact handoff shape to keep the selected scope, validation evidence, and operational result reviewable.

Input:

```text
service=rag-api; backend=otel; content-logging=off; quality-sampling=1%
```

Expected handoff:

```text
metrics=bounded; traces=redacted; slo=defined; alerts=tested
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Cohere status](https://status.cohere.com)
- [Error reference](https://docs.cohere.com/reference/errors)
