---
name: exa-incident-runbook
description: >-
  Contain Exa credential, data, cost, capacity, or correctness incidents while preserving safe evidence and vendor request IDs. Use when operating or reviewing this Exa boundary. Trigger with "Exa incident runbook", "review Exa incident runbook", or "fix Exa incident runbook".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<severity> <environment> <incident-window>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, exa]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Exa work requires network access"
---
# Exa Incident Containment Runbook

## Overview

Contain Exa credential, data, cost, capacity, or correctness incidents while preserving safe evidence and vendor request IDs. Treat credentials, queries, retrieved content, generated output, spend, and destructive state as separately governed boundaries.

## Prerequisites

- The target repository, environment, Exa team, product surface, and accountable owner.
- The workload's data classification, latency and freshness promise, cost ceiling, and retention policy.
- Current first-party documentation plus credentials only for a narrowly approved live check.

## Current Contract

Containment choices differ by incident: revoke or rotate a key, disable a caller, pause or delete Monitors, stop or cancel Agent runs, cancel Batches, quarantine webhook processing, or switch to a tested fallback. Deletion and cancellation are destructive and require exact targets.

## Authentication

For normal REST work, inject `EXA_API_KEY` from an approved server-side secret manager and send it only as `Authorization: Bearer` to the configured first-party Exa API host. Team Management service keys, hosted MCP OAuth or enterprise managed authorization, and payment-protocol calls are separate trust models. Never print, commit, place in a URL, or expose a credential to an untrusted client.

## Instructions

1. Declare severity, affected product, environment, owner, and evidence boundary.
2. Stop new work at the narrowest reversible application or queue control.
3. Snapshot content-free IDs, states, costs, error tags, timestamps, and request IDs.
4. Rotate credentials or pause vendor resources only with exact authorization.
5. Reconcile in-flight runs, batches, monitors, webhooks, and downstream outputs.
6. Verify recovery, document residual risk, and time-bound evidence retention.

## Tool Discipline

Use Read, Glob, and Grep to inspect repository code, configuration, fixtures, and evidence. Use Write and Edit only for approved implementation or documentation changes. Do not call Exa, run paid research, create or alter a Monitor, Webset, Agent run, Batch, team, member, API key, budget, webhook, or deployment merely because this skill was invoked.

## Approval Boundaries

Require an accountable owner before live queries involving sensitive intent, production credentials, spend or rate-limit changes, forced live crawling, generated summaries, external delivery, deployment, member or key changes, schedule creation, or destructive cancellation, stopping, deletion, or revocation. Read-only repository inspection and synthetic offline validation do not authorize live vendor actions.

## Failure Modes

- Blind retries can amplify cost, rate limits, or incorrect output.
- Deleting resources before capturing IDs can destroy the recovery trail.
- Rotating an API key does not automatically invalidate unrelated OAuth or service-key sessions.

## Output

Return the operation scope, environment, team and product surface, authorization class, contract and policy decisions, deterministic validation results, content-free identifiers, status and cost counts, risks, cleanup or rollback state, and a concise pass or fail receipt. Exclude credentials, raw queries, prompts, presigned URLs, retrieved content, generated output, and customer-derived data unless separately approved.

## Example

- Disable new Agent submissions, stop exact run IDs, preserve request IDs and cost totals, then restore through a one-run canary.
- Finish with request or resource IDs, assertion counts, cost and terminal state, rollback or deletion status, and the decision owner; never reproduce secrets or retrieved content.

## Validation

Rerun the smallest relevant deterministic test, compare actual behavior with the requested outcome and current first-party contract, verify sensitive fields are absent from evidence, and confirm deadlines, terminal state, downstream retention, and rollback before reporting success.

## References

Review the dated first-party evidence map before relying on any endpoint, parameter, search type, price, limit, beta, compliance, identity, retry, or lifecycle claim.

- [Current first-party evidence map](references/official-docs.md)
