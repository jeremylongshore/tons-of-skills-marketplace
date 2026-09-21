---
name: flyio-install-auth
description: >-
  Install or upgrade flyctl and establish least-privilege Fly.io authentication with expiry and rotation evidence. Use when onboarding an operator or automation identity. Trigger with: "install flyctl", "create Fly deploy token", "test Fly API auth".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[interactive-or-automation-scope]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - flyio
  - authentication
  - flyctl
  - tokens
compatibility: 'Requires a supported operator workstation or CI runner, a Fly.io account, an approved organization or app scope, and a secret manager.'
---

# Fly.io CLI and Least-Privilege Token Setup

## Overview

Separate interactive login from automation credentials. Current Fly.io guidance provides scoped deploy, organization, read-only, SSH, Machine-exec, and WireGuard token types; choose the smallest authority and lifespan that satisfies the workflow.

## Prerequisites

- Named human or workload identity and business owner
- Target organization, app, commands, environment, and expiry requirement
- Approved installation source and secret storage location

## Instructions

### Step 1: Select the identity mode

Use browser login for a human workstation. For automation, map required actions to app deploy, organization deploy, read-only, SSH, Machine-exec, or WireGuard scope.

### Step 2: Install from an official channel

Follow the provider installation method for the operating system, then record `fly version` and the provider-maintained release tag. Pin CI setup where reproducibility matters.

### Step 3: Create a scoped expiring token

Prefer `fly tokens create deploy` for one app and `fly tokens create readonly` for observation. Use organization scope only for justified multi-app operations.

### Step 4: Store and inject once

Place the token in the approved secret manager and expose it only as `FLY_API_TOKEN` or `FLY_ACCESS_TOKEN` to the intended process.

### Step 5: Validate the smallest read

Confirm effective identity and scope through a non-mutating app or Machine read. Distinguish an empty scoped listing from a failed credential.

### Step 6: Plan rotation and revocation

Record token ID, owner, scope, expiry, dependents, overlap procedure, emergency revocation, and post-rotation verification.

## Authentication

Machines API requests send `Authorization: Bearer <token>` to the public `https://api.machines.dev` endpoint outside the private network. The hidden deprecated `fly auth token` output is an all-powerful short-lived login token and must not be used as the routine CI credential.

## Tool Discipline

Use Read and Grep to inspect application configuration, deployment evidence, provider documentation, fixtures, logs, schemas, and existing tests before proposing a change. Use Write or Edit only for an approved plan, configuration, implementation, test, or redacted receipt. Do not create, deploy, scale, restart, stop, suspend, destroy, rotate, revoke, expose, or migrate live Fly.io resources without explicit operator approval.

## Output

- flyctl installation and version receipt
- Token inventory containing only identifier, owner, scope, expiry, and secret reference
- Read-only scope proof plus rotation and revocation runbook

Return the target organization, app, environment, region set, Machine or database identifiers, source-contract fingerprint, evidence, unresolved risks, rollback state, and final decision without exposing tokens, secrets, connection strings, or customer data.

## Examples

A single-app production pipeline receives a 30-day app deploy token in its protected environment. A monitoring job receives a separate organization read-only token. Both record token IDs and owners, while values remain only in the secret manager.

## Error Handling

| Failure | Response |
| --- | --- |
| Identity appears valid but listings are empty | Check scope filters and target app before broadening access; scoped tokens can hide out-of-scope resources. |
| Token is exposed | Revoke by token ID, rotate dependents, inspect access evidence, and avoid repeating the value in the incident record. |
| flyctl behavior differs from docs | Record the installed version, compare with the current provider release, and revalidate commands before use. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Machines API setup](https://fly.io/docs/machines/api/working-with-machines-api/)
- [Automation and tokens](https://fly.io/docs/flyctl/integrating/)
- [App configuration](https://fly.io/docs/reference/configuration/)
- [Access tokens](https://fly.io/docs/security/tokens/)
- [fly tokens create](https://fly.io/docs/flyctl/tokens-create/)
- [flyctl releases](https://github.com/superfly/flyctl/releases)
