---
name: notion-performance-tuning
description: >-
  Improve Notion integration latency and throughput while preserving completeness, fairness, and limit compliance. Use when measured operations miss performance objectives. Trigger with "tune Notion performance", "reduce Notion latency", or "optimize Notion pagination".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<operation> <measurement-window> <objective>"
version: 1.40.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, notion, performance]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Notion actions require network access and explicit approval"
---
# Notion Evidence-Driven Performance Tuning

## Overview

Improve Notion integration latency and throughput while preserving completeness, fairness, and limit compliance.. This workflow produces an auditable decision or artifact before any live action.

## Prerequisites

- Current first-party Notion documentation and the selected integration's tested API-version contract.
- A named workspace owner, content or data owner, and operation owner.
- Synthetic or approved non-production fixtures with secrets and workspace content removed.

## Current Contract

Performance depends on operation type, pagination and recursion, response size, rate pressure, network latency, queueing, downstream processing, and cache behavior. The observed bottleneck must select the optimization. Recheck the dated evidence map before relying on mutable fields, endpoints, versions, limits, or delivery behavior.

## Authentication

Use redacted telemetry and synthetic benchmarks. Content caches require classification, encryption, tenant isolation, expiry, and deletion behavior.

## Instructions

1. Record latency distributions, requests per business operation, pages, bytes, errors, retries, and queue wait.
2. Identify whether the constraint is Notion calls, pagination, block recursion, transformation, cache, queue, or destination.
3. Choose one intervention: narrower query, checkpoint, concurrency bound, cache, batch, webhook signal, or downstream optimization.
4. State consistency, freshness, completeness, fairness, and memory tradeoffs.
5. Canary against a representative synthetic or approved non-production workload.
6. Compare before and after, exercise rollback, and reject regressions hidden by averages.

## Tool Discipline

Use Read, Glob, and Grep to inspect documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Invocation alone does not authorize network access, credentials, workspace content, user data, file transfer, deployment, capability or sharing changes, writes, spend, or deletion.

## Approval Boundaries

Require approval before caching content, increasing concurrency, changing freshness, adding subscriptions, or benchmarking a live tenant.

## Error Handling

- Do not parallelize until Retry-After and tenant fairness are enforced.
- Do not optimize away required pagination or reconciliation.
- Stop if tail latency, error rate, or completeness worsens.

## Output

Return the baseline, bottleneck evidence, experiment, tradeoffs, measured result, safe envelope, and rollback threshold. Identify assumptions, owners, expirations, and evidence gaps explicitly.

## Examples

- Reduce block-recursion amplification by fetching only required page content.
- Cache stable schema metadata without caching sensitive row content.

## Validation

Exercise and record these paths with expected and observed results:

- cold cache
- warm cache
- multi-page
- 429
- downstream stall
- rollback

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources before relying on mutable behavior.
- Treat observed tenant behavior as environment-specific evidence, never a universal Notion guarantee.
