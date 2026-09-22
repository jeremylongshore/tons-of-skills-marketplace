---
name: runway-local-dev-loop
description: >-
  Build and test a Runway integration locally with recorded contracts, deterministic task states, and an opt-in paid canary. Use when shortening iteration without duplicate spend. Trigger with: "develop Runway locally", "mock Runway tasks", "Runway dev loop".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[service-or-test-path]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - runway
  - local-development
  - fixtures
  - testing
compatibility: 'Requires server-side Runway Dev access, current first-party documentation, an approved credit budget, and controlled media storage.'
---

# Runway Offline-First Development Loop

## Overview

Make routine development deterministic and non-billable. The local loop should model Runway's asynchronous protocol accurately, while a separately authorized canary detects provider drift without turning every test run into paid generation.

## Prerequisites

- A local service boundary that can replace the Runway client
- Redacted fixtures for create, task states, HTTP errors, and task failures
- A disabled-by-default credential path for an approved canary

## Instructions

### Step 1: Map the seam

Use Read and Grep to locate direct SDK calls, task persistence, output download code, retries, and cancellation. Introduce one provider interface if application code currently imports the SDK everywhere.

### Step 2: Model the state machine

Create fixtures for `PENDING`, `THROTTLED`, `RUNNING`, `SUCCEEDED`, `FAILED`, and `CANCELLED`. Make only `SUCCEEDED` include output; make failed fixtures include a machine-readable failure code.

### Step 3: Separate clocks and network

Inject polling time, jitter, timeout, and HTTP transport. Tests should advance a fake clock and never wait five real seconds or contact Runway.

### Step 4: Protect against duplicate work

Persist an internal operation ID and provider task ID. Simulate a lost response after task creation and prove recovery reads the saved task rather than issuing another paid request.

### Step 5: Test media boundaries

Use tiny synthetic files and fixtures for public URL, data URI, and `runway://` input. Model auto-crop review, upload expiry, output expiry, and owned-storage copy without retaining real signed URLs.

### Step 6: Run an opt-in canary

Require an explicit environment switch, safe prompt, model schema check, credit ceiling, and named approver. Keep CI and ordinary local commands on the fake provider.

## Authentication

Fixtures contain no usable secrets. The optional canary reads `RUNWAYML_API_SECRET` only in the server process, uses the reviewed version header, and refuses to run when the opt-in approval variables are incomplete.

## Tool Discipline

Use Read and Grep to inspect application configuration, provider documentation, lockfiles, fixtures, schemas, tests, and redacted operational evidence before proposing a change. Use Write or Edit only for an approved implementation, configuration, test, runbook, or redacted receipt. Do not create, cancel, delete, retry, deploy, rotate, revoke, publish, or otherwise mutate production Runway resources without explicit operator approval.

## Output

- Replaceable Runway client interface and deterministic fixture set
- Fast state-machine, retry, timeout, cancellation, and duplicate-recovery tests
- Redacted optional-canary receipt with a declared credit ceiling

Return the environment, organization alias, operation and task identifiers, API and SDK versions, model or router policy, source-contract fingerprint, task-state evidence, credit boundary, output disposition, unresolved risk, rollback state, and final decision without exposing API secrets, prompt or media contents, or temporary signed URLs.

## Examples

A developer reproduces a timeout after task creation by advancing a fake clock. The service restarts, finds the stored task ID, resumes retrieval, and copies a fixture output without creating a second task or spending credits.

## Error Handling

| Failure | Response |
| --- | --- |
| A unit test reaches the network | Fail closed and replace the unmocked client path. |
| Fixture accepts output on a non-success state | Correct the contract and add a regression assertion. |
| Canary variables are partially set | Refuse the call and print the missing approval fields without printing the secret. |

## Validation

Run the suite with network access disabled, prove all six task states, simulate a lost create response and expired output, and separately document any approved live canary. Routine local success must not depend on provider availability.

## Resources

- [First-party source notes](references/official-docs.md)
- [Runway agent context](https://docs.dev.runwayml.com/ai-context.md)
- [API reference](https://docs.dev.runwayml.com/api.md)
- [Models](https://docs.dev.runwayml.com/guides/models.md)
- [Usage tiers](https://docs.dev.runwayml.com/usage/tiers.md)
- [Pricing](https://docs.dev.runwayml.com/guides/pricing.md)
- [Production checklist](https://docs.dev.runwayml.com/guides/go-live.md)
