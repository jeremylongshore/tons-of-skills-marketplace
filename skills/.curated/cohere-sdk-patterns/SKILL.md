---
name: cohere-sdk-patterns
description: >-
  Implement a typed Cohere v2 provider boundary with timeouts, bounded retries, streaming, and response validation. Use when standardizing production SDK usage. Trigger with "Cohere SDK patterns", "Cohere client wrapper", or "refactor Cohere client".
argument-hint: "[repository-path] [typescript|python]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- cohere
- sdk
model: inherit
effort: high
compatibility: Designed for Claude Code; live verification requires network access and an approved Cohere API key
---
# Cohere SDK Integration Patterns

## Overview

Wrap generated SDK clients behind a small application contract so model changes, provider errors, and migrations stay localized.

## Prerequisites

- The target repository, runtime, environment, and accountable owner
- An approved Cohere team and key for any live verification
- Current quality, security, privacy, capacity, and change-control requirements

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect code, configuration, and evidence. Use `WebFetch` only for current Cohere primary documentation. Use `Write` or `Edit` only when the user requested implementation and the exact target files are known; never write credentials or customer content.

## Current Contract

- Instantiate one configured v2 client per runtime process unless tenancy requires a separate credential boundary.
- Require callers to supply an operation purpose, bounded timeout, and resolved model ID.
- Retry only transient transport, `429`, and eligible `5xx` failures with jitter and a total-attempt ceiling.
- Normalize Chat content, citations, tool calls, Embed vectors, Rerank scores, usage, and provider request metadata at the boundary.

## Authentication

Use an environment-specific key injected from an approved secret manager. Never print, persist, commit, or place `CO_API_KEY` in an example. Confirm access with the least costly bounded operation appropriate to the task, and treat key creation, rotation, revocation, role changes, and production-capacity requests as owner-approved actions.

## Instructions

1. Inventory current direct SDK calls and group them by Chat, Embed, Rerank, and model discovery.
2. Define typed request and result contracts that expose only application-required fields.
3. Centralize timeout, redaction, retry eligibility, and model resolution.
4. Implement streaming as an async iterator with cancellation and terminal-event validation.
5. Add contract fixtures for success, partial stream, timeout, limit, and schema drift.
6. Migrate one call site at a time and delete direct SDK access only after parity tests pass.

## Approval Boundaries

Do not expose or rotate keys, change Cohere Team roles, accept commercial terms, enable sensitive production data, increase spend or capacity, switch production models, send a support bundle, or execute model-proposed side effects without the accountable owner's approval. Keep diagnosis read-only unless implementation was requested.

## Output

Return the resolved API and model contract, files or settings inspected, evidence collected, validation result, remaining risk, owner, and rollback or next action. Redact keys, authorization headers, prompts, retrieved documents, embeddings, customer identifiers, and unrestricted environment output.

## Error Handling

| Condition | Response |
|---|---|
| Unknown event | Preserve it in diagnostics and fail the affected stream safely. |
| Retry storm | Enforce jitter, an attempt ceiling, and a shared concurrency budget. |
| Type drift | Update the adapter against the pinned SDK and add a fixture. |
| Empty content | Treat it as an invalid result unless the operation expected tool calls. |

## Examples

Use this compact handoff shape to keep the selected scope, validation evidence, and operational result reviewable.

Input:

```text
operations=chat,embed,rerank; timeout=15s; retries=2; stream-cancel=true
```

Expected handoff:

```text
adapter=typed; direct-sdk-calls=0; fixtures=pass; retry-budget=bounded
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [TypeScript SDK](https://github.com/cohere-ai/cohere-typescript)
- [Python SDK](https://github.com/cohere-ai/cohere-python)
