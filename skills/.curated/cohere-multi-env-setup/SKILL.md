---
name: cohere-multi-env-setup
description: >-
  Configure Cohere development, staging, and production with separate keys, model resolution, budgets, and promotion evidence. Use when operating Cohere across environments. Trigger with "Cohere environments", "Cohere staging", or "Cohere dev prod setup".
argument-hint: "[repository-path] [dev|staging|production]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- cohere
- environments
model: inherit
effort: high
compatibility: Designed for Claude Code; live verification requires network access and an approved Cohere API key
---
# Cohere Multi-Environment Configuration

## Overview

Keep credentials and capacity isolated while promoting one versioned provider contract through increasingly production-like environments.

## Prerequisites

- The target repository, runtime, environment, and accountable owner
- An approved Cohere team and key for any live verification
- Current quality, security, privacy, capacity, and change-control requirements

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect code, configuration, and evidence. Use `WebFetch` only for current Cohere primary documentation. Use `Write` or `Edit` only when the user requested implementation and the exact target files are known; never write credentials or customer content.

## Current Contract

- Use separate keys or provider deployments per environment and never fall back from production to an evaluation key.
- Resolve model availability per environment because Cohere platform and cloud-provider IDs differ.
- Promote configuration references, not secret values.
- Keep evaluation fixtures synthetic or approved and align staging limits closely enough to expose production failure modes.

## Authentication

Use an environment-specific key injected from an approved secret manager. Never print, persist, commit, or place `CO_API_KEY` in an example. Confirm access with the least costly bounded operation appropriate to the task, and treat key creation, rotation, revocation, role changes, and production-capacity requests as owner-approved actions.

## Instructions

1. Inventory environments, accounts, teams, cloud platforms, keys, owners, and data classes.
2. Define a validated configuration schema for provider, base URL, model IDs, timeouts, retries, and budgets.
3. Store secrets in environment-specific managers and bind access to runtime identities.
4. Run the same offline contracts everywhere and a bounded provider probe only in trusted environments.
5. Promote resolved configuration through review with quality, capacity, and rollback evidence.
6. Continuously detect key reuse, model drift, missing budgets, and unauthorized configuration changes.

## Approval Boundaries

Do not expose or rotate keys, change Cohere Team roles, accept commercial terms, enable sensitive production data, increase spend or capacity, switch production models, send a support bundle, or execute model-proposed side effects without the accountable owner's approval. Keep diagnosis read-only unless implementation was requested.

## Output

Return the resolved API and model contract, files or settings inspected, evidence collected, validation result, remaining risk, owner, and rollback or next action. Redact keys, authorization headers, prompts, retrieved documents, embeddings, customer identifiers, and unrestricted environment output.

## Error Handling

| Condition | Response |
|---|---|
| Shared key | Create environment-specific credentials and rotate the shared value. |
| Model unavailable | Resolve the correct platform ID; do not silently switch models. |
| Config drift | Block promotion until the reviewed schema and deployment agree. |
| Trial key in production | Fail startup or readiness and escalate to the owner. |

## Examples

Use this compact handoff shape to keep the selected scope, validation evidence, and operational result reviewable.

Input:

```text
environments=dev,staging,prod; provider=cohere-platform; promote=config-only
```

Expected handoff:

```text
keys=separate; models=resolved; schema=validated; promotion=evidenced
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Create a client](https://docs.cohere.com/docs/create-client)
- [Cloud compatibility](https://docs.cohere.com/docs/cohere-works-everywhere/)
