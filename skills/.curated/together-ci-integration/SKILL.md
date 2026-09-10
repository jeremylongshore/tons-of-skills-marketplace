---
name: together-ci-integration
description: >-
  Gate Together AI client, batch, fine-tuning, and deployment changes with offline contract tests plus a protected bounded live lane. Use when adding CI for a Together-backed repository. Trigger with "Together CI", "test Together integration", or "Together contract tests".
argument-hint: "[repository-path] [live-test-environment]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- together-ai
- ci
model: inherit
effort: high
compatibility: Designed for Claude Code; live CI requires a protected Together AI development project key
---
# Together AI Continuous Integration

## Overview

This skill keeps ordinary pull-request gates deterministic and secretless while retaining a separately protected live lane for provider-contract drift.

## Prerequisites

- The repository's CI platform, test runner, and provider adapter
- Sanitized fixtures for success, streaming, errors, limits, and asynchronous jobs
- A protected environment and development-only Together project key for live testing
- Explicit request, token, cost, concurrency, and timeout ceilings

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect workflows, manifests, adapters, tests, and secret references. Use `WebFetch` for current SDK and API contracts. Use `Write` or `Edit` only after confirming the CI file and fork-secret boundary.

## Current Contract

- Pull requests run schema, adapter, fixture, retry, reconciliation, and redaction tests without a live credential.
- A live lane is opt-in or trusted-branch-only, uses a development project, and sends one bounded non-sensitive request.
- Fork workflows never receive `TOGETHER_API_KEY` or a workflow token able to retrieve it.
- Paid batch, fine-tuning, and dedicated-capacity actions are plan/contract tests unless separately approved.

## Authentication

Inject a development-only project key into the protected live job as `TOGETHER_API_KEY`. Mask it, restrict environment access, and prevent execution of untrusted code in any secret-bearing workflow.

## Instructions

1. Inventory direct SDK calls, model constants, retry paths, async jobs, and deployment commands.
2. Add offline contract fixtures for response shapes, dynamic headers, terminal states, and errors.
3. Test model-policy fallbacks, batch ID reconciliation, key redaction, and bounded retry behavior.
4. Separate the live job behind a protected environment and trusted event/branch condition.
5. Limit live execution to a catalog/model-list probe or one small chat request with a hard budget.
6. Publish test evidence and cost while scrubbing prompts, responses, headers, and credentials.

## Approval Boundaries

Do not expose secrets to fork code or let CI submit fine-tunes, batches, provisioned capacity, or dedicated replicas without a distinct approval boundary and teardown.

## Output

Return offline coverage, fixture provenance, live-lane eligibility/result, secret boundary, request budget, cost, and any provider drift.

## Error Handling

| Condition | Response |
|---|---|
| No approved live key | Mark live verification skipped; keep offline gates authoritative. |
| Fork event requests secrets | Refuse the secret-bearing job. |
| Live model disappears | Refresh catalog/deprecations and fail visibly. |
| Credential appears in logs | Cancel publication, rotate the key, and scrub artifacts. |

## Examples

The example below shows the minimum redacted evidence expected from a successful invocation of this operator workflow.

```text
offline=pass; live=skipped(untrusted-event); paid-actions=disabled; secrets=not-exposed
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Authentication](https://docs.together.ai/docs/api-keys-authentication)
- [Python v2 client](https://github.com/togethercomputer/together-py)
- [Chat API](https://docs.together.ai/reference/chat-completions)
