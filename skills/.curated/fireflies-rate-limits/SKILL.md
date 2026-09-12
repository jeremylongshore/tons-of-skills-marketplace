---
name: fireflies-rate-limits
description: >-
  Monitor and enforce current Fireflies plan and operation-specific request limits with bounded concurrency, retryAfter handling, and cost-aware pagination. Use when preventing throttling or recovering from 429-style failures. Trigger with "Fireflies rate limit", "too_many_requests", or "budget Fireflies calls".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<repository-path> <workflow-scope>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, fireflies, rate-limits, reliability]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Fireflies work requires network access"
---
# Fireflies Request Budget and Backoff

## Overview

Enforce current Fireflies plan and operation-specific request limits with bounded concurrency, retryAfter handling, and cost-aware pagination.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The Fireflies principal, team, environment, and data classification for the work.
- Current Fireflies documentation, credentials only when needed, and an accountable approver.

## Current Contract

General documented limits are 50 requests/day for Free and Pro and 60 requests/minute for Business and Enterprise. addToLiveMeeting is 3 requests per 20 minutes, shareMeeting is 10/hour, and deleteTranscript is 10/minute. Treat docs and retryAfter as authoritative over hard-coded assumptions.

## Authentication

For authenticated operations, inject `FIREFLIES_API_KEY` from an approved secret manager and send it only as `Authorization: Bearer REDACTED_KEY` to `https://api.fireflies.ai/graphql`. Never print, commit, place in a URL, forward to a browser, or include the key in evidence. Webhook signing secrets are separate credentials and must not be reused as API keys.

## Instructions

1. Identify the plan and every operation-specific bucket used by the workload.
2. Set a conservative request budget and concurrency of one until measured.
3. Use pagination caps and field minimization to avoid unnecessary calls.
4. On too_many_requests, honor retryAfter when supplied and add bounded jitter.
5. Do not retry auth, privilege, invalid-argument, object-not-found, or AI-credit errors.
6. Export per-operation usage, throttles, wait time, and exhausted-budget metrics.
7. Load-test only against synthetic or approved data within a separate budget.

## Tool Discipline

Use Read, Glob, and Grep to inspect code, configuration, tests, and evidence. Use Write/Edit only for approved implementation or documentation changes. Do not query Fireflies, retrieve meeting content, create an AskFred thread, upload media, change account state, replay an event, or deploy merely because this skill was invoked.

## Approval Boundaries

Require approval before increasing concurrency, consuming a large daily quota, load testing, or changing the subscribed plan.

## Output

Return the exact operation or event surface, environment, authorization class, selected field groups, validation results, content-free metrics, decisions, and a concise pass/fail receipt. Keep secrets and meeting-derived content out of general output.

## Validation

Before reporting success, rerun the smallest relevant deterministic check, compare actual state with the requested outcome and current contract, verify no secret or meeting-derived content entered logs or artifacts, and record unresolved uncertainty explicitly.

## Error Handling

- No retryAfter: use a conservative documented window and bounded attempts.
- Daily quota exhausted: stop until reset or owner decision.
- Mutation outcome unknown after timeout: reconcile state before replay.

## Examples

- "Review fireflies request budget and backoff" produces a bounded plan and redacted receipt.
- A request that widens access or mutates production is paused at the approval boundary.

## Resources

Read [official Fireflies.ai evidence](references/official-docs.md) before relying on a field, filter, event, permission, plan limit, mutation, or processing state.
