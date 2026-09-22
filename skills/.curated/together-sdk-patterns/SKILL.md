---
name: together-sdk-patterns
description: >-
  Encapsulate Together AI SDK v2 behind a typed adapter with catalog-resolved models, bounded retries, streaming normalization, usage capture, and OpenAI-compatible migration seams. Use when building a reusable Together client layer. Trigger with "Together SDK pattern", "Together client wrapper", or "OpenAI compatibility on Together".
argument-hint: "[repository-path] [python|typescript]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.9.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- together-ai
- sdk
model: inherit
effort: high
compatibility: Designed for Claude Code; live calls require network access and a Together AI project key
---
# Together AI SDK Patterns

## Overview

This skill creates an application-owned boundary around Together's native v2 client or OpenAI-compatible surface so provider changes do not leak through every caller.

## Prerequisites

- The repository's language, dependency manager, and existing client abstractions
- Required capabilities such as chat, streaming, embeddings, batch, or fine-tuning
- Latency, retry, token, and spend budgets
- A policy for model selection and deprecation response

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to map existing provider calls and error handling. Use `WebFetch` for current SDK and API contracts. Use `Write` or `Edit` only to implement the approved adapter and focused tests.

## Current Contract

- Prefer the Together Python v2 client for Together-native features; v1 is maintenance-only.
- OpenAI clients require both the Together project key and `base_url="https://api.together.ai/v1"`.
- Together model IDs use provider/model names; OpenAI-native model strings return `404`.
- Normalize streaming chunks defensively and capture both ordinary usage and nested reasoning/cached-token fields when present.

## Authentication

Construct clients from runtime-injected `TOGETHER_API_KEY`. Keep the key out of adapter configuration objects that may be logged or serialized. REST and OpenAI-compatible clients send it as a Bearer token.

## Instructions

1. Inventory direct Together and OpenAI-compatible calls, consumed fields, and retry behavior.
2. Define typed request/result/error interfaces owned by the application.
3. Centralize base URL, timeouts, model policy, request bounds, and credential injection.
4. Normalize full and streaming responses without discarding finish reason, usage, warnings, or request metadata.
5. Retry only bounded transient classes with jitter; surface auth, billing, validation, and model errors immediately.
6. Add fake-transport contract tests and one opt-in live compatibility probe.

## Approval Boundaries

Do not change the default model, retry amplification, or OpenAI-to-Together routing globally without latency, quality, and cost evidence plus a rollback.

## Output

Return the adapter interface, runtime configuration contract, normalized result/error shapes, retry policy, model policy, and test evidence.

## Error Handling

| Condition | Response |
|---|---|
| OpenAI model ID returns `404` | Resolve a Together model ID; do not rewrite the error as transient. |
| Stream chunk has no choices | Skip safely and continue until terminal evidence. |
| SDK major mismatch | Stop and apply the v2 migration contract before feature work. |
| Retry budget exhausted | Return the last redacted status and retry metadata. |

## Examples

The example below shows the minimum redacted evidence expected from a successful invocation of this operator workflow.

```text
adapter=typed; sdk=together-v2; model=catalog-resolved; retries=bounded; usage=normalized
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Python v2 migration](https://docs.together.ai/docs/pythonv2-migration-guide)
- [OpenAI compatibility](https://docs.together.ai/docs/inference/openai-compatibility)
- [Official Together skills](https://github.com/togethercomputer/skills)
