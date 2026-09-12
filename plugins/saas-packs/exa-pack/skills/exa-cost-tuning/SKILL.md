---
name: exa-cost-tuning
description: >-
  Control Exa spend through endpoint selection, bounded result and content work, per-key budgets, and response-derived cost evidence. Use when operating or reviewing this Exa boundary. Trigger with "Exa cost tuning", "review Exa cost tuning", or "fix Exa cost tuning".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<workload> <monthly-budget> <owner>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, exa]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Exa work requires network access"
---
# Exa Cost and Credit Control

## Overview

Control Exa spend through endpoint selection, bounded result and content work, per-key budgets, and response-derived cost evidence. Treat credentials, queries, retrieved content, generated output, spend, and destructive state as separately governed boundaries.

## Prerequisites

- The target repository, environment, Exa team, product surface, and accountable owner.
- The workload's data classification, latency and freshness promise, cost ceiling, and retention policy.
- Current first-party documentation plus credentials only for a narrowly approved live check.

## Current Contract

Exa uses prepaid pay-as-you-go credits unless an enterprise contract says otherwise. Search, Contents, Answer, Monitors, and Agent have different pricing; additional results, summaries, deep types, provider calls, and metered Agent effort can add cost. Higher credit balance does not raise rate limits.

## Authentication

For normal REST work, inject `EXA_API_KEY` from an approved server-side secret manager and send it only as `Authorization: Bearer` to the configured first-party Exa API host. Team Management service keys, hosted MCP OAuth or enterprise managed authorization, and payment-protocol calls are separate trust models. Never print, commit, place in a URL, or expose a credential to an untrusted client.

## Instructions

1. Name the budget owner, team, workload, endpoint mix, and forecast horizon.
2. Verify current first-party pricing or the signed enterprise schedule.
3. Cap results, content types, subpages, freshness, Agent effort, and retry attempts.
4. Use key-level budgets where enabled and independent application-side circuit breakers.
5. Reconcile response costDollars and dashboard billing against workload identifiers.
6. Alert before credit exhaustion and review auto-recharge with its monthly maximum.

## Tool Discipline

Use Read, Glob, and Grep to inspect repository code, configuration, fixtures, and evidence. Use Write and Edit only for approved implementation or documentation changes. Do not call Exa, run paid research, create or alter a Monitor, Webset, Agent run, Batch, team, member, API key, budget, webhook, or deployment merely because this skill was invoked.

## Approval Boundaries

Require an accountable owner before live queries involving sensitive intent, production credentials, spend or rate-limit changes, forced live crawling, generated summaries, external delivery, deployment, member or key changes, schedule creation, or destructive cancellation, stopping, deletion, or revocation. Read-only repository inspection and synthetic offline validation do not authorize live vendor actions.

## Failure Modes

- Do not hard-code current public prices as permanent business logic.
- A 402 may mean account credits, key budget, or team budget is exhausted.
- Auto-recharge without a monthly maximum can defeat an application budget.

## Output

Return the operation scope, environment, team and product surface, authorization class, contract and policy decisions, deterministic validation results, content-free identifiers, status and cost counts, risks, cleanup or rollback state, and a concise pass or fail receipt. Exclude credentials, raw queries, prompts, presigned URLs, retrieved content, generated output, and customer-derived data unless separately approved.

## Example

- Budget interactive Search separately from Agent research, cap Agent effort, and alert on both response cost and remaining credits.
- Finish with request or resource IDs, assertion counts, cost and terminal state, rollback or deletion status, and the decision owner; never reproduce secrets or retrieved content.

## Validation

Rerun the smallest relevant deterministic test, compare actual behavior with the requested outcome and current first-party contract, verify sensitive fields are absent from evidence, and confirm deadlines, terminal state, downstream retention, and rollback before reporting success.

## References

Review the dated first-party evidence map before relying on any endpoint, parameter, search type, price, limit, beta, compliance, identity, retry, or lifecycle claim.

- [Current first-party evidence map](references/official-docs.md)
