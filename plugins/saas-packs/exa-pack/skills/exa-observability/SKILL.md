---
name: exa-observability
description: >-
  Instrument Exa calls with content-free metrics, traces, cost, and asynchronous lifecycle signals that support diagnosis without logging retrieved text. Use when operating or reviewing this Exa boundary. Trigger with "Exa observability", "review Exa observability", or "fix Exa observability".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<service> <slo> <dashboard>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, exa]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Exa work requires network access"
---
# Exa Operational Telemetry

## Overview

Instrument Exa calls with content-free metrics, traces, cost, and asynchronous lifecycle signals that support diagnosis without logging retrieved text. Treat credentials, queries, retrieved content, generated output, spend, and destructive state as separately governed boundaries.

## Prerequisites

- The target repository, environment, Exa team, product surface, and accountable owner.
- The workload's data classification, latency and freshness promise, cost ceiling, and retention policy.
- Current first-party documentation plus credentials only for a narrowly approved live check.

## Current Contract

Exa responses expose request IDs and often costDollars; errors expose status and tags; Contents exposes per-URL statuses. Agent, Monitor, Webset, and Batch operations add IDs, states, queues, events, and terminal outcomes that must be reconciled separately.

## Authentication

For normal REST work, inject `EXA_API_KEY` from an approved server-side secret manager and send it only as `Authorization: Bearer` to the configured first-party Exa API host. Team Management service keys, hosted MCP OAuth or enterprise managed authorization, and payment-protocol calls are separate trust models. Never print, commit, place in a URL, or expose a credential to an untrusted client.

## Instructions

1. Define service-level objectives for each endpoint and asynchronous product.
2. Emit endpoint, status, tag, latency, attempt, result count, and request ID safely.
3. Measure Contents status mix and freshness mode rather than logging page content.
4. Track run age, terminal state, webhook lag, queue depth, and reconciliation drift.
5. Attribute cost by environment, workload, key, product, and owner.
6. Alert on error-class shifts, stalled state, throttling, overload, credit risk, and missing events.

## Tool Discipline

Use Read, Glob, and Grep to inspect repository code, configuration, fixtures, and evidence. Use Write and Edit only for approved implementation or documentation changes. Do not call Exa, run paid research, create or alter a Monitor, Webset, Agent run, Batch, team, member, API key, budget, webhook, or deployment merely because this skill was invoked.

## Approval Boundaries

Require an accountable owner before live queries involving sensitive intent, production credentials, spend or rate-limit changes, forced live crawling, generated summaries, external delivery, deployment, member or key changes, schedule creation, or destructive cancellation, stopping, deletion, or revocation. Read-only repository inspection and synthetic offline validation do not authorize live vendor actions.

## Failure Modes

- Raw queries, URLs, highlights, summaries, and outputs are not safe default labels.
- HTTP success can hide partial Contents failures.
- Webhook delivery metrics without run reconciliation can report false completion.

## Output

Return the operation scope, environment, team and product surface, authorization class, contract and policy decisions, deterministic validation results, content-free identifiers, status and cost counts, risks, cleanup or rollback state, and a concise pass or fail receipt. Exclude credentials, raw queries, prompts, presigned URLs, retrieved content, generated output, and customer-derived data unless separately approved.

## Example

- A trace records request ID, Search type, content mode, result count, latency, cost, and redacted policy outcome, never the query or text.
- Finish with request or resource IDs, assertion counts, cost and terminal state, rollback or deletion status, and the decision owner; never reproduce secrets or retrieved content.

## Validation

Rerun the smallest relevant deterministic test, compare actual behavior with the requested outcome and current first-party contract, verify sensitive fields are absent from evidence, and confirm deadlines, terminal state, downstream retention, and rollback before reporting success.

## References

Review the dated first-party evidence map before relying on any endpoint, parameter, search type, price, limit, beta, compliance, identity, retry, or lifecycle claim.

- [Current first-party evidence map](references/official-docs.md)
