---
name: alchemy-common-errors
description: >-
  Classify Alchemy authentication, JSON-RPC, Data API, throughput, and partial-response failures before applying bounded recovery. Use when an Alchemy integration fails or degrades. Trigger with "Alchemy error", "Alchemy 429", or "debug an Alchemy request".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<sanitized-request-id> <endpoint-class> <symptom>"
version: 2.0.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, alchemy, troubleshooting, reliability]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Alchemy access requires network access, an appropriate credential, account capacity, and explicit approval"
---
# Alchemy Error Classification and Recovery

## Overview

Classify Alchemy authentication, JSON-RPC, Data API, throughput, and partial-response failures before applying bounded recovery. This workflow produces a reviewable artifact and negative-path evidence before any live side effect.

## Prerequisites

- Current first-party Alchemy documentation for the selected product, chain, feature, client, authentication method, limit, and lifecycle.
- Named product, application, security, data/privacy, budget, release, and operations owners appropriate to the requested scope.
- Synthetic or approved non-production fixtures, a credential canary, explicit success criteria, and a tested rollback boundary.

## Current Contract

Alchemy surfaces transport status, JSON-RPC error objects, product-specific errors, and—in Portfolio workflows—partial errors inside an HTTP 200 response. Recovery depends on idempotency and failure class. Current limits and method availability are account, product, network, and time dependent; static plan tables are not diagnostic authority.

## Authentication

Collect only a credential fingerprint or key identifier, never the credential. Verify application state, network, allowlists, endpoint family, and credential class in the dashboard or approved inventory without copying secrets into commands or tickets.

## Instructions

1. Capture timestamp, endpoint family, network, method, sanitized parameters, HTTP status, JSON-RPC code, response headers, request ID, attempt count, and affected SLO.
2. Classify the failure as local validation, authentication/policy, unsupported method/network, throughput/quota, provider transient, deterministic RPC rejection, partial response, or downstream parsing.
3. Reproduce with a synthetic or public fixture and the same environment class; compare current service status, feature support, and account usage.
4. Correct invalid inputs or routing without retry; honor retry guidance for transient or throughput failures within an idempotency-aware budget.
5. For partial success, retain successful partitions and retry only failed partitions using their documented fresh-request contract.
6. Verify recovery and the exhaustion path, redact the evidence bundle, and escalate persistent provider failures with the request ID.

## Tool Discipline

Use Read, Glob, and Grep to inspect current documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Skill invocation alone does not authorize network access, credentials, wallet addresses, customer data, plan changes, spend, key creation or rotation, webhook changes, deployment, replay, transaction construction, signing, broadcast, or deletion.

## Approval Boundaries

Operations owns retry budgets and degraded behavior. Security owns credential incidents. Raising throughput, changing plans, replaying writes, or moving traffic to another provider requires the relevant budget/release approval.

## Error Handling

- A retry cannot repair invalid parameters, unsupported features, or the wrong credential class.
- Do not log request URLs that embed an API key or full user payloads.
- Do not interpret HTTP 200 as complete success for endpoints that can return partial errors.

## Output

Return the redacted failure envelope, classification, current evidence, causal hypothesis, bounded repair, negative-path result, unresolved impact, owner, and escalation receipt. Mark assumptions, observations, source dates, environment-specific behavior, owners, and unresolved gaps explicitly.

## Examples

- Classify a `429` using observed headers and account usage, then prove both a bounded recovery and a user-visible exhausted state.
- Classify a Portfolio HTTP 200 with `partialErrors` as degraded partial success, not a successful complete portfolio.

## Validation

Exercise and record expected and observed results for:

- invalid params
- wrong key class
- unsupported network
- 429 with retry guidance
- transient 5xx
- HTTP 200 partial failure

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated Alchemy sources before execution.
- Treat observed account, application, network, indexer, chain, or provider behavior as environment-specific evidence, never a universal guarantee.
