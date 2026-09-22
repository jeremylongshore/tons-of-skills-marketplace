---
name: together-common-errors
description: >-
  Analyze and diagnose Together AI authentication, billing, request, model, throttling, overload, batch, fine-tuning, and endpoint failures from redacted evidence. Use when a Together integration fails or behaves inconsistently. Trigger with "Together error", "Together 429", or "Together model not found".
argument-hint: "[repository-path] [redacted-error-or-job-id]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.9.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- together-ai
- troubleshooting
model: inherit
effort: high
compatibility: Designed for Claude Code; live diagnosis may require network access and authorized Together project access
---
# Together AI Error Diagnosis

## Overview

This skill classifies failures by status and workload state, preserves evidence, and avoids turning permanent errors into costly retry storms.

## Prerequisites

- Redacted status, response body, headers, SDK version, and request shape
- The current model ID, endpoint type, and Together project alias
- Batch, fine-tune, endpoint, file, or deployment IDs when applicable
- The caller's timeout and retry policy

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect the adapter, logs, retry code, and manifests. Use `WebFetch` for current error, model, and lifecycle documentation. Use `Write` or `Edit` only for the approved fix or regression test after the failure class is proven.

## Current Contract

- `400` means request/schema trouble; `401` authentication; `402` spend limit; `404` endpoint/model; `429` throttling; `500`/`503` server or overload.
- Context overflow can surface as `403` in Together's error table; inspect the body rather than classifying by status alone.
- Model availability and redirects change. Resolve `404` against the current catalog and deprecation page.
- A completed asynchronous job can still contain line-level failures; inspect its error artifact.

## Authentication

Together APIs use a project-scoped Bearer key from `TOGETHER_API_KEY`. Verify presence and project routing without echoing the key. Treat a leaked header as a credential incident, not merely a request bug.

## Instructions

1. Reproduce once with a sanitized minimal request and capture status, body, useful headers, latency, and SDK version.
2. Classify the error as credential, billing, request, model lifecycle, dynamic limit, transient provider, or asynchronous-job failure.
3. Compare the exact request and model to current primary documentation.
4. Apply the narrowest correction and add a deterministic regression case.
5. Retry only `429`, `500`, `503`, or `504` with bounded jitter and an overall deadline.
6. Verify recovery, redact evidence, and report any provider-side incident separately.

## Approval Boundaries

Do not broaden credentials, raise spend limits, switch models, or resubmit paid jobs automatically. Each changes authority, behavior, or cost and requires the relevant owner.

## Output

Return the failure class, sanitized evidence, root cause, correction, retry disposition, regression coverage, and any required owner action.

## Error Handling

| Condition | Response |
|---|---|
| `401` | Repair credential injection or project selection; do not retry. |
| `402` | Stop and route to the billing owner. |
| `404` | Check URL, model catalog, and deprecations before changing code. |
| `429` or `503` | Honor current headers, jitter, and the bounded retry budget. |

## Examples

The example below shows the minimum redacted evidence expected from a successful invocation of this operator workflow.

```text
status=404; class=model-lifecycle; catalog=checked; substitution=approval-required; retry=no
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Error codes](https://docs.together.ai/docs/error-codes)
- [Deprecations](https://docs.together.ai/docs/deprecations)
- [Dynamic rate limits](https://docs.together.ai/docs/serverless/rate-limits)
