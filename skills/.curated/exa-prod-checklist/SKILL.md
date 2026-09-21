---
name: exa-prod-checklist
description: >-
  Gate an Exa-backed service on contract, security, cost, reliability, observability, and rollback evidence. Use when operating or reviewing this Exa boundary. Trigger with "Exa prod checklist", "review Exa prod checklist", or "fix Exa prod checklist".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<service> <environment> <release-sha>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, exa]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Exa work requires network access"
---
# Exa Production Readiness Gate

## Overview

Gate an Exa-backed service on contract, security, cost, reliability, observability, and rollback evidence. Treat credentials, queries, retrieved content, generated output, spend, and destructive state as separately governed boundaries.

## Prerequisites

- The target repository, environment, Exa team, product surface, and accountable owner.
- The workload's data classification, latency and freshness promise, cost ceiling, and retention policy.
- Current first-party documentation plus credentials only for a narrowly approved live check.

## Current Contract

Production readiness spans the chosen Exa product, not just connectivity. Search and Contents require content and freshness controls; Agent, Monitors, Websets, and Batch add asynchronous state; webhooks add signature and replay handling; every paid surface needs a budget owner.

## Authentication

For normal REST work, inject `EXA_API_KEY` from an approved server-side secret manager and send it only as `Authorization: Bearer` to the configured first-party Exa API host. Team Management service keys, hosted MCP OAuth or enterprise managed authorization, and payment-protocol calls are separate trust models. Never print, commit, place in a URL, or expose a credential to an untrusted client.

## Instructions

1. Freeze the release SHA, adapter version, endpoint inventory, and rollback owner.
2. Verify auth, secret rotation, data classification, domain policy, and moderation.
3. Exercise documented success, partial, throttle, billing, policy, and overload paths.
4. Confirm endpoint budgets, cost alerts, queue bounds, timeouts, and retry ceilings.
5. Verify request IDs, safe metrics, signed-webhook evidence, and deletion procedures.
6. Canary under explicit limits and promote only after the rollback window passes.

## Tool Discipline

Use Read, Glob, and Grep to inspect repository code, configuration, fixtures, and evidence. Use Write and Edit only for approved implementation or documentation changes. Do not call Exa, run paid research, create or alter a Monitor, Webset, Agent run, Batch, team, member, API key, budget, webhook, or deployment merely because this skill was invoked.

## Approval Boundaries

Require an accountable owner before live queries involving sensitive intent, production credentials, spend or rate-limit changes, forced live crawling, generated summaries, external delivery, deployment, member or key changes, schedule creation, or destructive cancellation, stopping, deletion, or revocation. Read-only repository inspection and synthetic offline validation do not authorize live vendor actions.

## Failure Modes

- A green Search smoke test does not validate asynchronous or webhook paths.
- Unbounded livecrawl, subpages, summaries, or Agent effort can change latency and cost.
- Rollback is incomplete if scheduled Monitors or in-flight runs continue producing output.

## Output

Return the operation scope, environment, team and product surface, authorization class, contract and policy decisions, deterministic validation results, content-free identifiers, status and cost counts, risks, cleanup or rollback state, and a concise pass or fail receipt. Exclude credentials, raw queries, prompts, presigned URLs, retrieved content, generated output, and customer-derived data unless separately approved.

## Example

- Release a five-percent canary with fixed Search limits, signed Monitor delivery, cost alarms, and a tested disable switch.
- Finish with request or resource IDs, assertion counts, cost and terminal state, rollback or deletion status, and the decision owner; never reproduce secrets or retrieved content.

## Validation

Rerun the smallest relevant deterministic test, compare actual behavior with the requested outcome and current first-party contract, verify sensitive fields are absent from evidence, and confirm deadlines, terminal state, downstream retention, and rollback before reporting success.

## References

Review the dated first-party evidence map before relying on any endpoint, parameter, search type, price, limit, beta, compliance, identity, retry, or lifecycle claim.

- [Current first-party evidence map](references/official-docs.md)
