---
name: notion-common-errors
description: >-
  Classify Notion API failures and choose a bounded recovery path from the observed status and error code. Use when handling authentication, permission, validation, conflict, limit, or service errors. Trigger with "fix Notion error", "classify Notion 403", or "handle Notion 429".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<status-or-code> <operation> <environment>"
version: 1.40.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, notion, errors]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Notion actions require network access and explicit approval"
---
# Notion Error Classification and Recovery

## Overview

Classify Notion API failures and choose a bounded recovery path from the observed status and error code.. This workflow produces an auditable decision or artifact before any live action.

## Prerequisites

- Current first-party Notion documentation and the selected integration's tested API-version contract.
- A named workspace owner, content or data owner, and operation owner.
- Synthetic or approved non-production fixtures with secrets and workspace content removed.

## Current Contract

The response status, structured code, message, request identifier, and Retry-After header are evidence. Recovery differs for invalid credentials, restricted resources, wrong IDs, invalid payloads, conflicts, rate limits, and service faults. Recheck the dated evidence map before relying on mutable fields, endpoints, versions, limits, or delivery behavior.

## Authentication

Verify token presence through a fingerprint or secret-manager reference. Check connection capabilities and content sharing separately from identity.

## Instructions

1. Capture one redacted response envelope and the originating operation.
2. Map the status and structured code to authentication, authorization, validation, identity, concurrency, limit, or service class.
3. Check selected API version and page/database/data-source identity before changing code.
4. Apply the class-specific action: correct input, restore access, wait as instructed, reconcile conflict, or pause for service recovery.
5. Retry only retryable classes with a strict attempt and time budget.
6. Verify recovery with the least-privilege read or fixture that proves the original fault is gone.

## Tool Discipline

Use Read, Glob, and Grep to inspect documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Invocation alone does not authorize network access, credentials, workspace content, user data, file transfer, deployment, capability or sharing changes, writes, spend, or deletion.

## Approval Boundaries

Require approval before capability changes, content sharing, token rotation, write replay, bulk retry, or support disclosure.

## Error Handling

- Do not treat every 404 as absence; inaccessible content can be indistinguishable from a bad identifier.
- Respect Retry-After instead of a fixed sleep.
- Quarantine unknown codes rather than guessing.

## Output

Return the observed evidence, class, likely causes, ruled-out causes, recovery action, retry budget, and verification result. Identify assumptions, owners, expirations, and evidence gaps explicitly.

## Examples

- Differentiate a wrong data-source ID from missing page sharing.
- Pause a write queue on repeated conflicts instead of duplicating pages.

## Validation

Exercise and record these paths with expected and observed results:

- all documented classes
- unknown code
- Retry-After
- wrong object type
- revoked token
- service recovery

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources before relying on mutable behavior.
- Treat observed tenant behavior as environment-specific evidence, never a universal Notion guarantee.
