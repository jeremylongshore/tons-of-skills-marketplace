---
name: together-webhooks-events
description: >-
  Convert Together AI batch, fine-tuning, upload, and dedicated-deployment job states into idempotent internal events using bounded polling and an optional owned callback. Use when integrating asynchronous Together work. Trigger with "Together job events", "Together callback", or "poll Together status".
argument-hint: "[repository-path] [batch|fine-tune|upload|deployment]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.9.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- together-ai
- asynchronous-jobs
model: inherit
effort: high
compatibility: Designed for Claude Code; polling requires authorized Together AI project access
---
# Together AI Job Events

## Overview

Together documents asynchronous retrieval and polling for batch, fine-tune, upload, and deployment state. This skill emits internal events from that source of truth instead of inventing a provider-signed webhook.

## Prerequisites

- The job type, ID, project, terminal states, and retrieval method
- A durable cursor/state store and idempotency key policy
- Poll interval, deadline, retry budget, and event retention policy
- An owned callback endpoint only if downstream push delivery is required

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect job persistence, pollers, queues, and callback handlers. Use `WebFetch` to confirm current job states and retrieval methods. Use `Write` or `Edit` only after the event contract and storage boundary are approved.

## Current Contract

- Do not expect a universal Together webhook signature header; no general signed webhook surface is documented for these job APIs.
- Persist the provider job ID before polling and derive internal idempotency from job ID plus observed state/version.
- Treat terminal job status and per-item output/error artifacts as separate facts.
- Deliver downstream callbacks from infrastructure you own and authenticate them with your own signing scheme.

## Authentication

Poll Together with the project-scoped `TOGETHER_API_KEY` Bearer credential. For an owned callback, use a separate secret, timestamped signature, replay window, and rotation plan; never present that signature as Together-generated.

## Instructions

1. Map provider job states to a small versioned internal event schema.
2. Persist job ID, last observed state, next poll time, attempt count, and deadline.
3. Retrieve with bounded exponential backoff and jitter; stop at terminal state or deadline.
4. Emit only on meaningful transitions and deduplicate by job/state key.
5. On completion, fetch output and error artifacts before declaring record-level success.
6. If needed, sign and deliver an internal callback with replay protection and a dead-letter path.

## Approval Boundaries

Do not expose the Together key to callback consumers, invent provider signatures, or delete remote/local job artifacts before reconciliation and retention approval.

## Output

Return the provider job reference, state mapping, poll schedule, transition ledger, reconciliation status, callback delivery evidence, and deadline/dead-letter disposition.

## Error Handling

| Condition | Response |
|---|---|
| Retrieval is transiently unavailable | Retry with jitter inside the overall deadline. |
| Job ID is missing | Stop; do not create a replacement job automatically. |
| Completion has an error file | Emit completed-with-errors and reconcile records. |
| Callback repeatedly fails | Preserve the event in a dead-letter queue for replay. |

## Examples

The example below shows the minimum redacted evidence expected from a successful invocation of this operator workflow.

```text
job=batch-redacted; transition=IN_PROGRESS->COMPLETED; records=reconciled; callback=owned-signed
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Batch tutorial](https://docs.together.ai/docs/inference/batch/tutorial)
- [Fine-tuning lifecycle](https://docs.together.ai/reference/cli/finetune)
- [Dedicated Model Inference](https://docs.together.ai/docs/dedicated-endpoints/overview)
