---
name: notion-known-pitfalls
description: >-
  Audit a Notion integration for recurring identity, access, version, pagination, webhook, and mutation mistakes. Use when reviewing a release or investigating confusing failures. Trigger with "review Notion pitfalls", "find Notion integration mistakes", or "check Notion assumptions".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<repository-or-design> <environment> <risk-focus>"
version: 1.40.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, notion, review]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Notion actions require network access and explicit approval"
---
# Notion Integration Pitfall Review

## Overview

Audit a Notion integration for recurring identity, access, version, pagination, webhook, and mutation mistakes.. This workflow produces an auditable decision or artifact before any live action.

## Prerequisites

- Current first-party Notion documentation and the selected integration's tested API-version contract.
- A named workspace owner, content or data owner, and operation owner.
- Synthetic or approved non-production fixtures with secrets and workspace content removed.

## Current Contract

Common failures arise from confusing databases with data sources, assuming capabilities equal content access, omitting pagination, pinning stale object shapes, treating webhooks as a ledger, or retrying writes without idempotency. Recheck the dated evidence map before relying on mutable fields, endpoints, versions, limits, or delivery behavior.

## Authentication

Check that the code distinguishes connection models, workspace binding, capabilities, shared content, and secret lifecycle.

## Instructions

1. Inventory all Notion clients, selected versions, tokens, object IDs, operations, and data flows.
2. Trace every database, data-source, page, block, file, search, and webhook assumption to first-party docs or a fixture.
3. Check pagination, size limits, unknown fields, error classes, Retry-After, and retry budgets.
4. Check idempotency, pre-state, read-back, compensation, and destructive-action approvals.
5. Check webhook signature, duplicate, ordering, aggregation, fetch-current, and reconciliation behavior.
6. Rank findings by exploitability, data impact, recurrence, and ease of correction.

## Tool Discipline

Use Read, Glob, and Grep to inspect documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Invocation alone does not authorize network access, credentials, workspace content, user data, file transfer, deployment, capability or sharing changes, writes, spend, or deletion.

## Approval Boundaries

Require approval before using live credentials or content to confirm a suspected pitfall; repository inspection remains read-only by default.

## Error Handling

- Do not fix a 404 by broadening access without proving identity.
- Do not assume a single search or query page is complete.
- Do not silently coerce legacy payloads into current writes.

## Output

Return the pitfall inventory, evidence, impact, false-positive notes, corrective action, owner, and verification test. Identify assumptions, owners, expirations, and evidence gaps explicitly.

## Examples

- Find a database ID passed to a data-source query.
- Find a webhook handler that trusts delivery order and never reconciles.

## Validation

Exercise and record these paths with expected and observed results:

- wrong ID type
- unshared content
- pagination
- unknown fields
- write retry
- webhook replay

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources before relying on mutable behavior.
- Treat observed tenant behavior as environment-specific evidence, never a universal Notion guarantee.
