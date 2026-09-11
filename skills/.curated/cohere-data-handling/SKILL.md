---
name: cohere-data-handling
description: >-
  Govern data sent to Cohere with classification, minimization, tenant controls, redaction, retention mapping, and contractual evidence. Use when processing sensitive or regulated data. Trigger with "Cohere privacy", "Cohere PII", or "Cohere data retention".
argument-hint: "[data-class] [jurisdiction] [environment]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- cohere
- privacy
model: inherit
effort: high
compatibility: Designed for Claude Code; live verification requires network access and an approved Cohere API key
---
# Cohere Data Handling and Privacy

## Overview

Decide what may cross the provider boundary from the signed agreement and application purpose, then enforce that decision before each request.

## Prerequisites

- The target repository, runtime, environment, and accountable owner
- An approved Cohere team and key for any live verification
- Current quality, security, privacy, capacity, and change-control requirements

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect code, configuration, and evidence. Use `WebFetch` only for current Cohere primary documentation. Use `Write` or `Edit` only when the user requested implementation and the exact target files are known; never write credentials or customer content.

## Current Contract

- Cohere's public privacy policy distinguishes enterprise Customer Data from general personal information and points to enterprise commitments.
- Do not infer retention, residency, training use, deletion, or subprocessors from a generic policy when a contract governs the workload.
- Embeddings and logs can encode sensitive information even when raw text is absent.
- Data minimization and tenant authorization must happen before Chat, Embed, Rerank, or tool calls.

## Authentication

Use an environment-specific key injected from an approved secret manager. Never print, persist, commit, or place `CO_API_KEY` in an example. Confirm access with the least costly bounded operation appropriate to the task, and treat key creation, rotation, revocation, role changes, and production-capacity requests as owner-approved actions.

## Instructions

1. Classify inputs, retrieved documents, outputs, embeddings, logs, and tool data by tenant and jurisdiction.
2. Map each data class to the signed terms, approved region, retention, deletion, access, and incident requirements.
3. Block disallowed classes and minimize, tokenize, or redact approved inputs before the provider call.
4. Apply tenant filters before retrieval and keep document identifiers safe for citation auditing.
5. Configure logs and caches with allowlisted fields, encryption, access control, and deletion tests.
6. Produce a data-flow record and obtain privacy or legal approval for unresolved contractual claims.

## Approval Boundaries

Do not expose or rotate keys, change Cohere Team roles, accept commercial terms, enable sensitive production data, increase spend or capacity, switch production models, send a support bundle, or execute model-proposed side effects without the accountable owner's approval. Keep diagnosis read-only unless implementation was requested.

## Output

Return the resolved API and model contract, files or settings inspected, evidence collected, validation result, remaining risk, owner, and rollback or next action. Redact keys, authorization headers, prompts, retrieved documents, embeddings, customer identifiers, and unrestricted environment output.

## Error Handling

| Condition | Response |
|---|---|
| Terms unavailable | Block sensitive production use until the governing agreement is identified. |
| PII detected | Apply the approved transformation or reject the request. |
| Cross-tenant data | Stop processing and invoke the data incident procedure. |
| Deletion unverified | Do not claim compliance; test each controlled storage layer. |

## Examples

Use this compact handoff shape to keep the selected scope, validation evidence, and operational result reviewable.

Input:

```text
data=customer-support; class=confidential; jurisdiction=EU; contract=enterprise
```

Expected handoff:

```text
purpose=approved; fields=minimized; retention=mapped; review=recorded
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Privacy policy](https://cohere.com/privacy)
- [Cohere security](https://cohere.com/security)
