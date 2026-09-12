---
name: notion-content-management
description: >-
  Plan and verify safe Notion page, block, markdown, and file-content changes with previews and rollback evidence. Use when creating, updating, moving, or trashing workspace content. Trigger with "edit Notion content", "publish Notion page", or "manage Notion blocks".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<content-scope> <change-intent> <environment>"
version: 1.40.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, notion, content]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Notion actions require network access and explicit approval"
---
# Notion Content Change Control

## Overview

Plan and verify safe Notion page, block, markdown, and file-content changes with previews and rollback evidence.. This workflow produces an auditable decision or artifact before any live action.

## Prerequisites

- Current first-party Notion documentation and the selected integration's tested API-version contract.
- A named workspace owner, content or data owner, and operation owner.
- Synthetic or approved non-production fixtures with secrets and workspace content removed.

## Current Contract

Current content operations distinguish pages, blocks, databases, and data sources. Block placement uses the current position object; current REST trash state and enhanced-markdown behavior must come from the selected version contract. Recheck the dated evidence map before relying on mutable fields, endpoints, versions, limits, or delivery behavior.

## Authentication

Use a connection with only the content capabilities needed for the approved scope. Confirm the exact parent and content-sharing path before any mutation.

## Instructions

1. Resolve stable IDs and capture a pre-change snapshot, revision marker, and content owner.
2. Choose page properties, block operations, enhanced markdown, or file uploads based on the documented object contract.
3. Build a semantic preview showing creates, replacements, moves, and trash actions.
4. Validate payload size, nesting, unsupported blocks, file lifecycle, and version shape offline.
5. Apply the smallest approved change with idempotency and conflict detection.
6. Read back the changed scope and preserve rollback material until acceptance.

## Tool Discipline

Use Read, Glob, and Grep to inspect documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Invocation alone does not authorize network access, credentials, workspace content, user data, file transfer, deployment, capability or sharing changes, writes, spend, or deletion.

## Approval Boundaries

Require content-owner approval for every write; require separate approval for replacement, move, trash, file upload, broad descendant access, or public sharing.

## Error Handling

- Never replace an entire page when a bounded block or property update is sufficient.
- Do not reuse expiring download URLs as durable file identifiers.
- Stop on concurrent edits or an unexpected parent.

## Output

Return the content manifest, semantic diff, approvals, applied IDs, read-back evidence, conflicts, and rollback package. Identify assumptions, owners, expirations, and evidence gaps explicitly.

## Examples

- Append an approved section at the end of a page and verify its blocks.
- Trash a duplicate only after preserving its parent and restoration evidence.

## Validation

Exercise and record these paths with expected and observed results:

- preview exactness
- unsupported blocks
- position semantics
- file completion
- concurrent edit
- restore path

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources before relying on mutable behavior.
- Treat observed tenant behavior as environment-specific evidence, never a universal Notion guarantee.
