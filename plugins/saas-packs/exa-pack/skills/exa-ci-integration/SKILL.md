---
name: exa-ci-integration
description: >-
  Add deterministic Exa contract checks to CI while keeping live credentials, spend, and volatile web results out of ordinary pull requests. Use when operating or reviewing this Exa boundary. Trigger with "Exa ci integration", "review Exa ci integration", or "fix Exa ci integration".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<repository> <protected-live-lane>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, exa]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Exa work requires network access"
---
# Exa CI Contract Verification

## Overview

Add deterministic Exa contract checks to CI while keeping live credentials, spend, and volatile web results out of ordinary pull requests. Treat credentials, queries, retrieved content, generated output, spend, and destructive state as separately governed boundaries.

## Prerequisites

- The target repository, environment, Exa team, product surface, and accountable owner.
- The workload's data classification, latency and freshness promise, cost ceiling, and retention policy.
- Current first-party documentation plus credentials only for a narrowly approved live check.

## Current Contract

Offline CI can verify owned request and response schemas, error tags, webhook signatures, and redaction. A live lane should be protected, synthetic, manually or schedule authorized, tightly budgeted, and non-blocking until its reliability is understood.

## Authentication

For normal REST work, inject `EXA_API_KEY` from an approved server-side secret manager and send it only as `Authorization: Bearer` to the configured first-party Exa API host. Team Management service keys, hosted MCP OAuth or enterprise managed authorization, and payment-protocol calls are separate trust models. Never print, commit, place in a URL, or expose a credential to an untrusted client.

## Instructions

1. Map the Exa adapter and enumerate contracts changed by the pull request.
2. Add sanitized fixtures for success, partial Contents status, 429, 402, and 503.
3. Verify no load-time shell commands or secret-dependent preprocessing occurs.
4. Test webhook signature verification with fixed local payloads and clocks.
5. Place a one-request live smoke lane behind protected credentials and concurrency.
6. Publish content-free gate evidence and distinguish skipped from passed live checks.

## Tool Discipline

Use Read, Glob, and Grep to inspect repository code, configuration, fixtures, and evidence. Use Write and Edit only for approved implementation or documentation changes. Do not call Exa, run paid research, create or alter a Monitor, Webset, Agent run, Batch, team, member, API key, budget, webhook, or deployment merely because this skill was invoked.

## Approval Boundaries

Require an accountable owner before live queries involving sensitive intent, production credentials, spend or rate-limit changes, forced live crawling, generated summaries, external delivery, deployment, member or key changes, schedule creation, or destructive cancellation, stopping, deletion, or revocation. Read-only repository inspection and synthetic offline validation do not authorize live vendor actions.

## Failure Modes

- A skipped live job must not be reported as vendor validation.
- Snapshotting web ranks or text makes pull requests nondeterministic.
- Fork pull requests must never receive production Exa secrets.

## Output

Return the operation scope, environment, team and product surface, authorization class, contract and policy decisions, deterministic validation results, content-free identifiers, status and cost counts, risks, cleanup or rollback state, and a concise pass or fail receipt. Exclude credentials, raw queries, prompts, presigned URLs, retrieved content, generated output, and customer-derived data unless separately approved.

## Example

- Every PR runs fixture contracts; a protected nightly job performs one URL-only Search and retains request ID, shape, latency, and cost.
- Finish with request or resource IDs, assertion counts, cost and terminal state, rollback or deletion status, and the decision owner; never reproduce secrets or retrieved content.

## Validation

Rerun the smallest relevant deterministic test, compare actual behavior with the requested outcome and current first-party contract, verify sensitive fields are absent from evidence, and confirm deadlines, terminal state, downstream retention, and rollback before reporting success.

## References

Review the dated first-party evidence map before relying on any endpoint, parameter, search type, price, limit, beta, compliance, identity, retry, or lifecycle claim.

- [Current first-party evidence map](references/official-docs.md)
