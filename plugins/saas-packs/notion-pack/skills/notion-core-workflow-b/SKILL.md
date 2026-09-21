---
name: notion-core-workflow-b
description: >-
  Create or update Notion pages and blocks with an idempotency key, semantic diff, and read-back verification. Use when an integration must write approved content. Trigger with "create Notion record", "update Notion page", or "append Notion blocks".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<parent-or-page-id> <write-intent> <idempotency-key>"
version: 1.40.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, notion, writes]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Notion actions require network access and explicit approval"
---
# Notion Idempotent Page Write Workflow

## Overview

Create or update Notion pages and blocks with an idempotency key, semantic diff, and read-back verification.. This workflow produces an auditable decision or artifact before any live action.

## Prerequisites

- Current first-party Notion documentation and the selected integration's tested API-version contract.
- A named workspace owner, content or data owner, and operation owner.
- Synthetic or approved non-production fixtures with secrets and workspace content removed.

## Current Contract

Page properties follow the parent data source schema; page body content is a block tree or enhanced markdown. Current placement and trash semantics depend on the pinned API contract. Recheck the dated evidence map before relying on mutable fields, endpoints, versions, limits, or delivery behavior.

## Authentication

Use only insert or update content capability required by the operation. Confirm parent access and keep lookup identities separate from write identities when risk warrants.

## Instructions

1. Resolve the exact parent, page, data source, and current revision.
2. Derive an idempotency key from the business object and operation version.
3. Render a semantic diff for properties, blocks, parent, and trash state.
4. Validate property types, relation targets, size limits, and block nesting offline.
5. Apply one approved mutation and persist the returned object ID before downstream work.
6. Read back the object, compare intended state, and retain compensation instructions.

## Tool Discipline

Use Read, Glob, and Grep to inspect documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Invocation alone does not authorize network access, credentials, workspace content, user data, file transfer, deployment, capability or sharing changes, writes, spend, or deletion.

## Approval Boundaries

Require the content owner before insert, update, move, append, replacement, comment creation, or trash operations.

## Error Handling

- Do not retry a timed-out create until searching the idempotency record.
- Do not coerce a property into a new type to make a payload pass.
- Stop if the parent or revision changed after approval.

## Output

Return the target identity, idempotency key, pre-state, approved diff, response identity, read-back delta, and compensation plan. Identify assumptions, owners, expirations, and evidence gaps explicitly.

## Examples

- Upsert one business record without duplicating it after a timeout.
- Append approved blocks and verify their order under the target page.

## Validation

Exercise and record these paths with expected and observed results:

- duplicate retry
- schema mismatch
- relation access
- position order
- concurrent change
- compensation

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources before relying on mutable behavior.
- Treat observed tenant behavior as environment-specific evidence, never a universal Notion guarantee.
