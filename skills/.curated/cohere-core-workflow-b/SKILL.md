---
name: cohere-core-workflow-b
description: >-
  Build a bounded Cohere v2 tool-use loop with JSON Schema, explicit dispatch, result correlation, and approval gates. Use when adding Cohere-powered agents or function calling. Trigger with "Cohere tool use", "Cohere agent", or "Cohere function calling".
argument-hint: "[repository-path] [tool-name]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- cohere
- tool-use
model: inherit
effort: high
compatibility: Designed for Claude Code; live verification requires network access and an approved Cohere API key
---
# Cohere Tool-Using Agent Loop

## Overview

Let the model propose typed tool calls while application code validates, authorizes, executes, correlates, and limits every side effect.

## Prerequisites

- The target repository, runtime, environment, and accountable owner
- An approved Cohere team and key for any live verification
- Current quality, security, privacy, capacity, and change-control requirements

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect code, configuration, and evidence. Use `WebFetch` only for current Cohere primary documentation. Use `Write` or `Edit` only when the user requested implementation and the exact target files are known; never write credentials or customer content.

## Current Contract

- Define each v2 tool as a function with JSON Schema parameters.
- Read proposed calls from the response message and correlate results with `tool_call_id`.
- Append the assistant tool-call message and tool results to the application-managed `messages` history.
- Command A+ was the current high-capability tool-use candidate on the review date; resolve availability before pinning it.

## Authentication

Use an environment-specific key injected from an approved secret manager. Never print, persist, commit, or place `CO_API_KEY` in an example. Confirm access with the least costly bounded operation appropriate to the task, and treat key creation, rotation, revocation, role changes, and production-capacity requests as owner-approved actions.

## Instructions

1. Define a minimal tool allowlist, strict schemas, timeouts, and side-effect classifications.
2. Resolve a live tool-capable model and submit the user message plus tool definitions.
3. Validate tool name, arguments, tenant scope, and approval state before dispatch.
4. Execute read-only calls automatically only if policy allows; pause for consequential writes.
5. Append correlated tool results and continue until content is returned or the iteration budget is exhausted.
6. Test unknown tools, invalid arguments, duplicate calls, timeouts, denial, and loop exhaustion.

## Approval Boundaries

Do not expose or rotate keys, change Cohere Team roles, accept commercial terms, enable sensitive production data, increase spend or capacity, switch production models, send a support bundle, or execute model-proposed side effects without the accountable owner's approval. Keep diagnosis read-only unless implementation was requested.

## Output

Return the resolved API and model contract, files or settings inspected, evidence collected, validation result, remaining risk, owner, and rollback or next action. Redact keys, authorization headers, prompts, retrieved documents, embeddings, customer identifiers, and unrestricted environment output.

## Error Handling

| Condition | Response |
|---|---|
| Unknown tool | Return a structured denial result; never dispatch by reflection. |
| Invalid arguments | Reject before execution and preserve validation evidence. |
| Missing correlation | Stop because tool results cannot be safely attached. |
| Loop exhausted | Return partial state and request direction without another model call. |

## Examples

Use this compact handoff shape to keep the selected scope, validation evidence, and operational result reviewable.

Input:

```text
goal=lookup-order; tools=read-only-order-status; max-iterations=4
```

Expected handoff:

```text
iterations=2; tool-calls=1; side-effects=none; final=validated
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Tool use](https://docs.cohere.com/docs/tool-use)
- [v1 to v2 migration](https://docs.cohere.com/docs/migrating-v1-to-v2)
