---
name: clickup-data-handling
description: >-
  Analyze, map, minimize, redact, retain, export, and delete ClickUp-derived work data under an application-owned governance policy. Use when ClickUp tasks, comments, attachments, or member data enter another system. Trigger with "ClickUp data handling", "ClickUp PII", or "ClickUp retention".
argument-hint: "[data-flow-or-repository] [assessment|remediation]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- clickup
- data-governance
model: inherit
effort: high
compatibility: Designed for Claude Code; legal retention and data-subject decisions require authorized owners
---
# ClickUp Work-Data Governance

## Overview

Treat ClickUp content as potentially sensitive and keep compliance obligations separate from unsupported API assumptions.

## Prerequisites

- A data-flow inventory covering tasks, descriptions, comments, attachments, members, webhooks, logs, and backups
- Authorized legal/security retention, deletion, residency, and access rules
- A scoped credential plus test fixtures that contain no real personal or confidential data

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect the repository, adapters, configuration names, tests, and evidence. Use `WebFetch` only for current official ClickUp documentation. Use `Write` or `Edit` after confirming the target file, Workspace boundary, and requested mode.

## Current Contract

- API responses reflect what the authenticated user can access; access is not proof that downstream storage is permitted.
- Webhook payloads can include user and before/after data and must be classified before persistence.
- Do not invent a universal ClickUp GDPR export/delete endpoint; map each application copy and authorized API action.
- Evidence can retain counts, hashes, classifications, and deletion receipts without retaining work content.

## Authentication

Use a personal token only for accountable individual/testing work or OAuth Authorization Code for a user-facing integration. Inject the token server-side through a governed secret reference, send it in `Authorization`, verify authorized Workspace IDs, and never print the token, OAuth client secret, or webhook secret.

## Instructions

1. Trace every ClickUp field from collection through processing, storage, logs, analytics, backups, and deletion.
2. Classify direct identifiers, free text, attachments, secrets, regulated content, and business metadata.
3. Minimize fields and scopes, redact telemetry, encrypt approved storage, and set retention by class.
4. Define subject/access/deletion workflows across ClickUp and each downstream copy with legal ownership.
5. Test export and deletion on synthetic records, including backups, queues, and failed jobs.
6. Produce a gap register and implement only owner-approved remediation.

## Approval Boundaries

Do not export, bulk delete, alter retention, scan private content, or claim legal compliance without the data owner and applicable legal/security approval.

## Output

Return the data map, field classifications, auth boundary, retention/deletion controls, test receipts, gaps, and accountable owners.

## Error Handling

| Condition | Response |
|---|---|
| Data owner or lawful basis is unknown | Stop collection or expansion and escalate. |
| Logs contain task text or tokens | Quarantine artifacts, rotate exposed secrets, and remediate logging. |
| Deletion cannot reach a downstream copy | Record the exception and block a false completion claim. |
| API access exceeds purpose | Reduce scope and revoke unnecessary copies. |

## Examples

The example below is a redacted operator receipt; it contains no task text, member data, credential, or webhook secret.

```text
flows=9; sensitive-fields=6; logs-redacted=yes; retention-mapped=8/9; deletion-test=partial; compliance-claim=no
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Authentication and access model](https://developer.clickup.com/docs/authentication)
- [Authentication](https://developer.clickup.com/docs/authentication)
- [Rate limits](https://developer.clickup.com/docs/rate-limits)
