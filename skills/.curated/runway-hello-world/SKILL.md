---
name: runway-hello-world
description: >-
  Create, observe, and preserve one approved Runway text-to-video task using the current per-model contract. Use when proving the first billable generation path. Trigger with: "Runway hello world", "first Runway video", "smoke test Runway generation".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[prompt-and-model-policy]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - runway
  - video-generation
  - smoke-test
  - tasks
compatibility: 'Requires server-side Runway Dev access, current first-party documentation, an approved credit budget, and controlled media storage.'
---

# One Controlled Runway Generation

## Overview

Prove the minimum asynchronous generation path without pretending that task creation is completion. A Runway generation consumes credits and may be moderated, so the smoke test requires an explicit cost ceiling, safe prompt, terminal-state evidence, and owned output storage.

## Prerequisites

- Server-side Runway authentication and available organization credits
- An operator-approved model, prompt, duration, ratio, and maximum credit budget
- Durable task storage and an output bucket with retention controls

## Instructions

### Step 1: Read the current model schema

Open the current models guide and the exact `text_to_video` model variant in the API reference. Confirm model identifier, required fields, prompt limit, ratio set, duration range, and price immediately before the test.

### Step 2: Freeze the billable intent

Record a unique operation ID, normalized request fingerprint, model, duration, ratio, estimated ceiling, and approval. Use `gen4.5` only when its current schema still matches the request; never revive retired `gen3a_turbo`.

### Step 3: Create one task

Submit one server-side request. Persist the returned task ID before waiting. Treat the create response as acceptance into the task system, not a generated asset.

### Step 4: Wait with a bound

Use the SDK wait helper or poll `GET /v1/tasks/<task-id>` no more frequently than every five seconds with jitter and backoff. Set a deadline. Remember that a client timeout does not cancel the provider task.

### Step 5: Classify the terminal state

Accept output only from `SUCCEEDED`. For `FAILED`, retain redacted `failureCode` and diagnostic text; for `CANCELLED`, record who cancelled. Treat `THROTTLED` as queued, not failed.

### Step 6: Own the output

Download successful output promptly, validate type and size, store it under the operation ID, and retain the source URL only as sensitive temporary evidence because Runway output URLs expire.

## Authentication

Create and task-read requests use the server-side bearer secret and reviewed Runway API version. Never expose the key or temporary signed output URL to an untrusted browser, log stream, or ticket.

## Tool Discipline

Use Read and Grep to inspect application configuration, provider documentation, lockfiles, fixtures, schemas, tests, and redacted operational evidence before proposing a change. Use Write or Edit only for an approved implementation, configuration, test, runbook, or redacted receipt. Do not create, cancel, delete, retry, deploy, rotate, revoke, publish, or otherwise mutate production Runway resources without explicit operator approval.

## Output

- Task ID, request fingerprint, approval, and observed state timeline
- Terminal-state classification with cost and moderation evidence
- Owned output object and checksum, or a redacted failure receipt

Return the environment, organization alias, operation and task identifiers, API and SDK versions, model or router policy, source-contract fingerprint, task-state evidence, credit boundary, output disposition, unresolved risk, rollback state, and final decision without exposing API secrets, prompt or media contents, or temporary signed URLs.

## Examples

An operator approves one five-second `gen4.5` test under a fixed credit ceiling. The worker persists the task ID, observes `PENDING`, `RUNNING`, and `SUCCEEDED`, copies the video into private storage, and records its checksum without publishing the temporary provider URL.

## Error Handling

| Failure | Response |
| --- | --- |
| Task stays `THROTTLED` | Keep the task queued, observe concurrency and daily limits, and do not submit duplicates. |
| Wait helper times out | Retrieve the saved task ID later or explicitly cancel it; timeout did not cancel the task. |
| Task fails moderation | Do not retry the same prompt; record the safety code without exposing unsafe content and review policy. |

## Validation

Replay the workflow with a safe approved canary, prove task ID persistence before polling, exercise one mocked failure and timeout path, and confirm the stored output remains available after discarding the temporary URL.

## Resources

- [First-party source notes](references/official-docs.md)
- [Runway agent context](https://docs.dev.runwayml.com/ai-context.md)
- [API reference](https://docs.dev.runwayml.com/api.md)
- [Models](https://docs.dev.runwayml.com/guides/models.md)
- [Usage tiers](https://docs.dev.runwayml.com/usage/tiers.md)
- [Pricing](https://docs.dev.runwayml.com/guides/pricing.md)
- [Production checklist](https://docs.dev.runwayml.com/guides/go-live.md)
