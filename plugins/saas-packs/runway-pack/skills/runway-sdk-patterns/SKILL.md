---
name: runway-sdk-patterns
description: >-
  Implement a typed Runway SDK boundary that survives timeouts, restarts, throttling, and task failures. Use when consolidating production client behavior. Trigger with: "Runway SDK pattern", "wrap Runway client", "recover Runway task".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[client-module]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - runway
  - sdk
  - resilience
  - task-state
compatibility: 'Requires server-side Runway Dev access, current first-party documentation, an approved credit budget, and controlled media storage.'
---

# Recoverable Runway SDK Client Pattern

## Overview

A production client must separate request acceptance, provider task execution, and output persistence. The SDK removes protocol boilerplate, but the application still owns operation identity, deadlines, cancellation, state recovery, observability, and business decisions.

## Prerequisites

- Pinned official Node or Python SDK and reviewed API contract
- Durable operation and provider-task persistence
- Injected timeout, retry, logging, and output-storage adapters

## Instructions

### Step 1: Create one client factory

Construct the SDK once per process from server-side configuration. Expose reviewed timeouts, retry policy, and user agent; do not scatter raw client creation across handlers.

### Step 2: Define typed commands and results

Represent create intent, accepted task ID, provider state, terminal result, and stored asset separately. Prevent callers from treating an accepted create response as output.

### Step 3: Persist before waiting

Write operation ID, normalized request hash, and provider task ID transactionally before calling a wait helper. On restart, retrieve the task and resume rather than creating again.

### Step 4: Bound waiting

Use `waitForTaskOutput` or `wait_for_task_output` with a deadline and cancellation signal. A local abort or timeout stops waiting only; call the task cancellation endpoint when policy requires provider cancellation.

### Step 5: Classify failures

Map HTTP responses, `TaskFailedError`, timeout, cancellation, and malformed output into distinct application errors. Retry only documented transient HTTP classes; never retry safety failures automatically.

### Step 6: Store and observe

Copy output to owned storage, emit queue, run, and download timings, and record SDK version, API version, model, task ID, and redacted request fingerprint.

## Authentication

The factory reads `RUNWAYML_API_SECRET` from a server secret provider. Direct protocol concerns such as bearer and version headers stay inside the SDK boundary; application logs must redact credentials and signed URLs.

## Tool Discipline

Use Read and Grep to inspect application configuration, provider documentation, lockfiles, fixtures, schemas, tests, and redacted operational evidence before proposing a change. Use Write or Edit only for an approved implementation, configuration, test, runbook, or redacted receipt. Do not create, cancel, delete, retry, deploy, rotate, revoke, publish, or otherwise mutate production Runway resources without explicit operator approval.

## Output

- Single typed client boundary with injected dependencies
- Restart-safe create, retrieve, wait, cancel, and output-copy behavior
- Structured error taxonomy and redacted telemetry contract

Return the environment, organization alias, operation and task identifiers, API and SDK versions, model or router policy, source-contract fingerprint, task-state evidence, credit boundary, output disposition, unresolved risk, rollback state, and final decision without exposing API secrets, prompt or media contents, or temporary signed URLs.

## Examples

A web request submits a generation and disconnects. The worker has already saved the task ID, so another process retrieves it, waits with a new deadline, stores the output, and marks the operation complete without issuing a duplicate create.

## Error Handling

| Failure | Response |
| --- | --- |
| SDK timeout | Return a nonterminal application state and schedule retrieval; cancel explicitly only when policy requires it. |
| `TaskFailedError` with safety code | Record a redacted diagnostic and stop; do not convert it into a transport retry. |
| Malformed successful output | Quarantine the response, preserve task evidence, and avoid publishing an unvalidated URL. |

## Validation

Run typed contract tests across every state and error class, kill the process after create to prove recovery, abort a wait to prove the provider task remains, and assert redaction of keys and URLs.

## Resources

- [First-party source notes](references/official-docs.md)
- [Runway agent context](https://docs.dev.runwayml.com/ai-context.md)
- [API reference](https://docs.dev.runwayml.com/api.md)
- [Models](https://docs.dev.runwayml.com/guides/models.md)
- [Usage tiers](https://docs.dev.runwayml.com/usage/tiers.md)
- [Pricing](https://docs.dev.runwayml.com/guides/pricing.md)
- [Production checklist](https://docs.dev.runwayml.com/guides/go-live.md)
