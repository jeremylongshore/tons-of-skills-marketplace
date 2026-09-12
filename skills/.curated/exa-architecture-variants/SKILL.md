---
name: exa-architecture-variants
description: >-
  Choose among direct Search, staged Contents, Answer, Agent, Monitors, Websets, and Batch using explicit latency, verification, volume, and lifecycle criteria. Use when operating or reviewing this Exa boundary. Trigger with "Exa architecture variants", "review Exa architecture variants", or "fix Exa architecture variants".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<use-case> <volume> <latency-class>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, exa]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Exa work requires network access"
---
# Exa Product Architecture Selection

## Overview

Choose among direct Search, staged Contents, Answer, Agent, Monitors, Websets, and Batch using explicit latency, verification, volume, and lifecycle criteria. Treat credentials, queries, retrieved content, generated output, spend, and destructive state as separately governed boundaries.

## Prerequisites

- The target repository, environment, Exa team, product surface, and accountable owner.
- The workload's data classification, latency and freshness promise, cost ceiling, and retention policy.
- Current first-party documentation plus credentials only for a narrowly approved live check.

## Current Contract

The Exa products are complementary rather than drop-in tiers. Search and Contents suit bounded synchronous retrieval; Answer synthesizes a cited response; Agent performs asynchronous multi-step research; Monitors recur and notify; Websets verify and enrich sets; enabled Batch handles offline Search or Agent volume.

## Authentication

For normal REST work, inject `EXA_API_KEY` from an approved server-side secret manager and send it only as `Authorization: Bearer` to the configured first-party Exa API host. Team Management service keys, hosted MCP OAuth or enterprise managed authorization, and payment-protocol calls are separate trust models. Never print, commit, place in a URL, or expose a credential to an untrusted client.

## Instructions

1. State the output, verification need, cadence, latency, volume, and cost ceiling.
2. Select the narrowest product and document why simpler options fail.
3. Model synchronous and asynchronous state, callbacks, polling, and terminal outcomes.
4. Place credentials, policy, content inspection, and citations at explicit boundaries.
5. Prototype with synthetic inputs and measure quality, latency, and cost.
6. Record the chosen variant, rejected alternatives, migration triggers, and rollback.

## Tool Discipline

Use Read, Glob, and Grep to inspect repository code, configuration, fixtures, and evidence. Use Write and Edit only for approved implementation or documentation changes. Do not call Exa, run paid research, create or alter a Monitor, Webset, Agent run, Batch, team, member, API key, budget, webhook, or deployment merely because this skill was invoked.

## Approval Boundaries

Require an accountable owner before live queries involving sensitive intent, production credentials, spend or rate-limit changes, forced live crawling, generated summaries, external delivery, deployment, member or key changes, schedule creation, or destructive cancellation, stopping, deletion, or revocation. Read-only repository inspection and synthetic offline validation do not authorize live vendor actions.

## Failure Modes

- A more autonomous product is not automatically a better retrieval architecture.
- Batch availability and beta headers require enterprise enablement.
- Recurring Monitors create durable vendor-side state that needs lifecycle ownership.

## Output

Return the operation scope, environment, team and product surface, authorization class, contract and policy decisions, deterministic validation results, content-free identifiers, status and cost counts, risks, cleanup or rollback state, and a concise pass or fail receipt. Exclude credentials, raw queries, prompts, presigned URLs, retrieved content, generated output, and customer-derived data unless separately approved.

## Example

- Use direct Search for interactive lookup, Agent for bounded deep research, and Monitors only when recurring deduplicated discovery is required.
- Finish with request or resource IDs, assertion counts, cost and terminal state, rollback or deletion status, and the decision owner; never reproduce secrets or retrieved content.

## Validation

Rerun the smallest relevant deterministic test, compare actual behavior with the requested outcome and current first-party contract, verify sensitive fields are absent from evidence, and confirm deadlines, terminal state, downstream retention, and rollback before reporting success.

## References

Review the dated first-party evidence map before relying on any endpoint, parameter, search type, price, limit, beta, compliance, identity, retry, or lifecycle claim.

- [Current first-party evidence map](references/official-docs.md)
