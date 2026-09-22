---
name: mistral-rate-limits
description: >-
  Control Mistral demand with live workspace limits, token-aware admission, bounded retry, and backpressure. Use when handling throttling or sizing throughput. Trigger with "Mistral rate limits", "fix Mistral 429s", or "design Mistral backpressure".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<workspace> <operation> <latency-slo>"
version: 1.14.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, mistral, reliability]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live or external Mistral actions require network access and explicit approval"
---
# Mistral Rate and Backpressure Control

## Overview

Treat provider limits as shared workspace capacity, not constants. Admit work against measured demand, preserve deadlines and fairness, and shed load before retry storms consume remaining budget.

## Prerequisites

- Current workspace request, token, and spend limits from the Admin Panel.
- Per-operation deadline, priority, idempotency, and maximum-attempt policy.
- Metrics for admitted, queued, throttled, retried, completed, and abandoned work.

## Current Contract

Mistral documents workspace-shared limits across API keys and reports current dimensions in the Admin Panel. Limits vary; never encode a numeric example as a default.

## Authentication

Limit telemetry excludes keys, prompts, responses, and files. Admin inspection requires separate authorized identity.

## Instructions

1. Capture current workspace limits and evidence time as observations.
2. Measure demand by operation, model, requests, tokens, and concurrency.
3. Define shared admission buckets and bounded queues with tenant fairness.
4. Honor explicit retry timing; otherwise use capped jitter only for safe transient failures.
5. Stop when deadline, attempt, token, or spend budget ends; return typed overload.
6. Load-test locally, then canary approved traffic and compare queue/SLO evidence.

## Tool Discipline

Use Read, Glob, and Grep to inspect code, locks, configuration, tests, and evidence. Use Write and Edit only for approved repository changes. Invocation alone does not authorize network calls, paid usage, uploads, stateful resources, admin mutations, deployments, or deletion.

## Approval Boundaries

Require approval for live load, limit increases, capacity changes, or fallback models. Additional keys do not create independent capacity.

## Error Handling

- Per-process limiters oversubscribe shared capacity across replicas.
- Retries after the user deadline waste tokens and worsen overload.
- Fallback changes quality, residency, context, and cost.

## Output

Return dated observed limits, demand profile, admission/retry policy, queue bounds, shed behavior, SLO evidence, and rollback.

## Examples

- Prioritize interactive work over approved batch preparation.
- Return overload once the deadline cannot survive the queue.

## Validation

Simulate bursts, replicas, `429`, missing retry metadata, cancellation, deadline expiry, and budget exhaustion offline. Prove that admission resumes gradually after recovery.

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources before relying on mutable endpoints, models, limits, prices, preview status, or retention.
- Record live account observations as environment-specific evidence, not universal Mistral guarantees.
