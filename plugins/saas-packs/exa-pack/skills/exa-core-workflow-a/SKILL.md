---
name: exa-core-workflow-a
description: >-
  Operate Search and Contents as an explicit two-stage retrieval workflow with bounded context, freshness, and cost. Use when operating or reviewing this Exa boundary. Trigger with "Exa core workflow a", "review Exa core workflow a", or "fix Exa core workflow a".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<query> <content-mode> <freshness-policy>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, exa]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Exa work requires network access"
---
# Exa Search and Contents Retrieval Workflow

## Overview

Operate Search and Contents as an explicit two-stage retrieval workflow with bounded context, freshness, and cost. Treat credentials, queries, retrieved content, generated output, spend, and destructive state as separately governed boundaries.

## Prerequisites

- The target repository, environment, Exa team, product surface, and accountable owner.
- The workload's data classification, latency and freshness promise, cost ceiling, and retention policy.
- Current first-party documentation plus credentials only for a narrowly approved live check.

## Current Contract

POST /search can return ranked results and nested contents. POST /contents retrieves known URLs or document IDs and always requires inspection of per-URL statuses. Highlights are token-efficient; text supports deeper analysis; summary is generated. Omitting maxAgeHours uses cache with livecrawl fallback, zero forces livecrawl, and minus one is cache-only.

## Authentication

For normal REST work, inject `EXA_API_KEY` from an approved server-side secret manager and send it only as `Authorization: Bearer` to the configured first-party Exa API host. Team Management service keys, hosted MCP OAuth or enterprise managed authorization, and payment-protocol calls are separate trust models. Never print, commit, place in a URL, or expose a credential to an untrusted client.

## Instructions

1. Classify the query, allowed domains, moderation need, and freshness requirement.
2. Choose type auto unless a measured latency or deep-synthesis need justifies another type.
3. Search with a bounded result count and minimal content mode.
4. Promote only approved URLs or IDs into a Contents request when more context is needed.
5. Inspect every Contents status and quarantine partial crawl failures.
6. Record request IDs, counts, freshness policy, and cost without copied content.

## Tool Discipline

Use Read, Glob, and Grep to inspect repository code, configuration, fixtures, and evidence. Use Write and Edit only for approved implementation or documentation changes. Do not call Exa, run paid research, create or alter a Monitor, Webset, Agent run, Batch, team, member, API key, budget, webhook, or deployment merely because this skill was invoked.

## Approval Boundaries

Require an accountable owner before live queries involving sensitive intent, production credentials, spend or rate-limit changes, forced live crawling, generated summaries, external delivery, deployment, member or key changes, schedule creation, or destructive cancellation, stopping, deletion, or revocation. Read-only repository inspection and synthetic offline validation do not authorize live vendor actions.

## Failure Modes

- Legacy neural is not the recommended type for new code.
- Forcing livecrawl increases latency and can still fail per URL.
- A successful batch-level Contents response can contain failed URL statuses.

## Output

Return the operation scope, environment, team and product surface, authorization class, contract and policy decisions, deterministic validation results, content-free identifiers, status and cost counts, risks, cleanup or rollback state, and a concise pass or fail receipt. Exclude credentials, raw queries, prompts, presigned URLs, retrieved content, generated output, and customer-derived data unless separately approved.

## Example

- Use auto Search with highlights for five results, then request capped text only for the two approved source URLs.
- Finish with request or resource IDs, assertion counts, cost and terminal state, rollback or deletion status, and the decision owner; never reproduce secrets or retrieved content.

## Validation

Rerun the smallest relevant deterministic test, compare actual behavior with the requested outcome and current first-party contract, verify sensitive fields are absent from evidence, and confirm deadlines, terminal state, downstream retention, and rollback before reporting success.

## References

Review the dated first-party evidence map before relying on any endpoint, parameter, search type, price, limit, beta, compliance, identity, retry, or lifecycle claim.

- [Current first-party evidence map](references/official-docs.md)
