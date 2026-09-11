---
name: cohere-hello-world
description: >-
  Run bounded Cohere v2 Chat, Embed, or Rerank requests with current model discovery and explicit validation. Use when proving a new Cohere setup. Trigger with "Cohere hello world", "Cohere quickstart", or "test Cohere API".
argument-hint: "[chat|embed|rerank] [typescript|python]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- cohere
- quickstart
model: inherit
effort: high
compatibility: Designed for Claude Code; live verification requires network access and an approved Cohere API key
---
# Cohere Bounded First Request

## Overview

Prove one selected endpoint end to end while keeping model choice, input type, output bounds, and evidence explicit.

## Prerequisites

- The target repository, runtime, environment, and accountable owner
- An approved Cohere team and key for any live verification
- Current quality, security, privacy, capacity, and change-control requirements

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect code, configuration, and evidence. Use `WebFetch` only for current Cohere primary documentation. Use `Write` or `Edit` only when the user requested implementation and the exact target files are known; never write credentials or customer content.

## Current Contract

- Discover a live model for the intended endpoint before pinning it.
- Chat v2 accepts a `messages` array and returns content under the response message.
- Embed v2 requires `input_type` and `embedding_types`; use `search_document` for indexed passages and `search_query` for queries.
- Rerank v2 orders supplied documents; select `rerank-v4.0-pro` for quality or `rerank-v4.0-fast` for measured latency needs.

## Authentication

Use an environment-specific key injected from an approved secret manager. Never print, persist, commit, or place `CO_API_KEY` in an example. Confirm access with the least costly bounded operation appropriate to the task, and treat key creation, rotation, revocation, role changes, and production-capacity requests as owner-approved actions.

## Instructions

1. Confirm authentication with `cohere-install-auth` and choose exactly one endpoint.
2. Resolve a live model from the catalog or Models API and record the resolved ID.
3. Use a non-sensitive, tiny fixture and set explicit output or result bounds.
4. Issue one v2 request and capture status, latency, model, billed-unit metadata when available, and response shape.
5. Validate non-empty Chat content, expected embedding dimensions, or monotonic Rerank ordering.
6. Return the minimal reproducible request with credentials redacted.

## Approval Boundaries

Do not expose or rotate keys, change Cohere Team roles, accept commercial terms, enable sensitive production data, increase spend or capacity, switch production models, send a support bundle, or execute model-proposed side effects without the accountable owner's approval. Keep diagnosis read-only unless implementation was requested.

## Output

Return the resolved API and model contract, files or settings inspected, evidence collected, validation result, remaining risk, owner, and rollback or next action. Redact keys, authorization headers, prompts, retrieved documents, embeddings, customer identifiers, and unrestricted environment output.

## Error Handling

| Condition | Response |
|---|---|
| `400` | Check required v2 fields and endpoint-specific input types. |
| `401` | Re-run the read-only authentication probe. |
| `404` model | Resolve an accessible live model instead of guessing an alias. |
| `429` | Honor the endpoint limit and stop the smoke test. |

## Examples

Use this compact handoff shape to keep the selected scope, validation evidence, and operational result reviewable.

Input:

```text
endpoint=embed; input=two-public-sentences; model=resolve-live; max-requests=1
```

Expected handoff:

```text
endpoint=embed-v2; model=resolved-id; vectors=2; validation=pass
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Chat API](https://docs.cohere.com/reference/chat)
- [Embed API](https://docs.cohere.com/reference/embed)
