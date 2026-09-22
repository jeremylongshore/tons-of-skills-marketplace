---
name: notion-local-dev-loop
description: >-
  Create a repeatable local Notion development loop using fixtures, mocks, and an explicitly shared sandbox. Use when implementing or debugging without touching production content. Trigger with "develop Notion locally", "mock Notion API", or "set up Notion sandbox".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<repository> <feature> <sandbox-workspace>"
version: 1.40.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, notion, development]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Notion actions require network access and explicit approval"
---
# Notion Isolated Local Development Loop

## Overview

Create a repeatable local Notion development loop using fixtures, mocks, and an explicitly shared sandbox.. This workflow produces an auditable decision or artifact before any live action.

## Prerequisites

- Current first-party Notion documentation and the selected integration's tested API-version contract.
- A named workspace owner, content or data owner, and operation owner.
- Synthetic or approved non-production fixtures with secrets and workspace content removed.

## Current Contract

Local tests should model the selected API version, pagination, errors, additive fields, data-source identities, and current write semantics. A sandbox smoke test complements but does not replace deterministic fixtures. Recheck the dated evidence map before relying on mutable fields, endpoints, versions, limits, or delivery behavior.

## Authentication

Use a dedicated sandbox connection and secret store reference. Never copy production tokens, page IDs, exports, or response bodies into fixtures.

## Instructions

1. Pin the SDK, selected API version, runtime, and fixture schema.
2. Create synthetic page, data-source, block, webhook, limit, and error fixtures with secret canaries.
3. Wrap the client behind an operation boundary that records status and request IDs without content.
4. Implement offline unit and contract tests before a live sandbox check.
5. Run one bounded read and, only when approved, one reversible sandbox write.
6. Reset fixtures, verify no production identifiers entered the workspace, and preserve test evidence.

## Tool Discipline

Use Read, Glob, and Grep to inspect documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Invocation alone does not authorize network access, credentials, workspace content, user data, file transfer, deployment, capability or sharing changes, writes, spend, or deletion.

## Approval Boundaries

Require the sandbox owner before any live call and explicit approval for writes, webhooks, file uploads, or destructive reset.

## Error Handling

- Do not record live responses as fixtures without classification and redaction.
- Do not make tests depend on search propagation timing.
- Fail if configuration points to a production connection or object.

## Output

Return the environment contract, fixture manifest, test commands, sandbox access map, live-check receipt, and cleanup status. Identify assumptions, owners, expirations, and evidence gaps explicitly.

## Examples

- Develop a data-source query entirely from synthetic multi-page fixtures.
- Exercise a page write in a sandbox and restore its original state.

## Validation

Exercise and record these paths with expected and observed results:

- production guard
- secret canary
- pagination
- unknown field
- retry
- sandbox cleanup

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources before relying on mutable behavior.
- Treat observed tenant behavior as environment-specific evidence, never a universal Notion guarantee.
