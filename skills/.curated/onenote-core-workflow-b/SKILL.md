---
name: onenote-core-workflow-b
description: >-
  Create or update OneNote page content with an HTML preview, stable targets, read-back verification, and compensation. Use when an approved workflow must write a page. Trigger with "create OneNote page", "update OneNote content", or "append OneNote HTML".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<section-or-page-id> <change-intent> <idempotency-key>"
version: 1.7.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, onenote, content]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live OneNote actions require network access, delegated authentication, and explicit approval"
---
# OneNote Controlled Page Change

## Overview

Create or update OneNote page content with an HTML preview, stable targets, read-back verification, and compensation.. This workflow produces an auditable decision or artifact before any live action.

## Prerequisites

- Current first-party Microsoft Graph OneNote documentation and the selected integration's tested contract.
- Named identity, content, workload, security, and operations owners appropriate to the requested scope.
- Synthetic or approved non-production fixtures with secrets and real notebook content removed.

## Current Contract

Page creation accepts constrained input HTML and uses multipart content when binary parts are present. Updates target elements by data-id or generated IDs returned by an includeIDs read; output HTML is normalized and is not a byte-for-byte echo of input. Recheck the dated evidence map before relying on mutable permissions, limits, SDK behavior, supported resources, or cloud availability.

## Authentication

Use delegated Notes.ReadWrite for the signed-in user only after the target section or page is approved. Keep credential values and notebook bodies out of logs.

## Instructions

1. Resolve the exact location, section or page ID, current content revision, and content owner.
2. Build well-formed UTF-8 input HTML and a semantic preview of every intended change.
3. Choose direct HTML or multipart creation, or resolve update targets from an includeIDs content read.
4. Validate supported elements, binary parts, request size, and idempotency behavior offline.
5. Apply one approved mutation and persist the returned page identity before downstream work.
6. Read back the page, compare semantic state, and preserve a compensation or quarantine plan.

## Tool Discipline

Use Read, Glob, and Grep to inspect documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Invocation alone does not authorize network access, delegated credentials, tenant or notebook content, consent, file transfer, deployment, writes, spend, sharing changes, or deletion.

## Approval Boundaries

Require content-owner approval for every create or update and separate approval for binary upload, broad replacement, cross-root copy, or deletion.

## Error Handling

- Do not assume returned HTML equals input HTML.
- Do not invent update IDs in submitted HTML; resolve server-generated targets.
- After an ambiguous timeout, reconcile the idempotency record before retrying.

## Output

Return the target identity, pre-state, semantic preview, approval, response identity, normalized read-back, conflicts, and compensation plan. Identify assumptions, owners, expirations, and evidence gaps explicitly.

## Examples

- Create a synthetic text-only page and verify its title and semantic body.
- Append to one stable target while preserving adjacent content.

## Validation

Exercise and record these paths with expected and observed results:

- unsupported element
- malformed XHTML
- multipart binary
- ambiguous timeout
- target drift
- read-back mismatch

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources before relying on mutable behavior.
- Treat observed tenant behavior as environment-specific evidence, never a universal OneNote guarantee.
