---
name: exa-advanced-troubleshooting
description: >-
  Localize complex Exa failures across query planning, retrieval, crawling, synthesis, SDK mapping, queues, and downstream consumption. Use when operating or reviewing this Exa boundary. Trigger with "Exa advanced troubleshooting", "review Exa advanced troubleshooting", or "fix Exa advanced troubleshooting".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<symptom> <request-ids> <time-window>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, exa]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Exa work requires network access"
---
# Exa Cross-layer Troubleshooting

## Overview

Localize complex Exa failures across query planning, retrieval, crawling, synthesis, SDK mapping, queues, and downstream consumption. Treat credentials, queries, retrieved content, generated output, spend, and destructive state as separately governed boundaries.

## Prerequisites

- The target repository, environment, Exa team, product surface, and accountable owner.
- The workload's data classification, latency and freshness promise, cost ceiling, and retention policy.
- Current first-party documentation plus credentials only for a narrowly approved live check.

## Current Contract

Search relevance, Contents crawl status, deep output grounding, Agent terminal state, webhook delivery, and application rendering are independent layers. A single request can succeed at one layer and fail at another, so evidence must preserve layer-specific IDs and decisions.

## Authentication

For normal REST work, inject `EXA_API_KEY` from an approved server-side secret manager and send it only as `Authorization: Bearer` to the configured first-party Exa API host. Team Management service keys, hosted MCP OAuth or enterprise managed authorization, and payment-protocol calls are separate trust models. Never print, commit, place in a URL, or expose a credential to an untrusted client.

## Instructions

1. Reproduce with a sanitized input and freeze endpoint, SDK, flags, and time window.
2. Trace the application request through adapter, Exa request ID, results, statuses, and downstream IDs.
3. Separate relevance, freshness, crawl, synthesis, schema, queue, and rendering symptoms.
4. Compare one controlled parameter at a time against a known-good fixture or request.
5. Escalate vendor defects with request IDs, tags, timestamps, and redacted shape evidence.
6. Verify the fix at the failed layer and then end to end before closing.

## Tool Discipline

Use Read, Glob, and Grep to inspect repository code, configuration, fixtures, and evidence. Use Write and Edit only for approved implementation or documentation changes. Do not call Exa, run paid research, create or alter a Monitor, Webset, Agent run, Batch, team, member, API key, budget, webhook, or deployment merely because this skill was invoked.

## Approval Boundaries

Require an accountable owner before live queries involving sensitive intent, production credentials, spend or rate-limit changes, forced live crawling, generated summaries, external delivery, deployment, member or key changes, schedule creation, or destructive cancellation, stopping, deletion, or revocation. Read-only repository inspection and synthetic offline validation do not authorize live vendor actions.

## Failure Modes

- Changing query, search type, freshness, and content mode together destroys causal evidence.
- Missing Contents statuses can make crawl failure look like a model failure.
- A repaired vendor response can still be mishandled by the local adapter or downstream schema.

## Output

Return the operation scope, environment, team and product surface, authorization class, contract and policy decisions, deterministic validation results, content-free identifiers, status and cost counts, risks, cleanup or rollback state, and a concise pass or fail receipt. Exclude credentials, raw queries, prompts, presigned URLs, retrieved content, generated output, and customer-derived data unless separately approved.

## Example

- Trace an empty RAG answer to successful Search, failed per-URL Contents statuses, and an adapter that discarded those statuses.
- Finish with request or resource IDs, assertion counts, cost and terminal state, rollback or deletion status, and the decision owner; never reproduce secrets or retrieved content.

## Validation

Rerun the smallest relevant deterministic test, compare actual behavior with the requested outcome and current first-party contract, verify sensitive fields are absent from evidence, and confirm deadlines, terminal state, downstream retention, and rollback before reporting success.

## References

Review the dated first-party evidence map before relying on any endpoint, parameter, search type, price, limit, beta, compliance, identity, retry, or lifecycle claim.

- [Current first-party evidence map](references/official-docs.md)
