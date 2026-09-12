---
name: notion-upgrade-migration
description: >-
  Upgrade a Notion integration across SDK or API contracts with inventory, compatibility tests, staged rollout, and rollback. Use when adopting current data-source, block, trash, or SDK behavior. Trigger with "upgrade Notion API", "migrate Notion SDK", or "update Notion version".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<current-contract> <target-contract> <repository>"
version: 1.40.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, notion, upgrade]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Notion actions require network access and explicit approval"
---
# Notion SDK and API Upgrade Control

## Overview

Upgrade a Notion integration across SDK or API contracts with inventory, compatibility tests, staged rollout, and rollback.. This workflow produces an auditable decision or artifact before any live action.

## Prerequisites

- Current first-party Notion documentation and the selected integration's tested API-version contract.
- A named workspace owner, content or data owner, and operation owner.
- Synthetic or approved non-production fixtures with secrets and workspace content removed.

## Current Contract

Recent contracts separated databases from data sources and changed search filters; the current contract also changes block placement, trash state, and a meeting-note block identity. SDK support and API opt-in are related but separate choices. Recheck the dated evidence map before relying on mutable fields, endpoints, versions, limits, or delivery behavior.

## Authentication

Run upgrade tests with a dedicated non-production connection and synthetic content. Never rotate production credentials merely to test compatibility.

## Instructions

1. Inventory every client, explicit or default API version, SDK pin, operation, object type, fixture, and webhook subscription version.
2. Read both intervening first-party upgrade guides and build a before/after contract matrix.
3. Replace database-query assumptions with data-source identities and update search and schema operations.
4. Update current block position, trash-state, and meeting-note handling plus unknown-field tolerance.
5. Run offline fixtures, dual-read comparisons, denied paths, reversible sandbox writes, and rollback tests.
6. Canary one bounded workload, reconcile results, and promote only with a retained rollback artifact.

## Tool Discipline

Use Read, Glob, and Grep to inspect documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Invocation alone does not authorize network access, credentials, workspace content, user data, file transfer, deployment, capability or sharing changes, writes, spend, or deletion.

## Approval Boundaries

Require release approval for version or SDK promotion and content-owner approval for any live compatibility write or migration.

## Error Handling

- Do not update the SDK and silently inherit a new API contract.
- Do not cast old fixtures into new types to make tests pass.
- Rollback on object-identity, trash-state, or reconciliation divergence.

## Output

Return the inventory, contract delta, code and fixture changes, compatibility matrix, canary evidence, decision, and rollback package. Identify assumptions, owners, expirations, and evidence gaps explicitly.

## Examples

- Migrate a database query to a data-source query using the resolved data-source ID.
- Verify current trash and block-position behavior in a reversible sandbox.

## Validation

Exercise and record these paths with expected and observed results:

- multiple data sources
- search filter
- block position
- trash state
- unknown field
- rollback

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources before relying on mutable behavior.
- Treat observed tenant behavior as environment-specific evidence, never a universal Notion guarantee.
