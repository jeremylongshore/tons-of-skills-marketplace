---
name: exa-enterprise-rbac
description: >-
  Govern Exa membership, API and service keys, team budgets, MCP OAuth, and enterprise managed authorization through least privilege and revocation evidence. Use when operating or reviewing this Exa boundary. Trigger with "Exa enterprise rbac", "review Exa enterprise rbac", or "fix Exa enterprise rbac".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<organization> <team> <role-change>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, exa]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Exa work requires network access"
---
# Exa Team and Enterprise Access Governance

## Overview

Govern Exa membership, API and service keys, team budgets, MCP OAuth, and enterprise managed authorization through least privilege and revocation evidence. Treat credentials, queries, retrieved content, generated output, spend, and destructive state as separately governed boundaries.

## Prerequisites

- The target repository, environment, Exa team, product surface, and accountable owner.
- The workload's data classification, latency and freshness promise, cost ceiling, and retention policy.
- Current first-party documentation plus credentials only for a narrowly approved live check.

## Current Contract

Exa teams own usage and plan features; team admins invite members. Team Management is separately enabled and uses service keys to manage API keys. Enterprise managed authorization for Claude follows Okta directory state for eligible organizations, uses auth.exa.ai and mcp.exa.ai/mcp with scope mcp:tools, and does not create users.

## Authentication

For normal REST work, inject `EXA_API_KEY` from an approved server-side secret manager and send it only as `Authorization: Bearer` to the configured first-party Exa API host. Team Management service keys, hosted MCP OAuth or enterprise managed authorization, and payment-protocol calls are separate trust models. Never print, commit, place in a URL, or expose a credential to an untrusted client.

## Instructions

1. Inventory organization, teams, admins, members, keys, OAuth clients, and workloads.
2. Map each human and service identity to an accountable owner and required surface.
3. Separate administrative service keys from ordinary runtime keys.
4. Apply key budgets and rate limits where the enabled API supports them.
5. Test member removal, key revocation, directory deprovisioning, and MCP session termination.
6. Review access, orphaned schedules, spend, and exceptions on a fixed cadence.

## Tool Discipline

Use Read, Glob, and Grep to inspect repository code, configuration, fixtures, and evidence. Use Write and Edit only for approved implementation or documentation changes. Do not call Exa, run paid research, create or alter a Monitor, Webset, Agent run, Batch, team, member, API key, budget, webhook, or deployment merely because this skill was invoked.

## Approval Boundaries

Require an accountable owner before live queries involving sensitive intent, production credentials, spend or rate-limit changes, forced live crawling, generated summaries, external delivery, deployment, member or key changes, schedule creation, or destructive cancellation, stopping, deletion, or revocation. Read-only repository inspection and synthetic offline validation do not authorize live vendor actions.

## Failure Modes

- A team membership model is not a claim of fine-grained resource RBAC.
- Enterprise managed authorization requires pre-provisioned matching users.
- Removing an application key does not revoke a user's OAuth or managed-auth access.

## Output

Return the operation scope, environment, team and product surface, authorization class, contract and policy decisions, deterministic validation results, content-free identifiers, status and cost counts, risks, cleanup or rollback state, and a concise pass or fail receipt. Exclude credentials, raw queries, prompts, presigned URLs, retrieved content, generated output, and customer-derived data unless separately approved.

## Example

- A production worker gets a budgeted runtime key; only a controlled automation service gets the separately enabled Team Management service key.
- Finish with request or resource IDs, assertion counts, cost and terminal state, rollback or deletion status, and the decision owner; never reproduce secrets or retrieved content.

## Validation

Rerun the smallest relevant deterministic test, compare actual behavior with the requested outcome and current first-party contract, verify sensitive fields are absent from evidence, and confirm deadlines, terminal state, downstream retention, and rollback before reporting success.

## References

Review the dated first-party evidence map before relying on any endpoint, parameter, search type, price, limit, beta, compliance, identity, retry, or lifecycle claim.

- [Current first-party evidence map](references/official-docs.md)
