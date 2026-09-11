---
name: linear-multi-env-setup
description: >-
  Analyze and enforce separate Linear development, staging, and production credentials, apps, webhooks, data, and rollout controls. Use when one integration runs across multiple environments. Trigger with "separate Linear environments", "stage Linear OAuth app", or "isolate Linear webhooks".
argument-hint: "[repository-path] [dev|staging|production]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.13.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- linear
- environment-isolation
model: inherit
effort: high
compatibility: Designed for Claude Code; live verification requires network access and an approved Linear workspace credential
---
# Linear Multi-Environment Isolation

## Overview

Make environment boundaries explicit so a local test cannot consume production credentials, events, or team data.

## Prerequisites

- The target repository, Linear workspace, environment, and accountable owner
- Current security, privacy, compliance, capacity, and change-control requirements
- An approved Linear credential only when a bounded live verification is necessary

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect code, configuration, and evidence. Use `WebFetch` only for current first-party Linear documentation and package metadata. Use `Write` or `Edit` only for requested implementation with known target files. Never write credentials, customer content, unrestricted environment output, or unredacted GraphQL variables.

## Current Contract

- OAuth callback URLs are registered on an application, and OAuth webhook settings create a workspace-specific webhook when that app is authorized.
- Webhook signing secrets and OAuth client secrets rotate independently and take effect immediately for their respective uses.
- Client credentials must be enabled per OAuth app and app-team access can be changed from the app details page.

## Authentication

Use a personal API key only for owner-controlled scripts, OAuth with PKCE for user-delegated applications, or an enabled client-credentials grant for approved automation. Personal keys use `Authorization: <API_KEY>`; OAuth tokens use `Authorization: Bearer <ACCESS_TOKEN>`. Store credentials server-side in an approved secret manager.

Treat app approval, team access, scope changes, credential creation, rotation, revocation, and production access as owner-approved actions.

## Instructions

1. Inventory every environment's workspace, OAuth app, callback URL, webhook URL, signing secret, client secret, team access, and data class.
2. Use separate app registrations and secret references where blast radius or callback ownership differs.
3. Validate exact callback allowlists, public HTTPS endpoints, environment labels, and least-privilege team access.
4. Prevent local and pull-request jobs from resolving production secret names or mutation endpoints.
5. Promote configuration through reviewed manifests while rotating or revoking credentials as separate approved operations.
6. Test misrouting, stale-secret, rollback, and environment-disable scenarios before production rollout.

## Approval Boundaries

Do not create, reveal, rotate, or revoke credentials; authorize an OAuth app; change scopes or team access; create, mutate, archive, or delete workspace data; configure or re-enable webhooks; import or export data; change roles, SCIM, or audit streaming; transmit diagnostics; change paid entitlements; or perform another production mutation without explicit approval from the accountable owner. Keep diagnosis read-only unless implementation was requested.

## Output

Return the workspace and team scope, auth mode without credential value, files and contracts inspected, exact operation names, evidence collected, validation result, sensitive fields redacted, remaining risk, accountable owner, approval state, and rollback or next action.

## Error Handling

| Condition | Response |
|---|---|
| Environment shares production secret | Stop rollout and create an independently owned credential boundary. |
| Webhook routed to wrong environment | Disable processing, preserve delivery IDs, and reconcile after correcting routing. |
| Callback mismatch | Register the exact environment callback; never use a broad wildcard. |
| Config promoted without app access | Fail readiness and correct team/app authorization before deploy. |

## Examples

Use a compact handoff that makes scope, mutation authority, and verification evidence reviewable.

Input:

```text
env=staging; workspace=test; oauth-app=staging; webhook=https-approved
```

Expected handoff:

```text
credential-boundary=separate; callback=exact; prod-access=none
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Linear developer documentation index](https://linear.app/llms.txt)
- [Linear GraphQL API](https://linear.app/developers/graphql.md)
