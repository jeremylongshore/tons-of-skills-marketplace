---
name: together-hello-world
description: >-
  Build a bounded Together AI chat-completion probe with a current model selected from the live catalog, optional streaming, usage capture, and redacted evidence. Use when proving a new inference connection. Trigger with "Together hello world", "first Together request", or "stream Together chat".
argument-hint: "[repository-path] [python|typescript|rest]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- together-ai
- inference
model: inherit
effort: medium
compatibility: Designed for Claude Code; live inference requires network access, an API key, and funded Together AI usage
---
# Together AI First Inference

## Overview

This skill produces the smallest observable chat-completion probe without freezing a model catalog entry into application policy.

## Prerequisites

- A configured `TOGETHER_API_KEY` secret reference
- Together Python SDK v2, current TypeScript SDK, or an HTTPS client
- A current chat model resolved from the Together catalog
- A small approved prompt containing no sensitive data

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect the client wrapper and configuration. Use `WebFetch` for the current quickstart, model catalog, and response contract. Use `Write` or `Edit` only for the approved sample or test file; never place the key in code.

## Current Contract

- Call `client.chat.completions.create()` with a Together model ID such as the current quickstart example.
- For streaming, iterate chunks and guard for an empty `choices` array before reading `delta.content`.
- Capture `finish_reason` and `usage`; bound `max_tokens`, timeout, and retry count.
- Re-resolve the model from the live catalog before production use because availability and redirects change.

## Authentication

The SDK reads `TOGETHER_API_KEY`. Direct REST requests send the same project key as a Bearer token to `https://api.together.ai/v1/chat/completions`. Never return or log the header.

## Instructions

1. Confirm the requested modality is chat and select a current chat-capable model.
2. Create one system message and one sanitized user message with an explicit output bound.
3. Choose non-streaming for contract inspection or streaming for latency and chunk handling.
4. Validate status, non-empty content, finish reason, model identifier, and usage fields.
5. Record latency and request outcome without storing the prompt or response when either is sensitive.
6. Remove disposable output and hand off the model-selection rationale.

## Approval Boundaries

Do not send customer data, regulated content, or proprietary prompts until data handling and retention are approved. Do not silently switch to a more expensive or materially different model.

## Output

Return the client/runtime, resolved model, streaming mode, bounded request parameters, status, finish reason, token usage, latency, and redaction disposition.

## Error Handling

| Condition | Response |
|---|---|
| `401` | Stop and repair credential injection. |
| `404` | Refresh the model catalog and deprecation page. |
| `429` | Read dynamic limit headers and retry with bounded jitter. |
| `503` or `504` | Retry briefly, then surface overload or timeout evidence. |

## Examples

The example below shows the minimum redacted evidence expected from a successful invocation of this operator workflow.

```text
model=catalog-resolved; stream=true; max_tokens=128; status=200; finish=stop; secret=redacted
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Quickstart](https://docs.together.ai/docs/quickstart)
- [Chat completions](https://docs.together.ai/docs/inference/chat/overview)
- [Chat API](https://docs.together.ai/reference/chat-completions)
