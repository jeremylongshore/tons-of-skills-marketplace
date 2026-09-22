---
name: runway-ci-integration
description: >-
  Gate Runway client changes in CI with offline schema fixtures and a separately approved canary lane. Use when preventing API drift without paying on every commit. Trigger with: "test Runway in CI", "Runway contract gate", "Runway canary workflow".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[workflow-file]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - runway
  - ci
  - contract-testing
  - supply-chain
compatibility: 'Requires server-side Runway Dev access, current first-party documentation, an approved credit budget, and controlled media storage.'
---

# Non-Billable Runway CI Contract Gate

## Overview

CI should catch client, request-shape, task-state, and storage regressions without generating media on untrusted code. Provider calls belong in a protected, manually approved canary lane with a hard credit ceiling and no fork secrets.

## Prerequisites

- A CI system with protected environments and fork-secret isolation
- Pinned SDK lockfile plus redacted API and task fixtures
- A documented owner for the optional live canary budget

## Instructions

### Step 1: Inventory trust boundaries

Inspect workflow triggers, permissions, secret inheritance, dependency installation, artifact retention, and fork behavior. Mark every event on which Runway credentials must be unavailable.

### Step 2: Build the offline gate

Validate request payloads against reviewed per-model fixtures, exercise all task states, verify retry classifications, and prove output is copied to owned storage. Run with network disabled where practical.

### Step 3: Pin the supply chain

Use lockfile-enforced installs, verify the selected SDK package, and fail on unexpected lockfile drift. Do not install an unreviewed latest SDK during CI.

### Step 4: Protect test evidence

Use synthetic prompts and media. Redact bearer values, signed output URLs, raw unsafe prompts, and provider responses before uploading artifacts; set a short artifact retention.

### Step 5: Isolate the live canary

Place it behind a protected environment, manual approval, trusted default-branch commit, explicit model schema, one-request ceiling, and concurrency lock. Never expose its secret to pull requests from forks.

### Step 6: Publish a decision

Report offline contract status separately from live provider status. A skipped canary is not a passing canary, and a created task is not a completed canary.

## Authentication

Ordinary CI receives no Runway credential. The protected canary obtains an organization-scoped key only after environment approval and uses server-side bearer authentication plus the reviewed version header.

## Tool Discipline

Use Read and Grep to inspect application configuration, provider documentation, lockfiles, fixtures, schemas, tests, and redacted operational evidence before proposing a change. Use Write or Edit only for an approved implementation, configuration, test, runbook, or redacted receipt. Do not create, cancel, delete, retry, deploy, rotate, revoke, publish, or otherwise mutate production Runway resources without explicit operator approval.

## Output

- Offline CI job covering payload, task, retry, cancellation, and storage contracts
- Protected canary policy with fork isolation, budget, and concurrency lock
- Redacted check summary that distinguishes offline, skipped, and live evidence

Return the environment, organization alias, operation and task identifiers, API and SDK versions, model or router policy, source-contract fingerprint, task-state evidence, credit boundary, output disposition, unresolved risk, rollback state, and final decision without exposing API secrets, prompt or media contents, or temporary signed URLs.

## Examples

A fork PR runs schema and state-machine fixtures but receives no secret. After merge, an authorized operator approves a single safe canary on the exact default-branch SHA; the workflow stores only the task ID, terminal state, checksum, and cost receipt.

## Error Handling

| Failure | Response |
| --- | --- |
| A fork job can read the secret | Disable the job immediately, rotate the key, and correct event and environment permissions. |
| Canary runs on every commit | Move it behind manual approval or a controlled schedule with a one-task budget. |
| CI records only task creation | Extend the gate to a bounded terminal-state and owned-output assertion. |

## Validation

Inspect effective workflow permissions, test a fork-equivalent event, run the offline lane with networking blocked, and prove the canary cannot exceed one approved request. Confirm uploaded artifacts contain no usable secret or signed URL.

## Resources

- [First-party source notes](references/official-docs.md)
- [Runway agent context](https://docs.dev.runwayml.com/ai-context.md)
- [API reference](https://docs.dev.runwayml.com/api.md)
- [Models](https://docs.dev.runwayml.com/guides/models.md)
- [Usage tiers](https://docs.dev.runwayml.com/usage/tiers.md)
- [Pricing](https://docs.dev.runwayml.com/guides/pricing.md)
- [Production checklist](https://docs.dev.runwayml.com/guides/go-live.md)
