---
name: exa-migration-deep-dive
description: >-
  Migrate a legacy web-search integration to Exa through semantic, filter, freshness, relevance, cost, and rollback comparisons. Use when operating or reviewing this Exa boundary. Trigger with "Exa migration deep dive", "review Exa migration deep dive", or "fix Exa migration deep dive".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<source-provider> <query-corpus> <cutover-window>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, exa]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Exa work requires network access"
---
# Legacy Search to Exa Migration

## Overview

Migrate a legacy web-search integration to Exa through semantic, filter, freshness, relevance, cost, and rollback comparisons. Treat credentials, queries, retrieved content, generated output, spend, and destructive state as separately governed boundaries.

## Prerequisites

- The target repository, environment, Exa team, product surface, and accountable owner.
- The workload's data classification, latency and freshness promise, cost ceiling, and retention policy.
- Current first-party documentation plus credentials only for a narrowly approved live check.

## Current Contract

Exa publishes a Bing migration guide, but provider fields and ranking semantics are not one-to-one. Exa Search supports domain, date, category, location, moderation, content, and deep-synthesis controls. Migration acceptance must evaluate the application outcome rather than translate parameters mechanically.

## Authentication

For normal REST work, inject `EXA_API_KEY` from an approved server-side secret manager and send it only as `Authorization: Bearer` to the configured first-party Exa API host. Team Management service keys, hosted MCP OAuth or enterprise managed authorization, and payment-protocol calls are separate trust models. Never print, commit, place in a URL, or expose a credential to an untrusted client.

## Instructions

1. Inventory legacy queries, filters, result fields, freshness, quotas, and downstream assumptions.
2. Build a consented evaluation corpus with relevance and safety judgments.
3. Map each requirement to Exa Search or a separate Contents stage.
4. Run shadow comparisons under matched result, freshness, and cost budgets.
5. Canary traffic with output-shape compatibility and a provider rollback switch.
6. Remove legacy credentials only after parity, observation, and stakeholder acceptance.

## Tool Discipline

Use Read, Glob, and Grep to inspect repository code, configuration, fixtures, and evidence. Use Write and Edit only for approved implementation or documentation changes. Do not call Exa, run paid research, create or alter a Monitor, Webset, Agent run, Batch, team, member, API key, budget, webhook, or deployment merely because this skill was invoked.

## Approval Boundaries

Require an accountable owner before live queries involving sensitive intent, production credentials, spend or rate-limit changes, forced live crawling, generated summaries, external delivery, deployment, member or key changes, schedule creation, or destructive cancellation, stopping, deletion, or revocation. Read-only repository inspection and synthetic offline validation do not authorize live vendor actions.

## Failure Modes

- Do not equate rank positions across providers.
- A field-name translation can hide different freshness or content semantics.
- Dual-running providers doubles data-handling and cost scope during migration.

## Output

Return the operation scope, environment, team and product surface, authorization class, contract and policy decisions, deterministic validation results, content-free identifiers, status and cost counts, risks, cleanup or rollback state, and a concise pass or fail receipt. Exclude credentials, raw queries, prompts, presigned URLs, retrieved content, generated output, and customer-derived data unless separately approved.

## Example

- Shadow ten percent of approved queries, compare relevance at five plus latency and cost, and cut over only after the safety floor holds.
- Finish with request or resource IDs, assertion counts, cost and terminal state, rollback or deletion status, and the decision owner; never reproduce secrets or retrieved content.

## Validation

Rerun the smallest relevant deterministic test, compare actual behavior with the requested outcome and current first-party contract, verify sensitive fields are absent from evidence, and confirm deadlines, terminal state, downstream retention, and rollback before reporting success.

## References

Review the dated first-party evidence map before relying on any endpoint, parameter, search type, price, limit, beta, compliance, identity, retry, or lifecycle claim.

- [Current first-party evidence map](references/official-docs.md)
