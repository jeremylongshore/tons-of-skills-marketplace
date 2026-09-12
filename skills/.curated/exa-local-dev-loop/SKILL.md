---
name: exa-local-dev-loop
description: >-
  Build and test an Exa adapter locally using schema fixtures, recorded content-free envelopes, and an explicit opt-in live lane. Use when operating or reviewing this Exa boundary. Trigger with "Exa local dev loop", "review Exa local dev loop", or "fix Exa local dev loop".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<fixture-set> <adapter-path>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, exa]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Exa work requires network access"
---
# Exa Deterministic Local Development Loop

## Overview

Build and test an Exa adapter locally using schema fixtures, recorded content-free envelopes, and an explicit opt-in live lane. Treat credentials, queries, retrieved content, generated output, spend, and destructive state as separately governed boundaries.

## Prerequisites

- The target repository, environment, Exa team, product surface, and accountable owner.
- The workload's data classification, latency and freshness promise, cost ceiling, and retention policy.
- Current first-party documentation plus credentials only for a narrowly approved live check.

## Current Contract

Search results, crawl output, and rankings are time-varying. Local tests should own sanitized response fixtures for request and failure shapes, while live calls remain a separately authorized integration lane with a small budget.

## Authentication

For normal REST work, inject `EXA_API_KEY` from an approved server-side secret manager and send it only as `Authorization: Bearer` to the configured first-party Exa API host. Team Management service keys, hosted MCP OAuth or enterprise managed authorization, and payment-protocol calls are separate trust models. Never print, commit, place in a URL, or expose a credential to an untrusted client.

## Instructions

1. Locate the application-owned Exa boundary and its existing tests.
2. Define typed request, response, status, and error-tag fixtures.
3. Cover Search, Contents per-URL statuses, and one retryable failure offline.
4. Inject a fake clock and deterministic retry schedule.
5. Gate any live probe behind explicit credentials and an opt-in flag.
6. Report fixture provenance, assertions, and whether a live call occurred.

## Tool Discipline

Use Read, Glob, and Grep to inspect repository code, configuration, fixtures, and evidence. Use Write and Edit only for approved implementation or documentation changes. Do not call Exa, run paid research, create or alter a Monitor, Webset, Agent run, Batch, team, member, API key, budget, webhook, or deployment merely because this skill was invoked.

## Approval Boundaries

Require an accountable owner before live queries involving sensitive intent, production credentials, spend or rate-limit changes, forced live crawling, generated summaries, external delivery, deployment, member or key changes, schedule creation, or destructive cancellation, stopping, deletion, or revocation. Read-only repository inspection and synthetic offline validation do not authorize live vendor actions.

## Failure Modes

- Do not commit real page contents, queries, API keys, or presigned URLs.
- Do not make network access a unit-test prerequisite.
- Do not treat a sanitized fixture as proof that the current vendor contract is unchanged.

## Output

Return the operation scope, environment, team and product surface, authorization class, contract and policy decisions, deterministic validation results, content-free identifiers, status and cost counts, risks, cleanup or rollback state, and a concise pass or fail receipt. Exclude credentials, raw queries, prompts, presigned URLs, retrieved content, generated output, and customer-derived data unless separately approved.

## Example

- An offline test returns a requestId, two URL-only results, costDollars, and a 429 Retry-After case through a fake transport.
- Finish with request or resource IDs, assertion counts, cost and terminal state, rollback or deletion status, and the decision owner; never reproduce secrets or retrieved content.

## Validation

Rerun the smallest relevant deterministic test, compare actual behavior with the requested outcome and current first-party contract, verify sensitive fields are absent from evidence, and confirm deadlines, terminal state, downstream retention, and rollback before reporting success.

## References

Review the dated first-party evidence map before relying on any endpoint, parameter, search type, price, limit, beta, compliance, identity, retry, or lifecycle claim.

- [Current first-party evidence map](references/official-docs.md)
