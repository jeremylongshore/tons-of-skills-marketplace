---
name: notion-sdk-patterns
description: >-
  Build a version-aware Notion SDK boundary with typed operations, pagination, error classification, and test seams. Use when writing or reviewing client code. Trigger with "design Notion SDK wrapper", "review Notion client code", or "update Notion SDK patterns".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<language> <operations> <api-version>"
version: 1.40.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, notion, sdk]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Notion actions require network access and explicit approval"
---
# Notion SDK Contract Patterns

## Overview

Build a version-aware Notion SDK boundary with typed operations, pagination, error classification, and test seams.. This workflow produces an auditable decision or artifact before any live action.

## Prerequisites

- Current first-party Notion documentation and the selected integration's tested API-version contract.
- A named workspace owner, content or data owner, and operation owner.
- Synthetic or approved non-production fixtures with secrets and workspace content removed.

## Current Contract

The official JavaScript SDK exposes current database, data-source, page, block, file, search, and auth operations. Pin and test an SDK/API combination; tolerate additive response fields and isolate vendor shapes. Recheck the dated evidence map before relying on mutable fields, endpoints, versions, limits, or delivery behavior.

## Authentication

Construct clients from a secret provider and tenant-bound connection profile. Never accept raw credentials through business-method arguments or return them in errors.

## Instructions

1. Define a narrow interface in domain terms rather than exporting the entire SDK client.
2. Pin the SDK and selected tested API version with an upgrade matrix.
3. Implement data-source identity resolution, complete pagination, property decoding, and unknown-field tolerance.
4. Classify structured errors and Retry-After before applying bounded retry.
5. Add idempotency and read-back at write boundaries, not inside generic transport retry.
6. Test adapters with fixtures plus a bounded non-production contract lane.

## Tool Discipline

Use Read, Glob, and Grep to inspect documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Invocation alone does not authorize network access, credentials, workspace content, user data, file transfer, deployment, capability or sharing changes, writes, spend, or deletion.

## Approval Boundaries

Require review before exposing a new operation, capability, user field, content type, or live-write test.

## Error Handling

- Do not cast legacy database-query responses into current data-source types.
- Do not retry all SDK exceptions.
- Do not let an SDK default silently choose the production API contract.

## Output

Return the interface, dependency and version pins, adapters, error map, pagination helper, write invariants, and contract tests. Identify assumptions, owners, expirations, and evidence gaps explicitly.

## Examples

- Wrap a data-source query behind a paginated domain iterator.
- Decode unknown additive fields without failing the whole response.

## Validation

Exercise and record these paths with expected and observed results:

- multi-page
- unknown field
- wrong ID type
- 429
- timed-out write
- SDK upgrade

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources before relying on mutable behavior.
- Treat observed tenant behavior as environment-specific evidence, never a universal Notion guarantee.
