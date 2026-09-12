---
name: onenote-common-errors
description: >-
  Classify Microsoft Graph OneNote failures from redacted response evidence and choose a bounded recovery path. Use when handling authentication, permission, provisioning, validation, throttling, or content errors. Trigger with "fix OneNote error", "classify OneNote 403", or "debug OneNote request".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<status-or-code> <operation> <location>"
version: 1.7.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, onenote, errors]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live OneNote actions require network access, delegated authentication, and explicit approval"
---
# OneNote Error Triage and Recovery

## Overview

Classify Microsoft Graph OneNote failures from redacted response evidence and choose a bounded recovery path.. This workflow produces an auditable decision or artifact before any live action.

## Prerequisites

- Current first-party Microsoft Graph OneNote documentation and the selected integration's tested contract.
- Named identity, content, workload, security, and operations owners appropriate to the requested scope.
- Synthetic or approved non-production fixtures with secrets and real notebook content removed.

## Current Contract

HTTP status, Graph error code, inner error, request identifier, target location, auth context, and operation are separate evidence. OneNote 429 responses do not promise a Retry-After header, and a user, group, or site root can fail for different access or provisioning reasons. Recheck the dated evidence map before relying on mutable permissions, limits, SDK behavior, supported resources, or cloud availability.

## Authentication

Record a delegated token alias, tenant alias, signed-in user alias, granted Notes scope, and target ownership. Never paste or decode bearer tokens into an incident artifact.

## Instructions

1. Capture one redacted response envelope and the exact read or write operation.
2. Classify the failure as transport, authentication, authorization, provisioning, identity, validation, throttling, conflict, or service state.
3. Check the user, group, or site root and the notebook, section, page, or resource identity separately.
4. Apply the smallest class-specific correction without broadening permissions by default.
5. Retry only retryable classes within a strict attempt and elapsed-time budget.
6. Verify recovery with the least-privilege read or synthetic fixture that reproduces the original path.

## Tool Discipline

Use Read, Glob, and Grep to inspect documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Invocation alone does not authorize network access, delegated credentials, tenant or notebook content, consent, file transfer, deployment, writes, spend, sharing changes, or deletion.

## Approval Boundaries

Require the signed-in user or content owner before a new content read. Require security approval for consent or credential changes and content-owner approval before replaying writes.

## Error Handling

- Do not turn every 403 into a broader Notes scope request.
- When 429 omits Retry-After, use bounded exponential backoff with jitter.
- Quarantine unknown Graph codes and preserve the request identifier.

## Output

Return the evidence envelope, fault class, ruled-out causes, minimal action, retry budget, verification result, and escalation package. Identify assumptions, owners, expirations, and evidence gaps explicitly.

## Examples

- Differentiate an unprovisioned OneNote store from an expired delegated session.
- Distinguish malformed input HTML from an inaccessible target section.

## Validation

Exercise and record these paths with expected and observed results:

- 401
- 403
- 404
- 400 validation
- 429 without server delay
- 5xx recovery

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources before relying on mutable behavior.
- Treat observed tenant behavior as environment-specific evidence, never a universal OneNote guarantee.
