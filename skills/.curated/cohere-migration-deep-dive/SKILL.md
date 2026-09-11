---
name: cohere-migration-deep-dive
description: >-
  Migrate an application to or from Cohere with a provider adapter, parallel embedding index, quality evaluation, canary traffic, and rollback. Use when changing model providers. Trigger with "migrate to Cohere", "replace OpenAI with Cohere", or "Cohere replatform".
argument-hint: "[source-provider] [target-provider] [workload]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- cohere
- provider-migration
model: inherit
effort: high
compatibility: Designed for Claude Code; live verification requires network access and an approved Cohere API key
---
# Cohere Provider Migration

## Overview

Treat provider migration as a semantic and operational change, not a search-and-replace of SDK calls.

## Prerequisites

- The target repository, runtime, environment, and accountable owner
- An approved Cohere team and key for any live verification
- Current quality, security, privacy, capacity, and change-control requirements

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect code, configuration, and evidence. Use `WebFetch` only for current Cohere primary documentation. Use `Write` or `Edit` only when the user requested implementation and the exact target files are known; never write credentials or customer content.

## Current Contract

- Cohere offers native v2 SDKs and an OpenAI compatibility API, but the compatibility surface omits Cohere-specific features.
- Chat messages, tool schemas, citations, safety controls, usage fields, errors, and stream events require explicit mapping.
- Embedding model changes require a parallel index because vectors from different contracts are not interchangeable.
- Model identifiers, limits, prices, and availability must be resolved for the target environment.

## Authentication

Use an environment-specific key injected from an approved secret manager. Never print, persist, commit, or place `CO_API_KEY` in an example. Confirm access with the least costly bounded operation appropriate to the task, and treat key creation, rotation, revocation, role changes, and production-capacity requests as owner-approved actions.

## Instructions

1. Inventory provider calls, prompts, tools, embeddings, indexes, streaming, errors, budgets, and user-visible quality.
2. Define a provider-neutral application port and golden evaluation set before implementing the target adapter.
3. Map supported semantics and record every incompatibility, especially citations, tools, safety, and structured output.
4. Build a parallel target embedding index with versioned model and dimension metadata.
5. Shadow or canary representative traffic and compare quality, latency, errors, throttling, and cost.
6. Cut over gradually, retain rollback through the observation window, and retire old keys and indexes only after approval.

## Approval Boundaries

Do not expose or rotate keys, change Cohere Team roles, accept commercial terms, enable sensitive production data, increase spend or capacity, switch production models, send a support bundle, or execute model-proposed side effects without the accountable owner's approval. Keep diagnosis read-only unless implementation was requested.

## Output

Return the resolved API and model contract, files or settings inspected, evidence collected, validation result, remaining risk, owner, and rollback or next action. Redact keys, authorization headers, prompts, retrieved documents, embeddings, customer identifiers, and unrestricted environment output.

## Error Handling

| Condition | Response |
|---|---|
| Compatibility gap | Use the native Cohere API or redesign explicitly; do not silently drop behavior. |
| Vector mixing | Stop and route queries only to the matching versioned index. |
| Tool mismatch | Add schema and approval contract tests before canarying. |
| Regression | Roll back traffic and preserve both evidence sets. |

## Examples

Use this compact handoff shape to keep the selected scope, validation evidence, and operational result reviewable.

Input:

```text
from=openai; to=cohere-v2; workload=enterprise-rag; canary=5%
```

Expected handoff:

```text
adapter=complete; index=parallel; eval=pass; rollback=retained
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [OpenAI compatibility](https://docs.cohere.com/docs/compatibility-api)
- [Model catalog](https://docs.cohere.com/docs/models)
