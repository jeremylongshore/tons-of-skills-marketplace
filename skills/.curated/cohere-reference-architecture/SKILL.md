---
name: cohere-reference-architecture
description: >-
  Design a governed Cohere architecture for Chat, RAG, tools, streaming, evaluation, and provider operations. Use when planning or reviewing a Cohere system. Trigger with "Cohere architecture", "Cohere RAG design", or "Cohere service layout".
argument-hint: "[system-name] [single-tenant|multi-tenant]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- cohere
- architecture
model: inherit
effort: high
compatibility: Designed for Claude Code; live verification requires network access and an approved Cohere API key
---
# Cohere Reference Architecture

## Overview

Define clear boundaries between clients, policy, retrieval, provider access, tools, evaluation, and operations so model behavior cannot bypass application controls.

## Prerequisites

- The target repository, runtime, environment, and accountable owner
- An approved Cohere team and key for any live verification
- Current quality, security, privacy, capacity, and change-control requirements

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect code, configuration, and evidence. Use `WebFetch` only for current Cohere primary documentation. Use `Write` or `Edit` only when the user requested implementation and the exact target files are known; never write credentials or customer content.

## Current Contract

- Keep a typed Cohere provider adapter behind an application service boundary.
- Apply tenant authorization and metadata filters before retrieval, then preserve document IDs through Rerank and citations.
- Dispatch tools through a policy-enforcing registry with schemas, approvals, timeouts, and audit evidence.
- Resolve model, lifecycle, capacity, and platform IDs through environment configuration and current provider sources.

## Authentication

Use an environment-specific key injected from an approved secret manager. Never print, persist, commit, or place `CO_API_KEY` in an example. Confirm access with the least costly bounded operation appropriate to the task, and treat key creation, rotation, revocation, role changes, and production-capacity requests as owner-approved actions.

## Instructions

1. Capture users, tenants, data classes, quality objectives, latency targets, side effects, and failure tolerance.
2. Draw trust boundaries for clients, API, policy, retrieval, vector store, Cohere, tools, logs, and secret stores.
3. Define request, result, citation, tool, error, and telemetry contracts at each boundary.
4. Choose synchronous, streaming, queued, or degraded paths with bounded retries and cancellation.
5. Attach offline evaluation, protected live probes, canarying, observability, budget, and incident controls.
6. Review threats, data terms, capacity, model lifecycle, rollback, and named ownership before implementation.

## Approval Boundaries

Do not expose or rotate keys, change Cohere Team roles, accept commercial terms, enable sensitive production data, increase spend or capacity, switch production models, send a support bundle, or execute model-proposed side effects without the accountable owner's approval. Keep diagnosis read-only unless implementation was requested.

## Output

Return the resolved API and model contract, files or settings inspected, evidence collected, validation result, remaining risk, owner, and rollback or next action. Redact keys, authorization headers, prompts, retrieved documents, embeddings, customer identifiers, and unrestricted environment output.

## Error Handling

| Condition | Response |
|---|---|
| Provider calls in UI | Move them behind the trusted server boundary. |
| Tenant filter after retrieval | Move authorization before any candidate can cross the boundary. |
| Tool reflection | Replace it with an explicit validated registry. |
| Implicit fallback | Require configured, evaluated, and approved model routes. |

## Examples

Use this compact handoff shape to keep the selected scope, validation evidence, and operational result reviewable.

Input:

```text
system=enterprise-search; tenants=multi; features=rag,tools,streaming
```

Expected handoff:

```text
boundaries=defined; contracts=versioned; controls=owned; rollback=designed
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Cloud compatibility](https://docs.cohere.com/docs/cohere-works-everywhere/)
- [Tool use](https://docs.cohere.com/docs/tool-use)
