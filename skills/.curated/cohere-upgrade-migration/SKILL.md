---
name: cohere-upgrade-migration
description: >-
  Migrate Cohere API v1 or older SDK usage to v2 with contract tests, model lifecycle checks, canarying, and rollback. Use when upgrading Cohere dependencies or endpoints. Trigger with "Cohere v1 to v2", "upgrade Cohere SDK", or "Cohere deprecation".
argument-hint: "[repository-path] [from-version] [to-version]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- cohere
- migration
model: inherit
effort: high
compatibility: Designed for Claude Code; live verification requires network access and an approved Cohere API key
---
# Cohere API and SDK Upgrade

## Overview

Inventory legacy behavior, move through the documented v2 contract, and prove semantic parity before removing rollback paths.

## Prerequisites

- The target repository, runtime, environment, and accountable owner
- An approved Cohere team and key for any live verification
- Current quality, security, privacy, capacity, and change-control requirements

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect code, configuration, and evidence. Use `WebFetch` only for current Cohere primary documentation. Use `Write` or `Edit` only when the user requested implementation and the exact target files are known; never write credentials or customer content.

## Current Contract

- V2 uses `messages` instead of separate message, preamble, and managed conversation history fields.
- V2 requires explicit models; Embed also requires embedding types.
- V2 tools use JSON Schema and correlate results with tool-call IDs.
- Legacy Generate, Summarize, Classify, managed connectors, selected models, and fine-tuning paths appear on Cohere's deprecation schedule.

## Authentication

Use an environment-specific key injected from an approved secret manager. Never print, persist, commit, or place `CO_API_KEY` in an example. Confirm access with the least costly bounded operation appropriate to the task, and treat key creation, rotation, revocation, role changes, and production-capacity requests as owner-approved actions.

## Instructions

1. Inventory SDK versions, endpoints, parameters, models, stream events, connectors, fine-tunes, and response parsing.
2. Read the current migration and deprecation pages and classify each dependency as live, legacy, deprecated, or shut down.
3. Add golden contract tests around current user-visible behavior and failure paths.
4. Introduce the v2 client and provider adapter while retaining a feature-flagged rollback path.
5. Migrate request and response shapes, then reindex embeddings if their model contract changes.
6. Canary representative traffic, compare quality and operations, and remove v1 only after rollback criteria remain clear.

## Approval Boundaries

Do not expose or rotate keys, change Cohere Team roles, accept commercial terms, enable sensitive production data, increase spend or capacity, switch production models, send a support bundle, or execute model-proposed side effects without the accountable owner's approval. Keep diagnosis read-only unless implementation was requested.

## Output

Return the resolved API and model contract, files or settings inspected, evidence collected, validation result, remaining risk, owner, and rollback or next action. Redact keys, authorization headers, prompts, retrieved documents, embeddings, customer identifiers, and unrestricted environment output.

## Error Handling

| Condition | Response |
|---|---|
| Missing v2 feature | Use an application-owned tool or retain a time-bound v1 path if still supported. |
| Embedding drift | Build a parallel index and cut over atomically. |
| Stream parser fails | Update from legacy text events to typed v2 events. |
| Quality regression | Stop the canary and preserve the old model path. |

## Examples

Use this compact handoff shape to keep the selected scope, validation evidence, and operational result reviewable.

Input:

```text
from=Client-v1; to=ClientV2; endpoints=chat,embed; canary=10%
```

Expected handoff:

```text
contracts=pass; deprecated-calls=0; quality=within-threshold; rollback=ready
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [API v1 to v2](https://docs.cohere.com/docs/migrating-v1-to-v2)
- [Deprecations](https://docs.cohere.com/docs/deprecations)
