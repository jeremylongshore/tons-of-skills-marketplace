---
name: exa-hello-world
description: >-
  Prove a new Exa Search integration with a bounded synthetic query and content-free assertions. Use when operating or reviewing this Exa boundary. Trigger with "Exa hello world", "review Exa hello world", or "fix Exa hello world".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<synthetic-query> <environment>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, exa]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Exa work requires network access"
---
# Exa Search Smoke Test

## Overview

Prove a new Exa Search integration with a bounded synthetic query and content-free assertions. Treat credentials, queries, retrieved content, generated output, spend, and destructive state as separately governed boundaries.

## Prerequisites

- The target repository, environment, Exa team, product surface, and accountable owner.
- The workload's data classification, latency and freshness promise, cost ceiling, and retention policy.
- Current first-party documentation plus credentials only for a narrowly approved live check.

## Current Contract

POST /search requires a query and defaults to type auto. New code should not select legacy neural terminology. A successful smoke test checks requestId, bounded results, valid HTTP(S) URLs, and costDollars rather than snapshotting volatile rankings or page text.

## Authentication

For normal REST work, inject `EXA_API_KEY` from an approved server-side secret manager and send it only as `Authorization: Bearer` to the configured first-party Exa API host. Team Management service keys, hosted MCP OAuth or enterprise managed authorization, and payment-protocol calls are separate trust models. Never print, commit, place in a URL, or expose a credential to an untrusted client.

## Instructions

1. Define a non-sensitive query with a stable topical expectation.
2. Set an explicit result cap and omit content extraction for the first probe.
3. Submit one authorized request through the application adapter.
4. Validate requestId, result count, URL schemes, and the cost field.
5. Repeat only once when the failure is explicitly retryable.
6. Delete transient output and retain only content-free evidence.

## Tool Discipline

Use Read, Glob, and Grep to inspect repository code, configuration, fixtures, and evidence. Use Write and Edit only for approved implementation or documentation changes. Do not call Exa, run paid research, create or alter a Monitor, Webset, Agent run, Batch, team, member, API key, budget, webhook, or deployment merely because this skill was invoked.

## Approval Boundaries

Require an accountable owner before live queries involving sensitive intent, production credentials, spend or rate-limit changes, forced live crawling, generated summaries, external delivery, deployment, member or key changes, schedule creation, or destructive cancellation, stopping, deletion, or revocation. Read-only repository inspection and synthetic offline validation do not authorize live vendor actions.

## Failure Modes

- HTTP 200 does not prove relevance or freshness.
- Exact rank and title snapshots are brittle because the web index changes.
- A live smoke test without an approved budget is not an offline validation.

## Output

Return the operation scope, environment, team and product surface, authorization class, contract and policy decisions, deterministic validation results, content-free identifiers, status and cost counts, risks, cleanup or rollback state, and a concise pass or fail receipt. Exclude credentials, raw queries, prompts, presigned URLs, retrieved content, generated output, and customer-derived data unless separately approved.

## Example

- Search for a public standards topic with type auto and three results, then assert shape and topical domains without storing returned text.
- Finish with request or resource IDs, assertion counts, cost and terminal state, rollback or deletion status, and the decision owner; never reproduce secrets or retrieved content.

## Validation

Rerun the smallest relevant deterministic test, compare actual behavior with the requested outcome and current first-party contract, verify sensitive fields are absent from evidence, and confirm deadlines, terminal state, downstream retention, and rollback before reporting success.

## References

Review the dated first-party evidence map before relying on any endpoint, parameter, search type, price, limit, beta, compliance, identity, retry, or lifecycle claim.

- [Current first-party evidence map](references/official-docs.md)
