---
name: exa-multi-env-setup
description: >-
  Separate Exa development, staging, and production credentials, budgets, schedules, data, and observability. Use when operating or reviewing this Exa boundary. Trigger with "Exa multi env setup", "review Exa multi env setup", or "fix Exa multi env setup".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<dev-team> <stage-team> <prod-team>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, exa]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Exa work requires network access"
---
# Exa Multi-environment Isolation

## Overview

Separate Exa development, staging, and production credentials, budgets, schedules, data, and observability. Treat credentials, queries, retrieved content, generated output, spend, and destructive state as separately governed boundaries.

## Prerequisites

- The target repository, environment, Exa team, product surface, and accountable owner.
- The workload's data classification, latency and freshness promise, cost ceiling, and retention policy.
- Current first-party documentation plus credentials only for a narrowly approved live check.

## Current Contract

Exa usage and paid access are organized through teams, and team members share plan features and limits. API keys can have names, rate limits, and budgets when Team Management is enabled. Environment isolation must be designed rather than inferred from a key name.

## Authentication

For normal REST work, inject `EXA_API_KEY` from an approved server-side secret manager and send it only as `Authorization: Bearer` to the configured first-party Exa API host. Team Management service keys, hosted MCP OAuth or enterprise managed authorization, and payment-protocol calls are separate trust models. Never print, commit, place in a URL, or expose a credential to an untrusted client.

## Instructions

1. Inventory teams, organizations, members, service keys, API keys, and owners.
2. Assign each environment an explicit team or documented isolation boundary.
3. Create narrowly named keys with budgets and rate limits where supported.
4. Prevent production keys from preview, developer, and forked-CI contexts.
5. Namespace Monitor, Webset, Agent, Batch, and evidence identifiers by environment.
6. Test revocation, promotion, teardown, and cross-environment denial.

## Tool Discipline

Use Read, Glob, and Grep to inspect repository code, configuration, fixtures, and evidence. Use Write and Edit only for approved implementation or documentation changes. Do not call Exa, run paid research, create or alter a Monitor, Webset, Agent run, Batch, team, member, API key, budget, webhook, or deployment merely because this skill was invoked.

## Approval Boundaries

Require an accountable owner before live queries involving sensitive intent, production credentials, spend or rate-limit changes, forced live crawling, generated summaries, external delivery, deployment, member or key changes, schedule creation, or destructive cancellation, stopping, deletion, or revocation. Read-only repository inspection and synthetic offline validation do not authorize live vendor actions.

## Failure Modes

- Multiple keys in one team can still share plan and capacity boundaries.
- Copying production data into staging changes the data-governance scope.
- Deleting a deployment does not remove vendor-side scheduled resources.

## Output

Return the operation scope, environment, team and product surface, authorization class, contract and policy decisions, deterministic validation results, content-free identifiers, status and cost counts, risks, cleanup or rollback state, and a concise pass or fail receipt. Exclude credentials, raw queries, prompts, presigned URLs, retrieved content, generated output, and customer-derived data unless separately approved.

## Example

- Development uses synthetic queries and a small key budget; production has separate ownership, limits, alerts, and scheduled-resource inventory.
- Finish with request or resource IDs, assertion counts, cost and terminal state, rollback or deletion status, and the decision owner; never reproduce secrets or retrieved content.

## Validation

Rerun the smallest relevant deterministic test, compare actual behavior with the requested outcome and current first-party contract, verify sensitive fields are absent from evidence, and confirm deadlines, terminal state, downstream retention, and rollback before reporting success.

## References

Review the dated first-party evidence map before relying on any endpoint, parameter, search type, price, limit, beta, compliance, identity, retry, or lifecycle claim.

- [Current first-party evidence map](references/official-docs.md)
