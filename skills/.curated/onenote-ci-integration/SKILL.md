---
name: onenote-ci-integration
description: >-
  Build deterministic CI gates for a OneNote integration without exposing delegated credentials or mutating real notebooks. Use when testing client, HTML, pagination, or migration changes. Trigger with "test OneNote in CI", "gate OneNote contracts", or "add OneNote fixtures".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<repository> <test-scope> <trusted-environment>"
version: 1.7.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, onenote, ci]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live OneNote actions require network access, delegated authentication, and explicit approval"
---
# OneNote Contract-Safe CI

## Overview

Build deterministic CI gates for a OneNote integration without exposing delegated credentials or mutating real notebooks.. This workflow produces an auditable decision or artifact before any live action.

## Prerequisites

- Current first-party Microsoft Graph OneNote documentation and the selected integration's tested contract.
- Named identity, content, workload, security, and operations owners appropriate to the requested scope.
- Synthetic or approved non-production fixtures with secrets and real notebook content removed.

## Current Contract

Pull requests can prove request construction, constrained HTML, pagination, errors, and retry behavior offline. A live test requires a trusted branch, a dedicated user-bound sandbox, synthetic content, and an explicit read or write boundary. Recheck the dated evidence map before relying on mutable permissions, limits, SDK behavior, supported resources, or cloud availability.

## Authentication

Keep delegated test credentials in an approved secret store. Fork jobs receive no secrets; logs record only tenant and user aliases, operation classes, status codes, and request identifiers.

## Instructions

1. Inventory OneNote calls, SDK versions, request builders, fixtures, and existing CI trust boundaries.
2. Define offline tests for service roots, paging, HTML normalization, update targets, errors, and throttling.
3. Separate untrusted pull-request jobs from protected trusted-branch smoke tests.
4. Scope any live lane to a synthetic notebook and one named delegated test user.
5. Make live writes opt-in, reversible, serialized, and followed by exact cleanup verification.
6. Gate promotion on negative cases, secret canaries, deterministic fixtures, and named rollback ownership.

## Tool Discipline

Use Read, Glob, and Grep to inspect documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Invocation alone does not authorize network access, delegated credentials, tenant or notebook content, consent, file transfer, deployment, writes, spend, sharing changes, or deletion.

## Approval Boundaries

Require repository-admin and sandbox-owner approval before enabling secrets or live calls. Require a separate approval for any write, sharing change, or cleanup deletion.

## Error Handling

- Treat a skipped trusted live lane as unknown, not passed.
- Stop if a fork receives a secret or a fixture contains real notebook content.
- Never update golden fixtures automatically from a live tenant.

## Output

Return the CI trust matrix, fixture inventory, commands, live-test boundary, redacted receipts, cleanup evidence, and failing owners. Identify assumptions, owners, expirations, and evidence gaps explicitly.

## Examples

- Reject a request that assumes one unpaged response is complete.
- Normalize created HTML in a fixture and compare semantic content rather than raw echo bytes.

## Validation

Exercise and record these paths with expected and observed results:

- fork isolation
- secret canary
- next-link paging
- HTML normalization
- 429 without Retry-After
- sandbox cleanup

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources before relying on mutable behavior.
- Treat observed tenant behavior as environment-specific evidence, never a universal OneNote guarantee.
