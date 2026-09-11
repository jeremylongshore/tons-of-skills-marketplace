---
name: cohere-webhooks-events
description: >-
  Handle Cohere v2 streaming events and convert application-owned asynchronous work into idempotent internal events without inventing provider webhooks. Use when building streaming UIs or event workflows. Trigger with "Cohere streaming", "Cohere SSE", or "Cohere events".
argument-hint: "[chat-stream|tool-stream|internal-event]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- cohere
- events
model: inherit
effort: high
compatibility: Designed for Claude Code; live verification requires network access and an approved Cohere API key
---
# Cohere Streaming and Application Events

## Overview

Separate response-stream events from durable business events and replace deprecated managed connectors with application-owned v2 tools.

## Prerequisites

- The target repository, runtime, environment, and accountable owner
- An approved Cohere team and key for any live verification
- Current quality, security, privacy, capacity, and change-control requirements

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect code, configuration, and evidence. Use `WebFetch` only for current Cohere primary documentation. Use `Write` or `Edit` only when the user requested implementation and the exact target files are known; never write credentials or customer content.

## Current Contract

- Chat v2 streaming is a server-sent response stream, not an inbound signed webhook surface.
- Handle typed content, citation, tool-call, and terminal events and tolerate additive unknown event types.
- Managed v1 connectors are deprecated; v2 retrieval and web search use user-defined tools.
- If the application emits durable callbacks, define its own authentication, signing, idempotency key, retries, and dead-letter policy.

## Authentication

Use an environment-specific key injected from an approved secret manager. Never print, persist, commit, or place `CO_API_KEY` in an example. Confirm access with the least costly bounded operation appropriate to the task, and treat key creation, rotation, revocation, role changes, and production-capacity requests as owner-approved actions.

## Instructions

1. Choose response streaming, tool streaming, or an application-owned durable event; do not conflate them.
2. Implement an async iterator with cancellation, timeout, terminal-state validation, and unknown-event telemetry.
3. Buffer partial content only within explicit memory and latency bounds.
4. Correlate tool calls and results before continuing the v2 message loop.
5. For durable internal events, persist state before delivery and enforce signature and replay-window validation.
6. Test disconnects, duplicate delivery, out-of-order events, partial streams, unknown types, and terminal errors.

## Approval Boundaries

Do not expose or rotate keys, change Cohere Team roles, accept commercial terms, enable sensitive production data, increase spend or capacity, switch production models, send a support bundle, or execute model-proposed side effects without the accountable owner's approval. Keep diagnosis read-only unless implementation was requested.

## Output

Return the resolved API and model contract, files or settings inspected, evidence collected, validation result, remaining risk, owner, and rollback or next action. Redact keys, authorization headers, prompts, retrieved documents, embeddings, customer identifiers, and unrestricted environment output.

## Error Handling

| Condition | Response |
|---|---|
| Partial stream | Mark output incomplete and do not treat it as a successful durable result. |
| Unknown event | Record its type safely and continue only when semantics allow. |
| Duplicate internal event | Return the prior idempotent result without repeating side effects. |
| Connector dependency | Migrate it to an application-owned v2 tool. |

## Examples

Use this compact handoff shape to keep the selected scope, validation evidence, and operational result reviewable.

Input:

```text
mode=chat-stream; tool-use=true; durable-callback=application-owned
```

Expected handoff:

```text
stream=typed; cancellation=tested; connector-v1=absent; events=idempotent
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Streaming](https://docs.cohere.com/docs/streaming)
- [API migration](https://docs.cohere.com/docs/migrating-v1-to-v2)
