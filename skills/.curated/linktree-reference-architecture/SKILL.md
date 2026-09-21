---
name: linktree-reference-architecture
description: 'Define ownership and trust boundaries across Linktree Admin, public profiles, destinations, analytics exports, and private partner automation. Use when reviewing a Linktree system design. Trigger with "architect Linktree integration".'
argument-hint: "[system-name] [scope]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- linktree
- architecture
- trust-boundaries
- governance
model: inherit
effort: medium
compatibility: Designed for Claude Code; live work requires an authorized Linktree account and approval from the profile, Workspace, data, or partner-integration owner
---
# Linktree Integration Authority Architecture

## Overview

Produce a repo-grounded architecture that distinguishes Linktree-owned public behavior, account-owner decisions, destination systems, approved exports, and contract-private interfaces.

## Prerequisites

- An authorized Linktree account or a clearly bounded design-only task
- The profile, Workspace, destination, campaign, data, or integration owner appropriate to the requested change
- Current account evidence for plan-dependent features and user-supplied approved partner documentation for every private interface

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect repository specifications, sanitized fixtures, policies, tests, and prior receipts.

Use `WebFetch` only for current official Linktree documentation or explicitly approved partner documentation.

Use `Write` or `Edit` only after confirming scope, target, owners, data classification, and approval state. These tools do not confer Linktree access, account authority, or permission to process visitor data. Return exact operator steps or an approval-gated handoff when a live action is not authorized.

## Current Contract

- The public profile and Linktree Admin are documented product surfaces; destinations remain independently owned systems.
- Insights and audience exports have plan, privacy, and handling constraints.
- Partner APIs and SDKs are program-gated, so private interface details require contract evidence.

## Authentication

For Admin work, use only the operator's individually provisioned Linktree account, documented Workspace role, and enabled MFA. Never request passwords, one-time codes, browser cookies, recovery codes, or session material. For partner automation, use only the authentication method, environment, scope, storage, rotation, and revocation process in the user-supplied approved partner contract. Public help pages do not establish a general API credential.

## Instructions

1. Inventory actors, profiles, Workspaces, destinations, audience flows, analytics consumers, partner integrations, data classes, and business owners.
2. Use Read, Glob, and Grep to trace repository specifications, adapters, scheduled jobs, data stores, ownership files, and incident runbooks.
3. Label every edge as documented public UI, browser redirect, approved export, user-supplied partner contract, or unsupported assumption.
4. For each boundary, record authentication, authorization, data minimization, retention, deletion, availability, reconciliation, and rollback ownership.
5. Model signed-out visitor, editor, Workspace administrator, analytics operator, destination owner, and partner-service failure paths using synthetic identifiers.
6. Use Write or Edit to create the architecture record and an assumption register; leave unverifiable edges blocked.
7. Use WebFetch only for current official Linktree product, privacy, status, or approved partner documentation.

## Approval Boundaries

Do not collapse Linktree, destination, and customer data ownership into one trust zone or represent an unapproved partner interface as public infrastructure.

## Output

Return actors, components, trust boundaries, edge authority, data classes, failure domains, controls, assumptions, blocked edges, owners, and next review date.

## Error Handling

| Condition | Response |
|---|---|
| An edge has no authority source | Mark it unsupported and block implementation across that edge. |
| Subscriber data lacks a deletion owner | Stop the data flow until retention and deletion are assigned. |
| Destination rollback depends on Linktree alone | Add destination-owner coordination and independent recovery. |

## Example

The example is a synthetic, redacted operator receipt, not proof of Linktree access or a live account change.

```text
system=creator-growth; profiles=2; destinations=6; public-edges=8; contract-private=1; unsupported=0; personal-data=audience-export; blocked=retention-owner
```

## Resources

- [Official documentation map](references/official-docs.md) — dated evidence and limits for this workflow.

Read the map before acting. Recheck current account and partner-specific evidence for plan-dependent or private behavior.

## Next Steps

Revalidate source dates, owner approval, target profile, and rollback readiness before repeating the workflow in another account, Workspace, campaign, region, plan, or integration.
