---
name: notion-rate-limits
description: >-
  Implement adaptive Notion request throttling and bounded retry behavior from observed responses. Use when handling 429s, queue pressure, or bursty workloads. Trigger with "handle Notion rate limits", "throttle Notion requests", or "fix Notion 429".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<workload> <queue> <service-objective>"
version: 1.40.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, notion, retries]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Notion actions require network access and explicit approval"
---
# Notion Rate-Limit and Retry Control

## Overview

Implement adaptive Notion request throttling and bounded retry behavior from observed responses.. This workflow produces an auditable decision or artifact before any live action.

## Prerequisites

- Current first-party Notion documentation and the selected integration's tested API-version contract.
- A named workspace owner, content or data owner, and operation owner.
- Synthetic or approved non-production fixtures with secrets and workspace content removed.

## Current Contract

Notion documents an average per-connection request rate, allows some bursts, returns 429 for rate pressure, and supplies Retry-After. Limits may change, so the runtime response is authoritative. Recheck the dated evidence map before relying on mutable fields, endpoints, versions, limits, or delivery behavior.

## Authentication

Throttle by approved connection and tenant boundary; never log tokens or create extra credentials to bypass a limit.

## Instructions

1. Measure requests by operation, tenant, outcome, Retry-After, latency, retry, and queue age.
2. Classify retryable rate and transient service failures separately from permanent input or access failures.
3. Use a shared limiter with bounded concurrency, tenant fairness, jitter, and a strict attempt and elapsed-time budget.
4. Honor Retry-After as the minimum wait and reduce future pressure after repeated limits.
5. Preserve idempotency and acknowledgement state before retrying writes.
6. Test recovery, saturation, cancellation, restart, and downstream backpressure.

## Tool Discipline

Use Read, Glob, and Grep to inspect documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Invocation alone does not authorize network access, credentials, workspace content, user data, file transfer, deployment, capability or sharing changes, writes, spend, or deletion.

## Approval Boundaries

Require platform approval before increasing concurrency or queue depth; require operation-owner approval before replaying writes or changing freshness objectives.

## Error Handling

- Never retry every 4xx response.
- Do not sleep while holding an unrenewed job lease.
- Stop and shed or defer load when the retry budget is exhausted.

## Output

Return the limiter policy, retry matrix, fairness model, measurements, saturation behavior, and rollback configuration. Identify assumptions, owners, expirations, and evidence gaps explicitly.

## Examples

- Honor a larger Retry-After value than the local backoff produced.
- Quarantine a permanent validation error instead of retrying it.

## Validation

Exercise and record these paths with expected and observed results:

- burst
- sustained load
- Retry-After
- write timeout
- cancellation
- restart

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources before relying on mutable behavior.
- Treat observed tenant behavior as environment-specific evidence, never a universal Notion guarantee.
