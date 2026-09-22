---
name: cohere-common-errors
description: >-
  Diagnose Cohere v2 authentication, validation, model, quota, transport, and provider failures from redacted evidence. Use when a Cohere request fails. Trigger with "Cohere error", "Cohere 429", or "debug Cohere API".
argument-hint: "[status-code|error-message] [request-id]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- cohere
- troubleshooting
model: inherit
effort: high
compatibility: Designed for Claude Code; live verification requires network access and an approved Cohere API key
---
# Cohere Error Diagnosis

## Overview

Classify the failing layer before changing code, and return a minimal reproduction plus the safest next action.

## Prerequisites

- The target repository, runtime, environment, and accountable owner
- An approved Cohere team and key for any live verification
- Current quality, security, privacy, capacity, and change-control requirements

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect code, configuration, and evidence. Use `WebFetch` only for current Cohere primary documentation. Use `Write` or `Edit` only when the user requested implementation and the exact target files are known; never write credentials or customer content.

## Current Contract

- `400` and `422` usually indicate an invalid request contract or incompatible feature combination.
- `401` means the key is absent, invalid, expired, or injected into the wrong runtime.
- `402` indicates a billing limit; `429` indicates a current endpoint or model limit.
- Eligible `5xx` and transport failures may be retried boundedly; deterministic client errors must not be retried.

## Authentication

Use an environment-specific key injected from an approved secret manager. Never print, persist, commit, or place `CO_API_KEY` in an example. Confirm access with the least costly bounded operation appropriate to the task, and treat key creation, rotation, revocation, role changes, and production-capacity requests as owner-approved actions.

## Instructions

1. Capture timestamp, endpoint, status, SDK version, resolved model, redacted request shape, and provider request identifier when available.
2. Check Cohere status and determine whether failures are global, model-specific, environment-specific, or request-specific.
3. Compare required v2 fields and feature combinations with the current reference.
4. Run one minimal non-sensitive reproduction with retries disabled.
5. Apply the smallest correction or mitigation and verify with one bounded probe.
6. Record the classification, evidence, correction, and rollback or escalation owner.

## Approval Boundaries

Do not expose or rotate keys, change Cohere Team roles, accept commercial terms, enable sensitive production data, increase spend or capacity, switch production models, send a support bundle, or execute model-proposed side effects without the accountable owner's approval. Keep diagnosis read-only unless implementation was requested.

## Output

Return the resolved API and model contract, files or settings inspected, evidence collected, validation result, remaining risk, owner, and rollback or next action. Redact keys, authorization headers, prompts, retrieved documents, embeddings, customer identifiers, and unrestricted environment output.

## Error Handling

| Condition | Response |
|---|---|
| No status | Inspect timeout, DNS, TLS, proxy, and cancellation evidence. |
| `404` model | Resolve an accessible live model and verify provider/platform naming. |
| `429` | Honor backoff and reduce concurrency; do not loop immediately. |
| `5xx` | Check status, retry boundedly, then degrade or escalate. |

## Examples

Use this compact handoff shape to keep the selected scope, validation evidence, and operational result reviewable.

Input:

```text
status=400; endpoint=/v2/embed; fields=model,texts,input_type; secret=redacted
```

Expected handoff:

```text
cause=missing-embedding_types; retryable=false; fix=add-required-field
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Error reference](https://docs.cohere.com/reference/errors)
- [Cohere status](https://status.cohere.com)
