---
name: assemblyai-rate-limits
description: >-
  Analyze and control AssemblyAI account request limits, concurrency, backoff, and admission queues. Use when handling 429s or planning throughput. Trigger with "AssemblyAI rate limit", "AssemblyAI concurrency", or "AssemblyAI backoff".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<workload-profile> <account-tier>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, assemblyai]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live AssemblyAI work requires network access"
---
# AssemblyAI Capacity and Retry Control

## Overview

Control capacity with explicit account limits, queues, and retry budgets. Keep data, credentials, spend, and replay decisions separately governed.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The AssemblyAI project, environment, region, data classification, and accountable owner.
- Current first-party documentation plus credentials only for a narrowly approved live check.

## Current Contract

AssemblyAI documents 20,000 API requests per five minutes plus operation-specific concurrency limits. Limits apply at account level; project keys mirror capacity rather than multiply it. Actual concurrency and autoscaling are account-specific, so use current dashboard and documentation evidence.

## Authentication

For live work, inject `ASSEMBLYAI_API_KEY` from an approved secret manager and send the raw value only in the AssemblyAI `Authorization` header to the configured first-party host. Never print, commit, place in a URL, or expose it to an untrusted client. Callback secrets and temporary streaming tokens are separate credentials.

## Instructions

1. Inventory submissions, polls, callbacks, gateway calls, and streaming concurrency.
2. Record current account limits and observed headers.
3. Allocate separate bounded pools by operation class.
4. Prefer callbacks to aggressive polling and use durable admission queues.
5. Honor `Retry-After` or capped exponential backoff with jitter.
6. Reconcile transcript IDs before retrying submission and alert on saturation.

## Tool Discipline

Use Read, Glob, and Grep to inspect repository code, configuration, fixtures, and evidence. Use Write and Edit only for approved implementation or documentation changes. Do not call AssemblyAI, upload audio, open a streaming session, mint a token, replay a callback, deploy, rotate a key, or delete a transcript merely because this skill was invoked.

## Approval Boundaries

Require an accountable owner before live audio processing, production credential or endpoint changes, paid model or capacity changes, content retention, callback replay, deployment, or deletion. Read-only repository inspection and synthetic offline validation do not authorize live vendor actions.

## Failure Modes

- More keys do not create more account capacity.
- Auth and validation failures are not retryable.
- Unbounded polling amplifies outages and competes with submissions.

## Output

Return the operation scope, environment, region, contract surface, authorization class, model and feature decisions, deterministic validation results, content-free identifiers, risks, cleanup or rollback state, and a concise pass/fail receipt. Exclude credentials, signed URLs, audio, transcript text, prompts, and customer-derived content.

## Example

- Start with the named environment, approved regional host, synthetic fixture identity, and bounded operation budget.
- Finish with safe IDs, contract and assertion counts, terminal state, cleanup status, and the decision owner; never reproduce speech content.

## Validation

Rerun the smallest relevant deterministic check, compare actual state with the requested outcome and current first-party contract, verify sensitive fields are absent from evidence, and confirm rollback, termination, or deletion state before reporting success.

## References

Review the dated first-party evidence map before relying on any model, parameter, limit, price, region, or lifecycle claim.

- [Current first-party evidence map](references/official-docs.md)
