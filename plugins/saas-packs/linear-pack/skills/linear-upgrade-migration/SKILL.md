---
name: linear-upgrade-migration
description: >-
  Upgrade a Linear integration across SDK releases and GraphQL deprecations with typed inventory, staged verification, and rollback. Use when package updates or schema notices require code changes. Trigger with "upgrade Linear SDK", "migrate Linear API code", or "fix Linear deprecation".
argument-hint: "[repository-path] [target-version-or-deprecation]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.13.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- linear
- upgrade
model: inherit
effort: high
compatibility: Designed for Claude Code; live verification requires network access and an approved Linear workspace credential
---
# Linear SDK and Schema Upgrade

## Overview

Derive the migration from the installed/current SDK diff and live schema instead of assuming every version change repeats the historical 1.x-to-2.x rename.

## Prerequisites

- The target repository, Linear workspace, environment, and accountable owner
- Current security, privacy, compliance, capacity, and change-control requirements
- An approved Linear credential only when a bounded live verification is necessary

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect code, configuration, and evidence. Use `WebFetch` only for current first-party Linear documentation and package metadata. Use `Write` or `Edit` only for requested implementation with known target files. Never write credentials, customer content, unrestricted environment output, or unredacted GraphQL variables.

## Current Contract

- The historical SDK 2.x migration changed mutations from model-first to verb-first names; modern upgrades must use actual release and type changes.
- Linear GraphQL has no conventional versioned API; deprecated fields use `@deprecated`, and API changes appear in the changelog with an `[API]` prefix.
- On 2026-09-11 npm reported `@linear/sdk` 95.0.0 requiring Node.js `>=18.x`; recheck before each upgrade.

## Authentication

Use a personal API key only for owner-controlled scripts, OAuth with PKCE for user-delegated applications, or an enabled client-credentials grant for approved automation. Personal keys use `Authorization: <API_KEY>`; OAuth tokens use `Authorization: Bearer <ACCESS_TOKEN>`. Store credentials server-side in an approved secret manager.

Treat app approval, team access, scope changes, credential creation, rotation, revocation, and production access as owner-approved actions.

## Instructions

1. Record current Node, SDK, lockfile, generated types, GraphQL operations, custom raw queries, and deprecated-field usage.
2. Read the target package metadata, repository changes, generated schema/type diff, and applicable Linear API changelog entries.
3. Classify compile-time renames, behavioral changes, auth/data implications, and runtime-only risks.
4. Upgrade on a bounded branch, commit the resolved lockfile, and repair adapters before business call sites.
5. Run static checks, unit/fixture tests, GraphQL contract tests, and an approved read-only workspace probe.
6. Stage rollout with package rollback instructions, monitoring thresholds, and schema reconciliation evidence.

## Approval Boundaries

Do not create, reveal, rotate, or revoke credentials; authorize an OAuth app; change scopes or team access; create, mutate, archive, or delete workspace data; configure or re-enable webhooks; import or export data; change roles, SCIM, or audit streaming; transmit diagnostics; change paid entitlements; or perform another production mutation without explicit approval from the accountable owner. Keep diagnosis read-only unless implementation was requested.

## Output

Return the workspace and team scope, auth mode without credential value, files and contracts inspected, exact operation names, evidence collected, validation result, sensitive fields redacted, remaining risk, accountable owner, approval state, and rollback or next action.

## Error Handling

| Condition | Response |
|---|---|
| No release evidence | Do not guess migration steps from the version number; inspect the package/schema diff. |
| Node incompatible | Upgrade runtime through its own approved lane or choose a supported SDK version. |
| Deprecated field still works | Schedule removal from the documented notice; do not rely on a non-functioning stub. |
| Live probe differs | Stop rollout, preserve the response contract, and update tests/adapter deliberately. |

## Examples

Use a compact handoff that makes scope, mutation authority, and verification evidence reviewable.

Input:

```text
current=resolved-lockfile; target=95.0.0; raw-queries=4; deprecations=inventory
```

Expected handoff:

```text
diff=reviewed; tests=required; rollout=staged; rollback=package-pin
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Linear developer documentation index](https://linear.app/llms.txt)
- [Linear GraphQL API](https://linear.app/developers/graphql.md)
