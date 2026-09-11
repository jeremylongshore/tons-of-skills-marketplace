---
name: linear-security-basics
description: >-
  Harden Linear credentials, OAuth, team access, webhook verification, logging, and rotation. Use when threat-modeling an integration or correcting a security gap. Trigger with "secure Linear integration", "review Linear OAuth security", or "verify Linear webhooks".
argument-hint: "[repository-path] [auth|webhook|data|rotation]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.13.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- linear
- security
model: inherit
effort: high
compatibility: Designed for Claude Code; live verification requires network access and an approved Linear workspace credential
---
# Linear Integration Security Baseline

## Overview

Apply least privilege and fail-closed verification across every credential, workspace boundary, inbound event, and diagnostic path.

## Prerequisites

- The target repository, Linear workspace, environment, and accountable owner
- Current security, privacy, compliance, capacity, and change-control requirements
- An approved Linear credential only when a bounded live verification is necessary

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect code, configuration, and evidence. Use `WebFetch` only for current first-party Linear documentation and package metadata. Use `Write` or `Edit` only for requested implementation with known target files. Never write credentials, customer content, unrestricted environment output, or unredacted GraphQL variables.

## Current Contract

- Authorization-code OAuth supports PKCE; applications must use exact registered redirect URLs and validate authorization state.
- All OAuth apps moved to the refresh-token system on 2026-04-01; access and refresh tokens require secure server-side storage and revocation handling.
- Webhook authenticity is HMAC-SHA256 over the exact raw body; compare safely and use timestamp/delivery ID for replay controls.
- Client-secret rotation and webhook-signing-secret rotation are separate operations with different impacts.

## Authentication

Use a personal API key only for owner-controlled scripts, OAuth with PKCE for user-delegated applications, or an enabled client-credentials grant for approved automation. Personal keys use `Authorization: <API_KEY>`; OAuth tokens use `Authorization: Bearer <ACCESS_TOKEN>`. Store credentials server-side in an approved secret manager.

Treat app approval, team access, scope changes, credential creation, rotation, revocation, and production access as owner-approved actions.

## Instructions

1. Inventory tokens, client and signing secrets, redirect URLs, scopes, team access, caches, logs, exports, and third-party processors.
2. Select the narrowest auth actor and scopes, validate OAuth state/PKCE, and store credentials only in an approved secret manager.
3. Verify webhook raw-body HMAC before parsing or queuing; reject invalid signatures and stale/replayed deliveries.
4. Redact authorization, cookies, queries, variables, issue content, emails, actor data, and signatures from telemetry.
5. Test revocation, client-secret rotation, signing-secret rotation, compromised-token containment, and app disablement.
6. Document residual risk, accountable owners, and an independently approved remediation rollout.

## Approval Boundaries

Do not create, reveal, rotate, or revoke credentials; authorize an OAuth app; change scopes or team access; create, mutate, archive, or delete workspace data; configure or re-enable webhooks; import or export data; change roles, SCIM, or audit streaming; transmit diagnostics; change paid entitlements; or perform another production mutation without explicit approval from the accountable owner. Keep diagnosis read-only unless implementation was requested.

## Output

Return the workspace and team scope, auth mode without credential value, files and contracts inspected, exact operation names, evidence collected, validation result, sensitive fields redacted, remaining risk, accountable owner, approval state, and rollback or next action.

## Error Handling

| Condition | Response |
|---|---|
| Token exposed | Revoke or rotate the affected credential, scrub retained copies, and audit access. |
| Signature invalid | Reject before parsing business data and preserve only redacted delivery metadata. |
| OAuth state mismatch | Abort the flow; do not exchange the code. |
| Scope too broad | Reduce scopes/team access and reauthorize through the approved change path. |

## Examples

Use a compact handoff that makes scope, mutation authority, and verification evidence reviewable.

Input:

```text
auth=oauth-pkce; scopes=read,write; teams=approved-subset; raw-body=true
```

Expected handoff:

```text
threat-model=updated; secrets=server-side; replay-control=delivery-id+timestamp
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Linear developer documentation index](https://linear.app/llms.txt)
- [Linear GraphQL API](https://linear.app/developers/graphql.md)
