---
name: together-core-workflow-a
description: >-
  Prepare, submit, monitor, and disposition a Together AI fine-tuning job using SDK v2, validated training data, explicit cost approval, and separate deployment verification. Use when adapting a model to custom examples or preferences. Trigger with "Together fine-tune", "train a Together model", or "Together DPO job".
argument-hint: "[repository-path] [training-file] [sft|dpo]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.9.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- together-ai
- fine-tuning
model: inherit
effort: high
compatibility: Designed for Claude Code; submission requires network access, a project key, training data, and funded Together AI usage
---
# Together AI Fine-Tuning Workflow

## Overview

This skill governs the expensive path from dataset qualification through an asynchronous fine-tune job and a separately approved serving handoff.

## Prerequisites

- A supported base model and tuning method confirmed in current Together documentation
- Sanitized, licensed training and optional validation JSONL
- Dataset-quality and holdout criteria
- A cost ceiling, job owner, cancellation rule, and deployment decision owner

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect data schemas, training configuration, and existing evaluations. Use `WebFetch` for current supported models and job parameters. Use `Write` or `Edit` only for approved data-validation, job-manifest, or evaluation files; never copy raw sensitive data into the skill output.

## Current Contract

- Use Together Python SDK v2 and `client.files.upload()` plus `client.fine_tuning.create()`.
- The CLI accepts a file ID or local path and reports an estimated price before confirmation.
- Prefer LoRA unless full tuning is justified; choose SFT or DPO from the behavior objective.
- A completed training job does not automatically deploy a model. Serving is a separate endpoint decision.

## Authentication

Fine-tuning APIs use the project-scoped `TOGETHER_API_KEY` Bearer credential. A W&B key, private Hugging Face token, or dataset-store credential is separate and must be scoped, stored, and redacted independently.

## Instructions

1. Define the target behavior, baseline evaluation, tuning method, and success threshold.
2. Validate format, licenses, consent, duplication, leakage, train/validation separation, and token distribution.
3. Confirm the base model is currently tunable and estimate cost before upload.
4. Upload with the fine-tune purpose and persist the returned file ID in a redacted manifest.
5. Submit only after approval; persist job ID, parameters, dataset hash, owner, and cancellation threshold.
6. Poll boundedly, review events/checkpoints, evaluate the output, and hand deployment off separately.

## Approval Boundaries

Do not upload data or confirm a paid job without dataset authority and cost approval. Do not deploy the resulting model or delete training artifacts automatically.

## Output

Return dataset checks, base model, method, estimated/approved cost, file and job references, terminal state, evaluation delta, and deployment recommendation.

## Error Handling

| Condition | Response |
|---|---|
| Dataset validation fails | Stop before upload and report line-level categories without sensitive rows. |
| Base model unsupported | Re-resolve the fine-tuning catalog; do not substitute silently. |
| Job cost exceeds ceiling | Do not confirm; reduce scope or seek approval. |
| Job fails or stalls | Capture events, stop bounded polling, and preserve IDs for support. |

## Examples

The example below shows the minimum redacted evidence expected from a successful invocation of this operator workflow.

```text
method=lora-sft; data=validated; estimate=approved; job=ft-redacted; deploy=not-started
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Fine-tuning CLI](https://docs.together.ai/reference/cli/finetune)
- [Fine-tune API](https://docs.together.ai/reference/post-fine-tunes)
- [Official fine-tuning skill](https://github.com/togethercomputer/skills/tree/main/skills/together-fine-tuning)
