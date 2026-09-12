---
name: exa-install-auth
description: >-
  Configure an Exa client without leaking credentials or mixing API-key, MCP OAuth, enterprise managed authorization, and payment-protocol trust models. Use when operating or reviewing this Exa boundary. Trigger with "Exa install auth", "review Exa install auth", or "fix Exa install auth".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<runtime> <team> <environment>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, exa]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Exa work requires network access"
---
# Exa Authentication and Installation Boundary

## Overview

Configure an Exa client without leaking credentials or mixing API-key, MCP OAuth, enterprise managed authorization, and payment-protocol trust models. Treat credentials, queries, retrieved content, generated output, spend, and destructive state as separately governed boundaries.

## Prerequisites

- The target repository, environment, Exa team, product surface, and accountable owner.
- The workload's data classification, latency and freshness promise, cost ceiling, and retention policy.
- Current first-party documentation plus credentials only for a narrowly approved live check.

## Current Contract

The public REST API uses the Exa API host and an Authorization Bearer header. SDKs can read EXA_API_KEY. Team Management uses a separately enabled service key against the admin API; hosted MCP normally uses OAuth, while enterprise managed authorization currently requires an eligible Exa organization, Claude organization, and Okta setup.

## Authentication

For normal REST work, inject `EXA_API_KEY` from an approved server-side secret manager and send it only as `Authorization: Bearer` to the configured first-party Exa API host. Team Management service keys, hosted MCP OAuth or enterprise managed authorization, and payment-protocol calls are separate trust models. Never print, commit, place in a URL, or expose a credential to an untrusted client.

## Instructions

1. Inventory the runtime, endpoint family, team, environment, and data class.
2. Choose exactly one supported authentication model for that boundary.
3. Place the credential in the approved secret manager and inject it only at runtime.
4. Pin the current SDK or raw-HTTP contract and validate configuration offline.
5. Run a synthetic read-only smoke check only when live access and spend are approved.
6. Record credential owner, scope, rotation path, test result, and rollback state.

## Tool Discipline

Use Read, Glob, and Grep to inspect repository code, configuration, fixtures, and evidence. Use Write and Edit only for approved implementation or documentation changes. Do not call Exa, run paid research, create or alter a Monitor, Webset, Agent run, Batch, team, member, API key, budget, webhook, or deployment merely because this skill was invoked.

## Approval Boundaries

Require an accountable owner before live queries involving sensitive intent, production credentials, spend or rate-limit changes, forced live crawling, generated summaries, external delivery, deployment, member or key changes, schedule creation, or destructive cancellation, stopping, deletion, or revocation. Read-only repository inspection and synthetic offline validation do not authorize live vendor actions.

## Failure Modes

- Do not send REST keys in URLs, browser bundles, logs, or client telemetry.
- A normal API key must not be treated as a Team Management service key.
- An MCP OAuth session does not authorize unrelated REST or administrative calls.

## Output

Return the operation scope, environment, team and product surface, authorization class, contract and policy decisions, deterministic validation results, content-free identifiers, status and cost counts, risks, cleanup or rollback state, and a concise pass or fail receipt. Exclude credentials, raw queries, prompts, presigned URLs, retrieved content, generated output, and customer-derived data unless separately approved.

## Example

- A server worker receives EXA_API_KEY from its production secret store, calls only the approved API host, and reports the request ID without revealing the key.
- Finish with request or resource IDs, assertion counts, cost and terminal state, rollback or deletion status, and the decision owner; never reproduce secrets or retrieved content.

## Validation

Rerun the smallest relevant deterministic test, compare actual behavior with the requested outcome and current first-party contract, verify sensitive fields are absent from evidence, and confirm deadlines, terminal state, downstream retention, and rollback before reporting success.

## References

Review the dated first-party evidence map before relying on any endpoint, parameter, search type, price, limit, beta, compliance, identity, retry, or lifecycle claim.

- [Current first-party evidence map](references/official-docs.md)
