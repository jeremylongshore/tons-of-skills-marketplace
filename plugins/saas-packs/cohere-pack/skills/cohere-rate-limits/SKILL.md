---
name: cohere-rate-limits
description: >-
  Implement Cohere endpoint-aware throttling, bounded retry, and queue backpressure from current limits and observed responses. Use when handling 429s or planning throughput. Trigger with "Cohere rate limit", "Cohere throttling", or "Cohere 429".
argument-hint: "[endpoint] [evaluation|production] [target-rps]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- cohere
- rate-limits
model: inherit
effort: high
compatibility: Designed for Claude Code; live verification requires network access and an approved Cohere API key
---
# Cohere Rate-Limit Control

## Overview

Treat limits as a live per-key, endpoint, and model contract rather than a single permanent requests-per-minute number.

## Prerequisites

- The target repository, runtime, environment, and accountable owner
- An approved Cohere team and key for any live verification
- Current quality, security, privacy, capacity, and change-control requirements

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect code, configuration, and evidence. Use `WebFetch` only for current Cohere primary documentation. Use `Write` or `Edit` only when the user requested implementation and the exact target files are known; never write credentials or customer content.

## Current Contract

- The reviewed page lists Chat limits per model; several newer variants require contacting sales for production capacity.
- On the review date, Embed was expressed in inputs per minute, while Rerank was expressed in requests per minute.
- Trial usage includes a monthly cap, and production arrangements can vary.
- A successful load plan must measure actual account behavior and preserve headroom instead of copying a static table.

## Authentication

Use an environment-specific key injected from an approved secret manager. Never print, persist, commit, or place `CO_API_KEY` in an example. Confirm access with the least costly bounded operation appropriate to the task, and treat key creation, rotation, revocation, role changes, and production-capacity requests as owner-approved actions.

## Instructions

1. Identify key type, endpoint, resolved model, request batch size, and documented current limit.
2. Convert limits into request, input, and token budgets as applicable.
3. Apply a shared queue with bounded concurrency, jittered backoff, and a total retry deadline.
4. Honor provider retry guidance when present and stop retrying deterministic client errors.
5. Load test below the approved ceiling with non-sensitive fixtures and record saturation behavior.
6. Alert on sustained throttling, queue age, dropped work, and budget exhaustion.

## Approval Boundaries

Do not expose or rotate keys, change Cohere Team roles, accept commercial terms, enable sensitive production data, increase spend or capacity, switch production models, send a support bundle, or execute model-proposed side effects without the accountable owner's approval. Keep diagnosis read-only unless implementation was requested.

## Output

Return the resolved API and model contract, files or settings inspected, evidence collected, validation result, remaining risk, owner, and rollback or next action. Redact keys, authorization headers, prompts, retrieved documents, embeddings, customer identifiers, and unrestricted environment output.

## Error Handling

| Condition | Response |
|---|---|
| Repeated `429` | Reduce concurrency and inspect key/model-specific capacity. |
| Queue growth | Apply admission control instead of hiding overload with retries. |
| Mixed endpoints | Use separate budgets because units and limits differ. |
| Unknown limit | Run a conservative probe or contact Cohere; do not invent capacity. |

## Examples

Use this compact handoff shape to keep the selected scope, validation evidence, and operational result reviewable.

Input:

```text
endpoint=rerank; key=production; model=resolved; workload=interactive
```

Expected handoff:

```text
concurrency=measured; retry=bounded-jitter; headroom=20%; alerts=configured
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [API key types and limits](https://docs.cohere.com/docs/rate-limits)
- [Going live](https://docs.cohere.com/docs/going-live)
