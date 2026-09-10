---
name: together-core-workflow-b
description: >-
  Run Together AI asynchronous batch inference from validated JSONL through upload, job polling, output/error download, and custom-id reconciliation. Use when bulk work can trade latency for lower cost. Trigger with "Together batch inference", "bulk Together requests", or "Together Batch API".
argument-hint: "[input-jsonl] [endpoint] [output-directory]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.9.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- together-ai
- batch-inference
model: inherit
effort: high
compatibility: Designed for Claude Code; job submission requires network access, a project key, and funded Together AI usage
---
# Together AI Batch Inference

## Overview

This skill converts independent offline requests into a recoverable Batch API job and reconciles every success and failure without relying on output order.

## Prerequisites

- Independent request records suitable for asynchronous processing
- A currently batch-eligible model and supported endpoint
- Stable unique `custom_id` values and an approved output location
- A request/token budget, retention policy, and job owner

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect input generation, schemas, and reconciliation code. Use `WebFetch` for current batch eligibility and SDK response shapes. Use `Write` or `Edit` only for approved JSONL, manifests, or reconciliation logic; avoid placing sensitive prompts in diagnostic output.

## Current Contract

- Each JSONL line contains a unique `custom_id` and a request `body`.
- Upload with `purpose="batch-api"`; create with `client.batches.create()` and the target endpoint.
- Results can arrive in arbitrary order. Join by `custom_id`.
- A `COMPLETED` batch can still have per-request failures in `error_file_id`; inspect both files.

## Authentication

File and batch APIs use the project-scoped `TOGETHER_API_KEY` as a Bearer credential. Keep remote file IDs and batch IDs as operational references, but redact the credential and sensitive request bodies.

## Instructions

1. Confirm requests are independent and the chosen model is currently batch eligible.
2. Validate JSONL syntax, endpoint body schema, unique IDs, request count, and token bounds locally.
3. Upload the file with batch purpose and record its hash and returned file ID.
4. Create the job with the uploaded ID and exact API endpoint; persist the returned batch ID.
5. Poll status with bounded backoff until terminal, without assuming the usual completion time.
6. Download output and error files, reconcile all IDs, verify counts, and apply retention cleanup.

## Approval Boundaries

Do not upload regulated or customer data without approval. Do not resubmit an ambiguous job: first reconcile the prior batch ID to avoid duplicate spend.

## Output

Return input hash/count, endpoint, model, file and batch references, terminal state, success/error counts, reconciliation result, cost evidence, and cleanup disposition.

## Error Handling

| Condition | Response |
|---|---|
| JSONL validation fails | Stop before upload and report offending line numbers. |
| Model is not batch eligible | Choose another model explicitly or use synchronous inference. |
| Polling deadline expires | Preserve the batch ID and hand off; do not create a duplicate. |
| IDs do not reconcile | Quarantine outputs and identify missing, duplicate, and unknown IDs. |

## Examples

The example below shows the minimum redacted evidence expected from a successful invocation of this operator workflow.

```text
input=10000; uploaded=10000; terminal=COMPLETED; success=9974; error=26; reconciled=10000
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Batch overview](https://docs.together.ai/docs/inference/batch/overview)
- [Batch tutorial](https://docs.together.ai/docs/inference/batch/tutorial)
- [Official batch skill](https://github.com/togethercomputer/skills/tree/main/skills/together-batch-inference)
