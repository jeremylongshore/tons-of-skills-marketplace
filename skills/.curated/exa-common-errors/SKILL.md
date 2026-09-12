---
name: exa-common-errors
description: >-
  Classify Exa failures by HTTP status, error tag, endpoint, and per-item crawl status before deciding whether to repair, retry, or escalate. Use when operating or reviewing this Exa boundary. Trigger with "Exa common errors", "review Exa common errors", or "fix Exa common errors".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<status-code> <error-tag> <request-id>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, exa]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Exa work requires network access"
---
# Exa Error and Status Decision Tree

## Overview

Classify Exa failures by HTTP status, error tag, endpoint, and per-item crawl status before deciding whether to repair, retry, or escalate. Treat credentials, queries, retrieved content, generated output, spend, and destructive state as separately governed boundaries.

## Prerequisites

- The target repository, environment, Exa team, product surface, and accountable owner.
- The workload's data classification, latency and freshness promise, cost ceiling, and retention policy.
- Current first-party documentation plus credentials only for a narrowly approved live check.

## Current Contract

Documented errors distinguish invalid requests, authentication, exhausted credits or budgets, access policy, per-URL crawl failure, rate limiting, service overload, and Answer generation failure. Most errors include requestId, error, and tag; 429 can use a simpler body. Contents also reports granular statuses inside a successful response.

## Authentication

For normal REST work, inject `EXA_API_KEY` from an approved server-side secret manager and send it only as `Authorization: Bearer` to the configured first-party Exa API host. Team Management service keys, hosted MCP OAuth or enterprise managed authorization, and payment-protocol calls are separate trust models. Never print, commit, place in a URL, or expose a credential to an untrusted client.

## Instructions

1. Capture endpoint, status, tag, request ID, attempt, and content-free input shape.
2. Separate request defects from auth, billing, policy, crawl, and capacity classes.
3. Repair 400-class contract errors instead of retrying them unchanged.
4. Honor Retry-After for 429 and use bounded jitter for documented transient failures.
5. Inspect Contents statuses even when the outer request succeeded.
6. Escalate persistent vendor failures with request IDs and redacted timing evidence.

## Tool Discipline

Use Read, Glob, and Grep to inspect repository code, configuration, fixtures, and evidence. Use Write and Edit only for approved implementation or documentation changes. Do not call Exa, run paid research, create or alter a Monitor, Webset, Agent run, Batch, team, member, API key, budget, webhook, or deployment merely because this skill was invoked.

## Approval Boundaries

Require an accountable owner before live queries involving sensitive intent, production credentials, spend or rate-limit changes, forced live crawling, generated summaries, external delivery, deployment, member or key changes, schedule creation, or destructive cancellation, stopping, deletion, or revocation. Read-only repository inspection and synthetic offline validation do not authorize live vendor actions.

## Failure Modes

- A 402 is a credit or budget boundary, not a transient server error.
- A 503 SERVICE_OVERLOADED is not fixed by merely lowering the caller's QPS.
- Never include API keys, full queries, or returned page text in support evidence.

## Output

Return the operation scope, environment, team and product surface, authorization class, contract and policy decisions, deterministic validation results, content-free identifiers, status and cost counts, risks, cleanup or rollback state, and a concise pass or fail receipt. Exclude credentials, raw queries, prompts, presigned URLs, retrieved content, generated output, and customer-derived data unless separately approved.

## Example

- Classify 429 RATE_LIMIT_EXCEEDED separately from 503 SERVICE_OVERLOADED and apply different operator actions.
- Finish with request or resource IDs, assertion counts, cost and terminal state, rollback or deletion status, and the decision owner; never reproduce secrets or retrieved content.

## Validation

Rerun the smallest relevant deterministic test, compare actual behavior with the requested outcome and current first-party contract, verify sensitive fields are absent from evidence, and confirm deadlines, terminal state, downstream retention, and rollback before reporting success.

## References

Review the dated first-party evidence map before relying on any endpoint, parameter, search type, price, limit, beta, compliance, identity, retry, or lifecycle claim.

- [Current first-party evidence map](references/official-docs.md)
