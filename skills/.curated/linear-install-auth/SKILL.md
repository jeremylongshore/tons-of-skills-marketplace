---
name: linear-install-auth
description: >-
  Install the current Linear TypeScript SDK and configure personal-key, OAuth, or app-actor authentication safely. Use when connecting a repository or correcting an auth setup. Trigger with "install Linear SDK", "configure Linear OAuth", or "set up Linear API auth".
argument-hint: "[repository-path] [personal-key|oauth|client-credentials]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.13.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- linear
- authentication
model: inherit
effort: high
compatibility: Designed for Claude Code; live verification requires network access and an approved Linear workspace credential
---
# Linear SDK Installation and Authentication

## Overview

Choose authentication from the operating model, pin the SDK through the repository's lockfile, and prove access with a bounded read-only query.

## Prerequisites

- The target repository, Linear workspace, environment, and accountable owner
- Current security, privacy, compliance, capacity, and change-control requirements
- An approved Linear credential only when a bounded live verification is necessary

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect code, configuration, and evidence. Use `WebFetch` only for current first-party Linear documentation and package metadata. Use `Write` or `Edit` only for requested implementation with known target files. Never write credentials, customer content, unrestricted environment output, or unredacted GraphQL variables.

## Current Contract

- The official package is `@linear/sdk`; npm reported 95.0.0 with Node.js `>=18.x` on 2026-09-11.
- Personal keys use a raw `Authorization` value; OAuth tokens use the Bearer scheme. The SDK represents these as `apiKey` and `accessToken`.
- OAuth is recommended for applications used by other people; scheduled automation should use the client-credentials grant when enabled.

## Authentication

Use a personal API key only for owner-controlled scripts, OAuth with PKCE for user-delegated applications, or an enabled client-credentials grant for approved automation. Personal keys use `Authorization: <API_KEY>`; OAuth tokens use `Authorization: Bearer <ACCESS_TOKEN>`. Store credentials server-side in an approved secret manager.

Treat app approval, team access, scope changes, credential creation, rotation, revocation, and production access as owner-approved actions.

## Instructions

1. Inspect runtime, Node version, manifest, lockfile, existing client construction, and secret provider.
2. Choose personal key for an owner-controlled integration, authorization-code OAuth for user-delegated access, or client credentials for approved unattended automation.
3. Pin a compatible SDK range and commit the resolved lockfile; do not silently take an unbounded latest version in CI.
4. Inject credentials from the approved server-side secret manager and document the variable name without its value.
5. Run a read-only viewer/team proof and check both transport status and GraphQL errors.
6. Assign owners for scope review, app approval, rotation, revocation, and emergency disablement.

## Approval Boundaries

Do not create, reveal, rotate, or revoke credentials; authorize an OAuth app; change scopes or team access; create, mutate, archive, or delete workspace data; configure or re-enable webhooks; import or export data; change roles, SCIM, or audit streaming; transmit diagnostics; change paid entitlements; or perform another production mutation without explicit approval from the accountable owner. Keep diagnosis read-only unless implementation was requested.

## Output

Return the workspace and team scope, auth mode without credential value, files and contracts inspected, exact operation names, evidence collected, validation result, sensitive fields redacted, remaining risk, accountable owner, approval state, and rollback or next action.

## Error Handling

| Condition | Response |
|---|---|
| Node below 18 | Upgrade through the repository's runtime policy before installing the current SDK. |
| 401 | Check token type, header form, injection, and revocation state without exposing it. |
| OAuth redirect mismatch | Use an exactly registered callback; do not add a wildcard. |
| Secret committed | Revoke or rotate it, remove retained copies, and audit access. |

## Examples

Use a compact handoff that makes scope, mutation authority, and verification evidence reviewable.

Input:

```text
runtime=node20; auth=oauth; secret=approved-reference; probe=viewer
```

Expected handoff:

```text
sdk=resolved-lockfile; auth=bearer; probe=read-only; secret=redacted
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Linear developer documentation index](https://linear.app/llms.txt)
- [Linear GraphQL API](https://linear.app/developers/graphql.md)
