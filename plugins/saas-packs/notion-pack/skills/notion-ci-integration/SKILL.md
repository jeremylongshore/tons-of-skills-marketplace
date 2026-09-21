---
name: notion-ci-integration
description: >-
  Build CI checks for Notion integration contracts without exposing tokens or mutating production content. Use when gating SDK, schema, fixture, or migration changes. Trigger with "test Notion in CI", "gate Notion schema drift", or "add Notion contract checks".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<repository> <test-scope> <environment>"
version: 1.40.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, notion, ci]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Notion actions require network access and explicit approval"
---
# Notion Contract-Safe CI Integration

## Overview

Build CI checks for Notion integration contracts without exposing tokens or mutating production content.. This workflow produces an auditable decision or artifact before any live action.

## Prerequisites

- Current first-party Notion documentation and the selected integration's tested API-version contract.
- A named workspace owner, content or data owner, and operation owner.
- Synthetic or approved non-production fixtures with secrets and workspace content removed.

## Current Contract

CI should validate local contracts by default. Any live smoke test needs a dedicated non-production connection, explicitly shared fixture content, bounded reads, and a pinned tested API version. Recheck the dated evidence map before relying on mutable fields, endpoints, versions, limits, or delivery behavior.

## Authentication

Use short-lived CI secret delivery where supported and a least-privilege non-production token. Mask values and prevent fork jobs from receiving secrets.

## Instructions

1. Define offline unit, schema, pagination, error, webhook-signature, and migration fixtures.
2. Pin the SDK and tested API version in the dependency and contract matrix.
3. Separate secret-free pull-request jobs from trusted-branch live smoke tests.
4. Make the live lane read-only, fixture-scoped, time-bounded, and concurrency-limited.
5. Capture redacted status, error code, and request identifier without response content.
6. Gate promotion on exact fixtures, negative paths, rollback evidence, and named ownership.

## Tool Discipline

Use Read, Glob, and Grep to inspect documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Invocation alone does not authorize network access, credentials, workspace content, user data, file transfer, deployment, capability or sharing changes, writes, spend, or deletion.

## Approval Boundaries

Require repository-admin and workspace-owner approval before enabling secrets, live reads, writes, scheduled jobs, or third-party CI access.

## Error Handling

- Fork pull requests must never receive Notion credentials.
- A skipped trusted live job is not a pass; report it distinctly.
- Do not auto-update snapshots from live production responses.

## Output

Return the CI trust matrix, job definitions, fixture inventory, secret provenance, gate results, and remediation owner. Identify assumptions, owners, expirations, and evidence gaps explicitly.

## Examples

- Reject a pull request that reintroduces an old object shape.
- Run a read-only bot-identity probe only on a protected trusted branch.

## Validation

Exercise and record these paths with expected and observed results:

- fork isolation
- secret masking
- offline determinism
- negative fixtures
- live-read boundary
- rollback gate

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources before relying on mutable behavior.
- Treat observed tenant behavior as environment-specific evidence, never a universal Notion guarantee.
