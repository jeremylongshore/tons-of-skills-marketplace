---
name: vastai-enterprise-rbac
description: >-
  Design and verify native Vast.ai Teams roles plus scoped API keys for least-privilege renter operations. Use when onboarding members, separating duties, or constraining automation. Trigger with: "configure Vast.ai RBAC", "create a Vast.ai team role", "scope a Vast.ai API key".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[team-actors-resources-and-required-actions]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - vastai
  - rbac
  - teams
  - governance
compatibility: 'Requires a Vast.ai Team, team administration authority, an actor/action inventory, and an independent access reviewer.'
---

# Native Vast.ai Team and Key Governance

## Overview

Use the platform's Teams and permission-category model instead of inventing an application-only proxy. Separate human roles from automation keys, constrain high-risk endpoints when possible, and prove both required access and expected denial.

## Prerequisites

- Team owner and inventory of members, services, resources, and environments
- Actor-by-action matrix for instance, user, billing, machine, miscellaneous, and team categories
- Joiner, mover, leaver, emergency-access, and periodic-review procedures

## Instructions

### Step 1: Model responsibilities

Map each actor to read and write operations. Keep billing-write, team-write, machine-write, and instance destruction separate unless a documented duty requires them.

### Step 2: Choose default or custom roles

Use Owner, Manager, or Member only when the preset matches. Otherwise create a named custom role from the minimum documented permission categories.

### Step 3: Constrain automation keys

Create a different named key per service and environment. Use endpoint and ID constraints where the API supports `eq`, `gte`, or `lte`.

### Step 4: Test both directions

For every role or key, run one required action and one prohibited action. A role is not accepted until the denial is observed.

### Step 5: Operate membership lifecycle

Assign roles during invitation, review movers before expanding access, remove departed members, revoke stale keys, and record effective context.

### Step 6: Review and recover

Export members, roles, keys, and audit evidence on schedule; time-bound emergency elevation and verify removal afterward.

## Authentication

Team roles govern member actions; scoped API keys govern programmatic access. Do not share personal full-access keys, and never give monitoring or cost-analysis jobs write authority by convenience.

## Tool Discipline

Use Read and Grep to inspect manifests, configuration, provider output, and existing tests before proposing a mutation. Use Write or Edit only for the approved plan, implementation, test, or redacted receipt; do not create, update, destroy, or fund Vast.ai resources without explicit operator approval.

## Output

- Actor/action matrix and role/key design
- Positive and negative access-test evidence
- Membership, key, review, and emergency-access receipt

Return team context, role/key IDs, permission categories and constraints, tests, exceptions, reviewer, and next review date.

## Examples

A deployment service gets `misc`, `user_read`, `instance_read`, and `instance_write`; a monitoring key gets only read categories; neither receives billing-write or team-write, and prohibited credit transfer is tested.

## Error Handling

| Failure | Response |
| --- | --- |
| Required action is denied | Add only the missing documented permission and rerun the denial suite. |
| Prohibited action succeeds | Remove excess access immediately and review audit logs. |
| Member context is ambiguous | Stop mutation and confirm personal versus team context. |
| Emergency elevation outlives its window | Revoke it, verify denial, and open a governance incident. |

## Resources

- [First-party source notes](references/official-docs.md)
- [CLI permissions](https://docs.vast.ai/cli/permissions)
- [API permissions](https://docs.vast.ai/api-reference/permissions)
- [Teams roles](https://docs.vast.ai/guides/teams/teams-roles)
