---
name: linktree-debug-bundle
description: 'Assemble a minimal, redacted Linktree troubleshooting bundle for support or incident handoff. Use when a profile, destination, Insights view, or partner integration fails. Trigger with "build Linktree debug bundle".'
argument-hint: "[incident-id] [symptom]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- linktree
- debugging
- support
- redaction
model: inherit
effort: medium
compatibility: Designed for Claude Code; live work requires an authorized Linktree account and approval from the profile, Workspace, data, or partner-integration owner
---
# Linktree Redacted Operator Evidence Bundle

## Overview

Capture reproducible evidence across the public profile, Admin observation, destination, service status, and approved adapter without leaking sessions, subscribers, or private contracts.

## Prerequisites

- An authorized Linktree account or a clearly bounded design-only task
- The profile, Workspace, destination, campaign, data, or integration owner appropriate to the requested change
- Current account evidence for plan-dependent features and user-supplied approved partner documentation for every private interface

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect repository specifications, sanitized fixtures, policies, tests, and prior receipts.

Use `WebFetch` only for current official Linktree documentation or explicitly approved partner documentation.

Use `Write` or `Edit` only after confirming scope, target, owners, data classification, and approval state. These tools do not confer Linktree access, account authority, or permission to process visitor data. Return exact operator steps or an approval-gated handoff when a live action is not authorized.

## Current Contract

- Linktree status is the public source for platform incident context.
- Browser-visible profile and destination behavior can be recorded without claiming access to Linktree internals.
- Partner logs and contracts remain private and should be summarized or redacted according to their handling rules.

## Authentication

For Admin work, use only the operator's individually provisioned Linktree account, documented Workspace role, and enabled MFA. Never request passwords, one-time codes, browser cookies, recovery codes, or session material. For partner automation, use only the authentication method, environment, scope, storage, rotation, and revocation process in the user-supplied approved partner contract. Public help pages do not establish a general API credential.

## Instructions

1. Record incident ID, reporter, symptom, first-seen time and timezone, affected profile, expected behavior, business impact, and current owner.
2. Use Read, Glob, and Grep to locate relevant change receipts, sanitized logs, fixtures, and destination ownership while excluding credentials and raw audience exports.
3. Capture Linktree service status, signed-out reproduction steps, device and browser class, link title, expected destination host, and observed redirect or error.
4. For approved partner automation, include contract revision, request correlation identifier, response class, and redacted timing only when permitted.
5. Remove tokens, cookies, email addresses, phone numbers, payment data, full query strings, private payloads, and unrelated profile information.
6. Use Write or Edit to assemble the smallest useful bundle and a manifest listing every included artifact and redaction.
7. Use WebFetch only for current official Linktree status or troubleshooting guidance.

## Approval Boundaries

Do not share browser sessions, raw HAR files, subscriber exports, private partner documents, or screenshots containing unrelated personal information.

## Output

Return incident ID, timeline, reproduction, affected surface, status evidence, change correlation, redactions, artifact manifest, escalation target, and next diagnostic action.

## Error Handling

| Condition | Response |
|---|---|
| Bundle contains a session or token | Stop distribution, remove it, rotate if exposed, and rebuild the bundle. |
| Symptom cannot be reproduced | Record that fact and preserve timestamps and reporter evidence without inventing a cause. |
| Service incident is active | Correlate impact and monitor official status before invasive changes. |

## Example

The example is a synthetic, redacted operator receipt, not proof of Linktree access or a live account change.

```text
incident=INC-42; surface=public-link; first-seen=2026-09-11T14:20Z; status=operational; repro=mobile-only; artifacts=3-redacted; escalation=destination-owner
```

## Resources

- [Official documentation map](references/official-docs.md) — dated evidence and limits for this workflow.

Read the map before acting. Recheck current account and partner-specific evidence for plan-dependent or private behavior.

## Next Steps

Revalidate source dates, owner approval, target profile, and rollback readiness before repeating the workflow in another account, Workspace, campaign, region, plan, or integration.
