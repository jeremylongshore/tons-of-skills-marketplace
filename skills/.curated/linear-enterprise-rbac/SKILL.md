---
name: linear-enterprise-rbac
description: >-
  Govern Linear workspace roles, team access, OAuth scopes, SCIM provisioning, and audit evidence. Use when designing enterprise access or reviewing identity-provider mappings. Trigger with "audit Linear access", "configure Linear SCIM", or "review Linear roles".
argument-hint: "[workspace] [roles|oauth|scim|audit]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.13.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- linear
- access-governance
model: inherit
effort: high
compatibility: Designed for Claude Code; live verification requires network access and an approved Linear workspace credential
---
# Linear Enterprise Access Governance

## Overview

Model access from the workspace's actual plan, roles, teams, OAuth actor, and identity-provider ownership instead of inventing application-side Linear roles.

## Prerequisites

- The target repository, Linear workspace, environment, and accountable owner
- Current security, privacy, compliance, capacity, and change-control requirements
- An approved Linear credential only when a bounded live verification is necessary

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect code, configuration, and evidence. Use `WebFetch` only for current first-party Linear documentation and package metadata. Use `Write` or `Edit` only for requested implementation with known target files. Never write credentials, customer content, unrestricted environment output, or unredacted GraphQL variables.

## Current Contract

- Workspace Owner exists only on Enterprise; Team Owner exists on Business and Enterprise; Free-plan users are admins.
- SCIM 2.0 is an Enterprise capability. Linear supplies the base connector URL and bearer token in security settings; do not hard-code a guessed endpoint.
- SCIM group push can map groups one-to-one to teams, and special `linear-owners`, `linear-admins`, and `linear-guests` groups control roles.
- Enterprise audit logs retain 90 days of events and are accessible only to workspace owners.

## Authentication

Use a personal API key only for owner-controlled scripts, OAuth with PKCE for user-delegated applications, or an enabled client-credentials grant for approved automation. Personal keys use `Authorization: <API_KEY>`; OAuth tokens use `Authorization: Bearer <ACCESS_TOKEN>`. Store credentials server-side in an approved secret manager.

Treat app approval, team access, scope changes, credential creation, rotation, revocation, and production access as owner-approved actions.

## Instructions

1. Confirm plan, workspace owners, admins, team owners, members, guests, private teams, and existing SCIM ownership.
2. Map each application action to the narrowest OAuth scopes and team access; do not derive authorization from UI role labels alone.
3. Review identity-provider group mappings, default public teams, guest exceptions, suspension, and break-glass ownership.
4. Test create, update, suspend, unsuspend, group removal, and disconnect behavior in a non-production identity set.
5. Configure audit queries or streaming with redaction, retention, and SIEM ownership appropriate to the signed policy.
6. Produce a least-privilege matrix and a separately approved rollout/rollback plan.

## Approval Boundaries

Do not create, reveal, rotate, or revoke credentials; authorize an OAuth app; change scopes or team access; create, mutate, archive, or delete workspace data; configure or re-enable webhooks; import or export data; change roles, SCIM, or audit streaming; transmit diagnostics; change paid entitlements; or perform another production mutation without explicit approval from the accountable owner. Keep diagnosis read-only unless implementation was requested.

## Output

Return the workspace and team scope, auth mode without credential value, files and contracts inspected, exact operation names, evidence collected, validation result, sensitive fields redacted, remaining risk, accountable owner, approval state, and rollback or next action.

## Error Handling

| Condition | Response |
|---|---|
| Plan capability unavailable | Do not emulate SCIM or audit-log guarantees; escalate the entitlement decision. |
| Conflicting SCIM groups | Resolve push order and role ownership before changing memberships. |
| Guest data exposure risk | Review connected integrations and team visibility before enabling access. |
| Break-glass path absent | Do not make the IdP authoritative until recovery ownership is tested. |

## Examples

Use a compact handoff that makes scope, mutation authority, and verification evidence reviewable.

Input:

```text
plan=enterprise; idp=okta; groups=owners,admins,guests,teams; audit=siem
```

Expected handoff:

```text
role-map=reviewed; scim-url=workspace-supplied; rollout=approval-pending
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Linear developer documentation index](https://linear.app/llms.txt)
- [Linear GraphQL API](https://linear.app/developers/graphql.md)
