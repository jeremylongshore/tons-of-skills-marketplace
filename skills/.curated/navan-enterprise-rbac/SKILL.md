---
name: navan-enterprise-rbac
description: >-
  Map Navan account roles and integration privileges to application-owned enterprise controls. Use when designing admin, API, SFTP, SCIM, SSO, finance, or support access. Trigger with "Navan RBAC", "Navan permissions", or "review Navan access".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<tenant> <role-set> <integration-set>"
version: 1.9.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, navan, rbac]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live or external Navan actions require network access and explicit approval"
---
# Navan Enterprise Access Governance

## Overview

Map Navan account roles and integration privileges to application-owned enterprise controls. This workflow produces an auditable decision or artifact before any live action.

## Prerequisites

- Access to the selected tenant's current Navan Help Center and contracted integration documentation.
- A named business owner and data owner for the travel or expense workflow.
- A non-production evidence set with secrets and traveler data removed.

## Current Contract

Public integration listings confirm identity and user-management options, but exact Navan roles and entitlements are account-specific. Capture them from the current tenant and never invent universal role names or assignment APIs.

## Authentication

Separate human login, organization administration, provisioning, data ingestion, finance reconciliation, write-back, and support access. Bind automation identities to one purpose and tenant.

## Instructions

1. Inventory human roles, groups, integration identities, and current privileges.
2. Map each business action and data class to least-privilege access.
3. Document SSO, SCIM, HRIS, manual, and break-glass authority paths.
4. Identify toxic combinations across booking, expense, payment, approval, and export.
5. Define joiner, mover, leaver, periodic review, and emergency revocation controls.
6. Test denied paths and reconcile Navan assignments with the enterprise source of authority.

## Tool Discipline

Use Read, Glob, and Grep to inspect documentation, schemas, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Invocation alone does not authorize network access, credentials, traveler or expense data, bookings, payments, policy or identity changes, file transfers, deployments, or deletion.

## Approval Boundaries

Admin grants, provisioning changes, finance or payment privileges, break-glass use, service identities, and cross-tenant access require named approvers.

## Error Handling

- A corporate title is not proof of a Navan entitlement.
- Do not let the same automation approve and reconcile its own writes.
- Fail closed when the identity source and Navan assignment disagree.

## Output

Return a role-action-data matrix, identity sources, toxic combinations, review cadence, revocation path, and unresolved tenant facts. Identify assumptions, owners, expirations, and evidence gaps explicitly.

## Examples

- Separate expense review from ERP posting.
- Reconcile a SCIM-managed user with a manually granted admin entitlement.

## Validation

Test joiner, mover, leaver, dormant account, revoked service identity, break-glass expiry, and tenant isolation. Record expected and observed results, including fail-closed behavior.

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources and the selected tenant's in-account contract before relying on mutable endpoints, fields, entitlements, limits, or delivery behavior.
- Record tenant observations as environment-specific evidence, never universal Navan guarantees.
