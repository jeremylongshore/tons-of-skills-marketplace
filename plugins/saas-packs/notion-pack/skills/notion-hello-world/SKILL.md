---
name: notion-hello-world
description: >-
  Prove a Notion connection, API version, and shared-content boundary with a minimal read-only check. Use when onboarding or diagnosing initial access. Trigger with "test Notion connection", "Notion hello world", or "verify Notion token".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<connection-alias> <fixture-page-or-data-source> <environment>"
version: 1.40.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, notion, onboarding]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Notion actions require network access and explicit approval"
---
# Notion Read-Only Connection Proof

## Overview

Prove a Notion connection, API version, and shared-content boundary with a minimal read-only check.. This workflow produces an auditable decision or artifact before any live action.

## Prerequisites

- Current first-party Notion documentation and the selected integration's tested API-version contract.
- A named workspace owner, content or data owner, and operation owner.
- Synthetic or approved non-production fixtures with secrets and workspace content removed.

## Current Contract

The smallest safe proof identifies the bot or token context and retrieves one explicitly shared non-sensitive fixture. Search results alone do not prove access to arbitrary workspace content. Recheck the dated evidence map before relying on mutable fields, endpoints, versions, limits, or delivery behavior.

## Authentication

Use an approved non-production bearer secret through the runtime secret store. Record only its connection alias and one-way fingerprint.

## Instructions

1. Confirm the connection type, environment, token owner, and selected tested API version.
2. Share one synthetic fixture page or data source with read-only capability.
3. Retrieve the current bot identity and record content-free metadata.
4. Retrieve the fixture by its exact ID and confirm the expected object type.
5. Exercise one denied path against an intentionally unshared fixture.
6. Remove temporary access if created and preserve the redacted proof.

## Tool Discipline

Use Read, Glob, and Grep to inspect documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Invocation alone does not authorize network access, credentials, workspace content, user data, file transfer, deployment, capability or sharing changes, writes, spend, or deletion.

## Approval Boundaries

Require the workspace owner before creating a connection or sharing content; do not create or modify pages in this workflow.

## Error Handling

- A 200 response from bot identity does not prove content access.
- Do not paste the token into a command history or artifact.
- Stop if the fixture contains real workspace data.

## Output

Return the connection alias, environment, selected version, bot fingerprint, fixture identity, allow/deny results, and cleanup receipt. Identify assumptions, owners, expirations, and evidence gaps explicitly.

## Examples

- Prove access to one synthetic page and denial of an unshared page.
- Verify a data-source identity without querying business rows.

## Validation

Exercise and record these paths with expected and observed results:

- valid token
- revoked token
- shared fixture
- unshared fixture
- wrong object ID
- secret leakage

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources before relying on mutable behavior.
- Treat observed tenant behavior as environment-specific evidence, never a universal Notion guarantee.
