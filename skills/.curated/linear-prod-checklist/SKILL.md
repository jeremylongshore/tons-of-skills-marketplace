---
name: linear-prod-checklist
description: >-
  Analyze a Linear integration for production across auth, data, quotas, webhooks, recovery, and ownership. Use when preparing a launch, material permission change, or production migration. Trigger with "review Linear readiness", "launch Linear integration", or "Linear production checklist".
argument-hint: "[repository-path] [environment]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.13.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- linear
- production-readiness
model: inherit
effort: high
compatibility: Designed for Claude Code; live verification requires network access and an approved Linear workspace credential
---
# Linear Production Readiness Gate

## Overview

Produce an evidence-backed go, conditional-go, or no-go decision instead of a box-checking document detached from the deployed system.

## Prerequisites

- The target repository, Linear workspace, environment, and accountable owner
- Current security, privacy, compliance, capacity, and change-control requirements
- An approved Linear credential only when a bounded live verification is necessary

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect code, configuration, and evidence. Use `WebFetch` only for current first-party Linear documentation and package metadata. Use `Write` or `Edit` only for requested implementation with known target files. Never write credentials, customer content, unrestricted environment output, or unredacted GraphQL variables.

## Current Contract

- OAuth is recommended for apps used by others, and app/team authorization, refresh behavior, and secret rotation must be tested.
- Webhook receivers require public HTTPS, raw-body signature verification, a 200 response within five seconds, deduplication, and reconciliation.
- Request and complexity limits vary by auth mode and can include lower endpoint-specific windows.

## Authentication

Use a personal API key only for owner-controlled scripts, OAuth with PKCE for user-delegated applications, or an enabled client-credentials grant for approved automation. Personal keys use `Authorization: <API_KEY>`; OAuth tokens use `Authorization: Bearer <ACCESS_TOKEN>`. Store credentials server-side in an approved secret manager.

Treat app approval, team access, scope changes, credential creation, rotation, revocation, and production access as owner-approved actions.

## Instructions

1. Identify the exact artifact, commit, environment, workspace/team scope, data classes, owner, and rollback authority.
2. Verify SDK/runtime compatibility, token type, exact scopes, secret storage, rotation, revocation, and access review.
3. Run offline tests plus approved read-only auth, error, rate-header, pagination, and webhook-signature probes.
4. Review data minimization, export/retention, observability redaction, idempotency, queue behavior, and missed-event reconciliation.
5. Exercise dependency outage, token failure, throttling, duplicate webhook, rollback, and disablement paths.
6. Record blockers, evidence, accountable approvers, decision, expiry, and post-launch checks.

## Approval Boundaries

Do not create, reveal, rotate, or revoke credentials; authorize an OAuth app; change scopes or team access; create, mutate, archive, or delete workspace data; configure or re-enable webhooks; import or export data; change roles, SCIM, or audit streaming; transmit diagnostics; change paid entitlements; or perform another production mutation without explicit approval from the accountable owner. Keep diagnosis read-only unless implementation was requested.

## Output

Return the workspace and team scope, auth mode without credential value, files and contracts inspected, exact operation names, evidence collected, validation result, sensitive fields redacted, remaining risk, accountable owner, approval state, and rollback or next action.

## Error Handling

| Condition | Response |
|---|---|
| Evidence missing | Mark the gate incomplete; do not infer readiness from configuration. |
| Rollback untested | Return no-go for a material mutation path. |
| Shared quota unowned | Assign a workspace budget owner before launch. |
| Sensitive logs | Block launch until redaction and retained-data cleanup are verified. |

## Examples

Use a compact handoff that makes scope, mutation authority, and verification evidence reviewable.

Input:

```text
artifact=commit-sha; env=production; scope=two-teams; rollback=tested
```

Expected handoff:

```text
decision=conditional-go; blockers=listed; approvers=required
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Linear developer documentation index](https://linear.app/llms.txt)
- [Linear GraphQL API](https://linear.app/developers/graphql.md)
