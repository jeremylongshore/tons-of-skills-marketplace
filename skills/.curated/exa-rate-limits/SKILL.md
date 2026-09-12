---
name: exa-rate-limits
description: >-
  Budget Exa throughput per endpoint and distinguish caller rate limiting from vendor overload and billing exhaustion. Use when operating or reviewing this Exa boundary. Trigger with "Exa rate limits", "review Exa rate limits", or "fix Exa rate limits".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<endpoint-mix> <target-throughput> <team>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, exa]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Exa work requires network access"
---
# Exa Endpoint Rate-limit Control

## Overview

Budget Exa throughput per endpoint and distinguish caller rate limiting from vendor overload and billing exhaustion. Treat credentials, queries, retrieved content, generated output, spend, and destructive state as separately governed boundaries.

## Prerequisites

- The target repository, environment, Exa team, product surface, and accountable owner.
- The workload's data classification, latency and freshness promise, cost ceiling, and retention policy.
- Current first-party documentation plus credentials only for a narrowly approved live check.

## Current Contract

Published defaults are 10 QPS for /search, 100 QPS for /contents, and 10 QPS for /answer, while enterprise limits may differ. A 429 can reflect API-key, team, or network limits and should honor Retry-After when present. A 503 SERVICE_OVERLOADED is a separate capacity signal.

## Authentication

For normal REST work, inject `EXA_API_KEY` from an approved server-side secret manager and send it only as `Authorization: Bearer` to the configured first-party Exa API host. Team Management service keys, hosted MCP OAuth or enterprise managed authorization, and payment-protocol calls are separate trust models. Never print, commit, place in a URL, or expose a credential to an untrusted client.

## Instructions

1. Inventory endpoint mix, team limits, key-specific controls, concurrency, and burst shape.
2. Set independent token buckets for Search, Contents, Answer, Agent, and administrative traffic.
3. Bound queues and propagate deadlines instead of allowing hidden backlog growth.
4. Honor Retry-After and use capped jitter only for retryable classes.
5. Measure attempts, completions, throttles, overloads, queue age, and cost together.
6. Request a limit change only with measured demand and an owner-approved capacity plan.

## Tool Discipline

Use Read, Glob, and Grep to inspect repository code, configuration, fixtures, and evidence. Use Write and Edit only for approved implementation or documentation changes. Do not call Exa, run paid research, create or alter a Monitor, Webset, Agent run, Batch, team, member, API key, budget, webhook, or deployment merely because this skill was invoked.

## Approval Boundaries

Require an accountable owner before live queries involving sensitive intent, production credentials, spend or rate-limit changes, forced live crawling, generated summaries, external delivery, deployment, member or key changes, schedule creation, or destructive cancellation, stopping, deletion, or revocation. Read-only repository inspection and synthetic offline validation do not authorize live vendor actions.

## Failure Modes

- Adding keys does not prove that team or network capacity increased.
- Retrying 402 or invalid 400 requests wastes capacity and money.
- Global throttling can let a high-volume Contents job starve interactive Search.

## Output

Return the operation scope, environment, team and product surface, authorization class, contract and policy decisions, deterministic validation results, content-free identifiers, status and cost counts, risks, cleanup or rollback state, and a concise pass or fail receipt. Exclude credentials, raw queries, prompts, presigned URLs, retrieved content, generated output, and customer-derived data unless separately approved.

## Example

- Give interactive Search its own 10-QPS budget and run Contents backfills through a separately bounded queue.
- Finish with request or resource IDs, assertion counts, cost and terminal state, rollback or deletion status, and the decision owner; never reproduce secrets or retrieved content.

## Validation

Rerun the smallest relevant deterministic test, compare actual behavior with the requested outcome and current first-party contract, verify sensitive fields are absent from evidence, and confirm deadlines, terminal state, downstream retention, and rollback before reporting success.

## References

Review the dated first-party evidence map before relying on any endpoint, parameter, search type, price, limit, beta, compliance, identity, retry, or lifecycle claim.

- [Current first-party evidence map](references/official-docs.md)
