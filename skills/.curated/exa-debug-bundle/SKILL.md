---
name: exa-debug-bundle
description: >-
  Produce a minimal Exa diagnostic bundle that preserves reproducibility without exposing credentials, queries, retrieved content, or customer data. Use when operating or reviewing this Exa boundary. Trigger with "Exa debug bundle", "review Exa debug bundle", or "fix Exa debug bundle".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<incident-window> <request-ids>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, exa]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Exa work requires network access"
---
# Exa Privacy-safe Debug Bundle

## Overview

Produce a minimal Exa diagnostic bundle that preserves reproducibility without exposing credentials, queries, retrieved content, or customer data. Treat credentials, queries, retrieved content, generated output, spend, and destructive state as separately governed boundaries.

## Prerequisites

- The target repository, environment, Exa team, product surface, and accountable owner.
- The workload's data classification, latency and freshness promise, cost ceiling, and retention policy.
- Current first-party documentation plus credentials only for a narrowly approved live check.

## Current Contract

Useful Exa evidence includes endpoint family, SDK version, request ID, status, error tag, timing, result and status counts, cost, freshness mode, and retry history. Sensitive values and web content are unnecessary for most first-line diagnosis.

## Authentication

For normal REST work, inject `EXA_API_KEY` from an approved server-side secret manager and send it only as `Authorization: Bearer` to the configured first-party Exa API host. Team Management service keys, hosted MCP OAuth or enterprise managed authorization, and payment-protocol calls are separate trust models. Never print, commit, place in a URL, or expose a credential to an untrusted client.

## Instructions

1. Set the incident window, environment, data classification, and evidence owner.
2. Collect configuration names and hashes rather than secret values.
3. Record request IDs, statuses, tags, timing, counts, and retry decisions.
4. Replace queries, URLs, prompts, schemas, and content with approved fingerprints or categories.
5. Scan the candidate bundle for keys, bearer headers, presigned URLs, and customer text.
6. Encrypt, time-bound, and delete the bundle according to the incident policy.

## Tool Discipline

Use Read, Glob, and Grep to inspect repository code, configuration, fixtures, and evidence. Use Write and Edit only for approved implementation or documentation changes. Do not call Exa, run paid research, create or alter a Monitor, Webset, Agent run, Batch, team, member, API key, budget, webhook, or deployment merely because this skill was invoked.

## Approval Boundaries

Require an accountable owner before live queries involving sensitive intent, production credentials, spend or rate-limit changes, forced live crawling, generated summaries, external delivery, deployment, member or key changes, schedule creation, or destructive cancellation, stopping, deletion, or revocation. Read-only repository inspection and synthetic offline validation do not authorize live vendor actions.

## Failure Modes

- Environment dumps commonly expose EXA_API_KEY and unrelated secrets.
- Returned highlights, summaries, and Agent output may contain sensitive third-party text.
- A support bundle without request IDs or timestamps is difficult to correlate.

## Output

Return the operation scope, environment, team and product surface, authorization class, contract and policy decisions, deterministic validation results, content-free identifiers, status and cost counts, risks, cleanup or rollback state, and a concise pass or fail receipt. Exclude credentials, raw queries, prompts, presigned URLs, retrieved content, generated output, and customer-derived data unless separately approved.

## Example

- Share two request IDs, error tags, latency percentiles, SDK version, and a hashed config snapshot instead of raw payloads.
- Finish with request or resource IDs, assertion counts, cost and terminal state, rollback or deletion status, and the decision owner; never reproduce secrets or retrieved content.

## Validation

Rerun the smallest relevant deterministic test, compare actual behavior with the requested outcome and current first-party contract, verify sensitive fields are absent from evidence, and confirm deadlines, terminal state, downstream retention, and rollback before reporting success.

## References

Review the dated first-party evidence map before relying on any endpoint, parameter, search type, price, limit, beta, compliance, identity, retry, or lifecycle claim.

- [Current first-party evidence map](references/official-docs.md)
