---
name: together-local-dev-loop
description: >-
  Develop Together AI integrations with a fake transport, recorded response shapes, deterministic assertions, and an opt-in bounded live probe. Use when iterating without spending tokens on every test. Trigger with "Together local dev", "mock Together API", or "test Together client".
argument-hint: "[repository-path] [test-command]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.9.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- together-ai
- testing
model: inherit
effort: medium
compatibility: Designed for Claude Code; optional live probes require network access and a Together AI project key
---
# Together AI Local Development Loop

## Overview

This skill keeps ordinary development offline and deterministic while retaining one explicit live lane for detecting provider-contract drift.

## Prerequisites

- The repository's test runner and client abstraction
- Sanitized fixtures for success, streaming chunks, `401`, `404`, `429`, and `503`
- A separate development project key for an opt-in live probe
- A fixed token and request budget for that probe

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to discover the wrapper, tests, fixtures, and environment gates. Use `WebFetch` to confirm current response and error shapes. Use `Write` or `Edit` only after matching repository conventions; never save live prompts, outputs, or credentials as fixtures.

## Current Contract

- Inject a client or transport rather than mocking SDK internals throughout the codebase.
- Preserve the SDK response fields the application actually consumes: choices, deltas, finish reason, usage, and error status.
- Make live tests opt-in, bounded, non-sensitive, and visibly skipped when no approved key exists.
- Test dynamic limit-header handling without hard-coding permanent RPM or TPM values.

## Authentication

Offline tests use no key. The live lane reads a development-only `TOGETHER_API_KEY` from the approved test secret store and must be unavailable to untrusted fork workflows.

## Instructions

1. Locate the narrowest Together client boundary and enumerate consumed fields.
2. Build typed fake responses for non-streaming, streaming, and each retry class.
3. Assert model selection, request bounds, idempotent reconciliation keys, and redaction.
4. Gate the live probe behind an explicit environment switch plus a development key.
5. Limit the live probe to one small request against a catalog-resolved model.
6. Compare shape-level behavior, update sanitized fixtures if approved, and record cost/cleanup.

## Approval Boundaries

Do not expose a live key to pull requests from forks. Do not refresh fixtures from customer traffic or authorize an unbounded live test suite.

## Output

Return fake-contract coverage, offline test results, live-lane disposition, model-resolution evidence, request budget, and any detected SDK or API drift.

## Error Handling

| Condition | Response |
|---|---|
| SDK object is hard to fake | Introduce an application-owned adapter; do not patch deep internals. |
| Live key absent | Mark the live lane skipped, not passed. |
| Fixture contains sensitive text | Remove it and replace it with synthetic data. |
| Live response shape changed | Preserve evidence and update the adapter before fixtures. |

## Examples

The example below shows the minimum redacted evidence expected from a successful invocation of this operator workflow.

```text
offline=34_pass; live=skipped(no-approved-key); fixtures=synthetic; token_budget=128
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Python v2 client](https://github.com/togethercomputer/together-py)
- [Chat API](https://docs.together.ai/reference/chat-completions)
- [Error codes](https://docs.together.ai/docs/error-codes)
