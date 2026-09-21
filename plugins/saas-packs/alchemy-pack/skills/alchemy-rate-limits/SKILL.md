---
name: alchemy-rate-limits
description: >-
  Design account-aware Alchemy throttling, bounded retries, and admission control from observed throughput rather than stale plan constants. Use when preventing or handling rate limits. Trigger with "Alchemy rate limit", "Alchemy throughput", or "fix Alchemy 429s".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<traffic-class> <account> <slo>"
version: 2.0.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, alchemy, rate-limits, reliability]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Alchemy access requires network access, an appropriate credential, account capacity, and explicit approval"
---
# Alchemy Throughput and Backpressure Control

## Overview

Design account-aware Alchemy throttling, bounded retries, and admission control from observed throughput rather than stale plan constants. This workflow produces a reviewable artifact and negative-path evidence before any live side effect.

## Prerequisites

- Current first-party Alchemy documentation for the selected product, chain, feature, client, authentication method, limit, and lifecycle.
- Named product, application, security, data/privacy, budget, release, and operations owners appropriate to the requested scope.
- Synthetic or approved non-production fixtures, a credential canary, explicit success criteria, and a tested rollback boundary.

## Current Contract

Alchemy throughput is measured in compute units at the account level using a rolling ten-second token-bucket model. Method costs, plan allowances, and elastic behavior can change. A per-process requests-per-second limiter is therefore insufficient: control must use current account terms, method mix, shared consumers, response signals, and measured demand.

## Authentication

Usage inspection requires the authorized dashboard owner or an Admin access key for the documented Admin API; an application key is not an Admin credential. Never export account usage or credential material into public logs.

## Instructions

1. Inventory every workload sharing the account by method family, estimated current compute-unit cost, burst shape, priority, idempotency, and SLO.
2. Recheck current method costs, account throughput, plan terms, and elastic-demand behavior; record source date and observed tenant settings.
3. Create a shared admission budget across processes, reserve capacity for critical reads, and shed or defer background work before saturation.
4. Use concurrency limits plus bounded exponential backoff with jitter, honoring provider guidance and retrying only idempotent operations automatically.
5. Emit attempt count, queue time, response class, observed usage, and final disposition without logging credentials or full user payloads.
6. Load-test below, at, and above the approved envelope; prove recovery, exhausted-budget behavior, and rollback before changing production limits.

## Tool Discipline

Use Read, Glob, and Grep to inspect current documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Skill invocation alone does not authorize network access, credentials, wallet addresses, customer data, plan changes, spend, key creation or rotation, webhook changes, deployment, replay, transaction construction, signing, broadcast, or deletion.

## Approval Boundaries

Operations approves admission and retry policy; product approves degraded behavior. Purchasing capacity, enabling elastic spend, or changing account limits requires budget-owner approval.

## Error Handling

- Do not hardcode remembered free-plan throughput or method costs as a permanent limiter.
- Do not retry deterministic JSON-RPC errors or non-idempotent writes automatically.
- If independent processes cannot share a budget, set conservative partitions and document the risk of account-level contention.

## Output

Return the workload/CU inventory, dated account assumptions, shared admission design, retry matrix, telemetry, load evidence, spend boundary, degraded behavior, and rollback threshold. Mark assumptions, observations, source dates, environment-specific behavior, owners, and unresolved gaps explicitly.

## Examples

- Reserve throughput for customer reads while deferring a metadata backfill when the shared rolling window approaches its approved envelope.
- Demonstrate that a repeated `429` stops after the retry budget and returns an explicit degraded result rather than an infinite wait.

## Validation

Exercise and record expected and observed results for:

- short burst
- sustained saturation
- shared-worker contention
- 429 with retry guidance
- non-idempotent request
- retry budget exhausted

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated Alchemy sources before execution.
- Treat observed account, application, network, indexer, chain, or provider behavior as environment-specific evidence, never a universal guarantee.
