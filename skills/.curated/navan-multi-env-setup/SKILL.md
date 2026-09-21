---
name: navan-multi-env-setup
description: >-
  Separate Navan development, test, staging, and production identities, data, and destinations. Use when configuring multiple environments or tenants. Trigger with "Navan environments", "separate Navan tenants", or "Navan staging setup".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<tenant-set> <environment-set> <promotion-policy>"
version: 1.9.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, navan, environments]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live or external Navan actions require network access and explicit approval"
---
# Navan Tenant and Environment Isolation

## Overview

Separate Navan development, test, staging, and production identities, data, and destinations. This workflow produces an auditable decision or artifact before any live action.

## Prerequisites

- Access to the selected tenant's current Navan Help Center and contracted integration documentation.
- A named business owner and data owner for the travel or expense workflow.
- A non-production evidence set with secrets and traveler data removed.

## Current Contract

Not every Navan customer has equivalent sandbox, API, file, or identity surfaces. Record the real environment model from the account, then simulate absent capabilities locally instead of relabeling production as test.

## Authentication

Give each available environment and tenant distinct credentials, secret paths, host allowlists, destinations, schedules, and revocation owners. Never select production by default.

## Instructions

1. Inventory real tenants and vendor-provided environments.
2. Map each integration surface, identity, destination, and data class.
3. Create fail-closed configuration with explicit tenant and environment labels.
4. Use synthetic fixtures where a vendor sandbox is unavailable.
5. Define promotion evidence without copying secrets or personal data.
6. Test cross-tenant denial, revocation, rollback, and configuration drift.

## Tool Discipline

Use Read, Glob, and Grep to inspect documentation, schemas, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Invocation alone does not authorize network access, credentials, traveler or expense data, bookings, payments, policy or identity changes, file transfers, deployments, or deletion.

## Approval Boundaries

Creating credentials, enabling a surface, copying data, adding destinations, changing schedules, or promoting to production requires explicit approval.

## Error Handling

- A URL suffix is not sufficient environment isolation.
- Never use production traveler data as a test fixture.
- Reject missing or contradictory tenant labels before network access.

## Output

Return the environment matrix, configuration contract, secret ownership, data policy, promotion gates, and drift checks. Identify assumptions, owners, expirations, and evidence gaps explicitly.

## Examples

- Use fixtures when Booking API has no sandbox entitlement.
- Block a staging worker configured with a production destination.

## Validation

Prove no credential, host, destination, schedule, or artifact crosses the tenant/environment matrix. Record expected and observed results, including fail-closed behavior.

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources and the selected tenant's in-account contract before relying on mutable endpoints, fields, entitlements, limits, or delivery behavior.
- Record tenant observations as environment-specific evidence, never universal Navan guarantees.
