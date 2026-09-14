---
name: runway-common-errors
description: >-
  Diagnose Runway transport errors, queued states, moderation failures, and malformed model requests without duplicate generation. Use when a task or API call fails. Trigger with: "debug Runway error", "Runway task failed", "Runway 429".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[task-id-or-redacted-error]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - runway
  - errors
  - moderation
  - retries
compatibility: 'Requires server-side Runway Dev access, current first-party documentation, an approved credit budget, and controlled media storage.'
---

# Runway HTTP and Task Failure Triage

## Overview

Runway has two failure planes: synchronous HTTP responses and asynchronous task terminal states. Triage must preserve the task ID, selected model schema, and redacted evidence before deciding whether a retry is safe.

## Prerequisites

- Task ID or redacted HTTP response with request correlation
- Model, endpoint, API version, SDK version, and request fingerprint
- Access to current HTTP-error and task-failure guidance

## Instructions

### Step 1: Identify the failure plane

If create returned no task ID, classify the HTTP status. If a task exists, retrieve it and classify `THROTTLED`, `FAILED`, `CANCELLED`, or malformed `SUCCEEDED` output separately.

### Step 2: Protect against duplicates

Search durable operation and task records before any retry. A client timeout or lost response is not proof that create failed; reconcile by task ID or operation evidence first.

### Step 3: Handle request errors

Treat `400`, `401`, `404`, and `405` as non-retryable until their cause changes. For `400`, compare the request against the exact selected model variant instead of editing fields by guesswork.

### Step 4: Handle transient HTTP errors

Retry `429`, `502`, `503`, and `504` only with a bound, exponential backoff, and random jitter up to 50 percent. Respect the operation deadline and credit budget.

### Step 5: Handle task failures

Inspect `failureCode`. Never retry safety failures automatically; they still consume credits. Internal or preprocessing-internal failures may permit a delayed, bounded retry according to current documentation.

### Step 6: Close the incident

Record the corrected contract or provider recovery, duplicate check, credits at risk, final task state, stored output disposition, and whether a docs or fixture update is required.

## Authentication

Triage reads provider tasks using the server-side organization key. Evidence must redact bearer secrets, unsafe prompt bodies, customer media, and signed output URLs while retaining identifiers and hashes needed for correlation.

## Tool Discipline

Use Read and Grep to inspect application configuration, provider documentation, lockfiles, fixtures, schemas, tests, and redacted operational evidence before proposing a change. Use Write or Edit only for an approved implementation, configuration, test, runbook, or redacted receipt. Do not create, cancel, delete, retry, deploy, rotate, revoke, publish, or otherwise mutate production Runway resources without explicit operator approval.

## Output

- HTTP-versus-task failure classification and duplicate-risk decision
- Bounded retry, repair, cancellation, or escalation action
- Redacted incident receipt and regression-test update

Return the environment, organization alias, operation and task identifiers, API and SDK versions, model or router policy, source-contract fingerprint, task-state evidence, credit boundary, output disposition, unresolved risk, rollback state, and final decision without exposing API secrets, prompt or media contents, or temporary signed URLs.

## Examples

A create call returns `400` after a model migration. The operator compares the payload with that model's current discriminated schema, finds an invalid ratio copied from another model, updates the fixture, and retries once under the original operation ID.

## Error Handling

| Failure | Response |
| --- | --- |
| No task ID and ambiguous network failure | Do not issue an immediate duplicate; reconcile logs and durable operation state, then require approval if uncertainty remains. |
| Repeated transient failure reaches the bound | Stop retries, preserve the last request ID, and escalate with provider and budget evidence. |
| Failure evidence contains unsafe or personal media | Restrict and redact the bundle before sharing while preserving hashes and failure codes. |

## Validation

Exercise every documented HTTP class, all task terminal states, duplicate-recovery ambiguity, a safety failure, and retry exhaustion. Assert that only approved transient classes retry and every loop has an attempt and time bound.

## Resources

- [First-party source notes](references/official-docs.md)
- [Runway agent context](https://docs.dev.runwayml.com/ai-context.md)
- [API reference](https://docs.dev.runwayml.com/api.md)
- [Models](https://docs.dev.runwayml.com/guides/models.md)
- [Usage tiers](https://docs.dev.runwayml.com/usage/tiers.md)
- [Pricing](https://docs.dev.runwayml.com/guides/pricing.md)
- [Production checklist](https://docs.dev.runwayml.com/guides/go-live.md)
