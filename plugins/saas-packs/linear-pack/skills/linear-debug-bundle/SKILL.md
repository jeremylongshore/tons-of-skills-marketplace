---
name: linear-debug-bundle
description: >-
  Assemble a minimal, redacted Linear integration diagnostic bundle for internal or vendor escalation. Use when a failure needs reproducible evidence without exposing tokens or workspace content. Trigger with "collect Linear diagnostics", "build a Linear debug bundle", or "escalate Linear API issue".
argument-hint: "[repository-path] [incident-id]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.13.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- linear
- debugging
model: inherit
effort: high
compatibility: Designed for Claude Code; live verification requires network access and an approved Linear workspace credential
---
# Linear Redacted Debug Bundle

## Overview

Collect contract, version, timing, and failure metadata while excluding credentials, raw environment dumps, customer content, and unrestricted GraphQL variables.

## Prerequisites

- The target repository, Linear workspace, environment, and accountable owner
- Current security, privacy, compliance, capacity, and change-control requirements
- An approved Linear credential only when a bounded live verification is necessary

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect code, configuration, and evidence. Use `WebFetch` only for current first-party Linear documentation and package metadata. Use `Write` or `Edit` only for requested implementation with known target files. Never write credentials, customer content, unrestricted environment output, or unredacted GraphQL variables.

## Current Contract

- Useful evidence includes operation name, timestamp, status, GraphQL error code/path, SDK version, redacted rate headers, and webhook delivery ID.
- SDK errors can contain queries, variables, response data, and raw errors; each field requires redaction before sharing.
- Webhook payloads can contain issue, comment, customer, and actor data; a delivery ID is safer evidence than the full payload.

## Authentication

Use a personal API key only for owner-controlled scripts, OAuth with PKCE for user-delegated applications, or an enabled client-credentials grant for approved automation. Personal keys use `Authorization: <API_KEY>`; OAuth tokens use `Authorization: Bearer <ACCESS_TOKEN>`. Store credentials server-side in an approved secret manager.

Treat app approval, team access, scope changes, credential creation, rotation, revocation, and production access as owner-approved actions.

## Instructions

1. Define the recipient, purpose, incident window, and approved data classes before collection.
2. Record package and runtime versions, endpoint host, auth mode—not token—and the smallest failing operation name.
3. Extract only allowlisted status, error-code/path, timing, request ID, delivery ID, and rate-budget fields.
4. Redact authorization, cookies, secrets, URLs with tokens, GraphQL variables, issue text, comments, emails, and user names.
5. Review the archive manifest and sample every included file before transmission.
6. Record recipient, retention deadline, deletion owner, and the exact secure transfer channel.

## Approval Boundaries

Do not create, reveal, rotate, or revoke credentials; authorize an OAuth app; change scopes or team access; create, mutate, archive, or delete workspace data; configure or re-enable webhooks; import or export data; change roles, SCIM, or audit streaming; transmit diagnostics; change paid entitlements; or perform another production mutation without explicit approval from the accountable owner. Keep diagnosis read-only unless implementation was requested.

## Output

Return the workspace and team scope, auth mode without credential value, files and contracts inspected, exact operation names, evidence collected, validation result, sensitive fields redacted, remaining risk, accountable owner, approval state, and rollback or next action.

## Error Handling

| Condition | Response |
|---|---|
| Unrestricted env dump requested | Refuse it and collect named allowlisted variables without values. |
| Raw payload required | Use a synthetic reproduction or owner-approved minimized excerpt. |
| Secret detected | Stop, rotate if exposed, scrub the bundle, and re-review. |
| Recipient unclear | Keep the bundle local and do not transmit. |

## Examples

Use a compact handoff that makes scope, mutation authority, and verification evidence reviewable.

Input:

```text
incident=LIN-INC-42; operation=IssueLookup; status=400; content=excluded
```

Expected handoff:

```text
bundle=local; fields=allowlisted; secrets=0; transfer=approval-pending
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Linear developer documentation index](https://linear.app/llms.txt)
- [Linear GraphQL API](https://linear.app/developers/graphql.md)
