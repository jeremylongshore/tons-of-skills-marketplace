---
name: exa-known-pitfalls
description: >-
  Audit an Exa integration for stale search types, unsafe secrets, ignored partial failures, unbounded content work, weak citations, and orphaned asynchronous resources. Use when operating or reviewing this Exa boundary. Trigger with "Exa known pitfalls", "review Exa known pitfalls", or "fix Exa known pitfalls".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<repository> <product-surface>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, exa]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Exa work requires network access"
---
# Exa Integration Pitfall Review

## Overview

Audit an Exa integration for stale search types, unsafe secrets, ignored partial failures, unbounded content work, weak citations, and orphaned asynchronous resources. Treat credentials, queries, retrieved content, generated output, spend, and destructive state as separately governed boundaries.

## Prerequisites

- The target repository, environment, Exa team, product surface, and accountable owner.
- The workload's data classification, latency and freshness promise, cost ceiling, and retention policy.
- Current first-party documentation plus credentials only for a narrowly approved live check.

## Current Contract

Common current hazards include legacy neural type usage, stale x-api-key examples instead of Bearer auth, unchecked Contents statuses, forced livecrawl everywhere, unbounded summaries or subpages, unsigned Monitor webhooks, and assumptions that code rollback cancels vendor-side work.

## Authentication

For normal REST work, inject `EXA_API_KEY` from an approved server-side secret manager and send it only as `Authorization: Bearer` to the configured first-party Exa API host. Team Management service keys, hosted MCP OAuth or enterprise managed authorization, and payment-protocol calls are separate trust models. Never print, commit, place in a URL, or expose a credential to an untrusted client.

## Instructions

1. Search code and configuration for every Exa endpoint, SDK call, header, and key.
2. Flag legacy types, stale auth, hidden defaults, beta features, and unbounded parameters.
3. Trace partial statuses, error tags, request IDs, citations, costs, and redaction.
4. Inventory Agent runs, Monitors, Websets, Batches, webhooks, and teardown ownership.
5. Prioritize findings by credential, data, cost, correctness, and availability impact.
6. Repair one bounded contract at a time and add a regression assertion.

## Tool Discipline

Use Read, Glob, and Grep to inspect repository code, configuration, fixtures, and evidence. Use Write and Edit only for approved implementation or documentation changes. Do not call Exa, run paid research, create or alter a Monitor, Webset, Agent run, Batch, team, member, API key, budget, webhook, or deployment merely because this skill was invoked.

## Approval Boundaries

Require an accountable owner before live queries involving sensitive intent, production credentials, spend or rate-limit changes, forced live crawling, generated summaries, external delivery, deployment, member or key changes, schedule creation, or destructive cancellation, stopping, deletion, or revocation. Read-only repository inspection and synthetic offline validation do not authorize live vendor actions.

## Failure Modes

- Do not replace a stale literal without validating surrounding behavior.
- Do not assume public-web content is safe to log or execute.
- Do not call a workflow reliable when it ignores resource state after timeout.

## Output

Return the operation scope, environment, team and product surface, authorization class, contract and policy decisions, deterministic validation results, content-free identifiers, status and cost counts, risks, cleanup or rollback state, and a concise pass or fail receipt. Exclude credentials, raw queries, prompts, presigned URLs, retrieved content, generated output, and customer-derived data unless separately approved.

## Example

- Replace legacy neural and x-api-key assumptions, add Contents status checks, and verify Monitor signatures with regression tests.
- Finish with request or resource IDs, assertion counts, cost and terminal state, rollback or deletion status, and the decision owner; never reproduce secrets or retrieved content.

## Validation

Rerun the smallest relevant deterministic test, compare actual behavior with the requested outcome and current first-party contract, verify sensitive fields are absent from evidence, and confirm deadlines, terminal state, downstream retention, and rollback before reporting success.

## References

Review the dated first-party evidence map before relying on any endpoint, parameter, search type, price, limit, beta, compliance, identity, retry, or lifecycle claim.

- [Current first-party evidence map](references/official-docs.md)
