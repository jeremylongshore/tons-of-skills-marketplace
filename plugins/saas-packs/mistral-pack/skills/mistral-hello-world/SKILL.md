---
name: mistral-hello-world
description: >-
  Validate one minimal Mistral chat request with pinned inputs, usage evidence, and zero sensitive data. Use when proving a new integration path. Trigger with "Mistral hello world", "test my Mistral setup", or "make a first Mistral request".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<runtime> <environment> <model-alias>"
version: 1.14.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, mistral, quickstart]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live or external Mistral actions require network access and explicit approval"
---
# Mistral Bounded First Request

## Overview

Prove the smallest useful chat path without turning a quickstart into production authority. Build offline, use synthetic text, capture content-free evidence, and stop after one approved response.

## Prerequisites

- A configured server-side `MISTRAL_API_KEY` reference.
- A current model identifier selected from account-visible evidence.
- Approval for one billable request and a non-sensitive synthetic prompt.

## Current Contract

The current chat surface is `POST /v1/chat/completions`. A request includes a model and messages; response and usage shapes come from the current endpoint schema. Model aliases and availability are mutable.

## Authentication

Resolve the key only at runtime through the trusted client boundary. Do not print the key, headers, prompt, or response content in the receipt.

## Instructions

1. Inspect runtime and dependency lock before selecting the official client.
2. Resolve an allowed model dynamically; do not rely on an old price or context table.
3. Construct one deterministic message containing no secrets, personal data, or customer content.
4. Review parameters and maximum output before authorizing the live call.
5. Execute once after approval; record status, latency, returned model, finish reason, and usage.
6. Dispose of response content unless the approved plan explicitly retains the synthetic sample.

## Tool Discipline

Use Read, Glob, and Grep to inspect code, locks, configuration, tests, and evidence. Use Write and Edit only for approved repository changes. Invocation alone does not authorize network calls, paid usage, uploads, stateful resources, admin mutations, deployments, or deletion.

## Approval Boundaries

Require approval for the live call, model, output bound, and retained response. Do not add retries, tools, files, or stateful resources.

## Error Handling

- `401` is a configuration problem, not a reason to reveal a credential.
- `429` requires current workspace evidence, not immediate repeated calls.
- Model-not-found requires fresh discovery; never silently fall back to a costlier model.

## Output

Return endpoint, requested/returned model, result class, latency, finish reason, usage, retention decision, and rollback. Redact content and credentials.

## Examples

- Prove staging with the prompt `Reply with the word ready`.
- Report `request_count=1; content_retained=no; usage_recorded=yes`.

## Validation

Assert exactly one request, recognized shape, bounded output, usage capture, no sensitive data, no logging, and no fallback.

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources before relying on mutable endpoints, models, limits, prices, preview status, or retention.
- Record live account observations as environment-specific evidence, not universal Mistral guarantees.
