---
name: exa-load-scale
description: >-
  Validate Exa capacity with synthetic workload models, endpoint-specific budgets, bounded queues, and stop conditions. Use when operating or reviewing this Exa boundary. Trigger with "Exa load scale", "review Exa load scale", or "fix Exa load scale".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<workload-model> <max-qps> <duration>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, exa]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Exa work requires network access"
---
# Exa Load and Capacity Verification

## Overview

Validate Exa capacity with synthetic workload models, endpoint-specific budgets, bounded queues, and stop conditions. Treat credentials, queries, retrieved content, generated output, spend, and destructive state as separately governed boundaries.

## Prerequisites

- The target repository, environment, Exa team, product surface, and accountable owner.
- The workload's data classification, latency and freshness promise, cost ceiling, and retention policy.
- Current first-party documentation plus credentials only for a narrowly approved live check.

## Current Contract

Published QPS differs by endpoint and enterprise limits can differ by team. Search, Contents, and Answer have distinct ceilings; asynchronous Agent or Batch is not equivalent to synchronous load. Enterprise Batch is beta, must be enabled, and requires the current first-party `Exa-Beta` header documented for that feature.

## Authentication

For normal REST work, inject `EXA_API_KEY` from an approved server-side secret manager and send it only as `Authorization: Bearer` to the configured first-party Exa API host. Team Management service keys, hosted MCP OAuth or enterprise managed authorization, and payment-protocol calls are separate trust models. Never print, commit, place in a URL, or expose a credential to an untrusted client.

## Instructions

1. Obtain vendor and service-owner approval for the environment, volume, duration, and spend.
2. Model endpoint mix, result sizes, content modes, freshness, and asynchronous work.
3. Use synthetic non-sensitive inputs and shared limiters across workers.
4. Ramp gradually with hard stop conditions for errors, latency, cost, and backlog.
5. Measure 429 separately from 503, partial crawl status, and downstream saturation.
6. Drain queues, reconcile runs or batches, and delete test artifacts after the evidence window.

## Tool Discipline

Use Read, Glob, and Grep to inspect repository code, configuration, fixtures, and evidence. Use Write and Edit only for approved implementation or documentation changes. Do not call Exa, run paid research, create or alter a Monitor, Webset, Agent run, Batch, team, member, API key, budget, webhook, or deployment merely because this skill was invoked.

## Approval Boundaries

Require an accountable owner before live queries involving sensitive intent, production credentials, spend or rate-limit changes, forced live crawling, generated summaries, external delivery, deployment, member or key changes, schedule creation, or destructive cancellation, stopping, deletion, or revocation. Read-only repository inspection and synthetic offline validation do not authorize live vendor actions.

## Failure Modes

- Do not load-test production or third-party target sites without authorization.
- More workers can violate a shared team or network limit.
- A completed Batch can contain failed item rows that need separate accounting.

## Output

Return the operation scope, environment, team and product surface, authorization class, contract and policy decisions, deterministic validation results, content-free identifiers, status and cost counts, risks, cleanup or rollback state, and a concise pass or fail receipt. Exclude credentials, raw queries, prompts, presigned URLs, retrieved content, generated output, and customer-derived data unless separately approved.

## Example

- Ramp synthetic Search to the approved ceiling while Contents runs in its own pool, then stop on throttle or cost thresholds.
- Finish with request or resource IDs, assertion counts, cost and terminal state, rollback or deletion status, and the decision owner; never reproduce secrets or retrieved content.

## Validation

Rerun the smallest relevant deterministic test, compare actual behavior with the requested outcome and current first-party contract, verify sensitive fields are absent from evidence, and confirm deadlines, terminal state, downstream retention, and rollback before reporting success.

## References

Review the dated first-party evidence map before relying on any endpoint, parameter, search type, price, limit, beta, compliance, identity, retry, or lifecycle claim.

- [Current first-party evidence map](references/official-docs.md)
