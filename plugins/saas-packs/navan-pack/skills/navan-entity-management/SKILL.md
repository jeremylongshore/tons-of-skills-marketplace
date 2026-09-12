---
name: navan-entity-management
description: >-
  Govern workforce, organization, and access lifecycle changes across Navan and enterprise identity sources. Use when operating HRIS, SCIM, SSO, or manual provisioning. Trigger with "manage Navan users", "Navan SCIM", or "offboard Navan traveler".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<identity-source> <tenant> <lifecycle-event>"
version: 1.9.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, navan, identity]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live or external Navan actions require network access and explicit approval"
---
# Navan Workforce and Organization Lifecycle

## Overview

Govern workforce, organization, and access lifecycle changes across Navan and enterprise identity sources. This workflow produces an auditable decision or artifact before any live action.

## Prerequisites

- Access to the selected tenant's current Navan Help Center and contracted integration documentation.
- A named business owner and data owner for the travel or expense workflow.
- A non-production evidence set with secrets and traveler data removed.

## Current Contract

Navan publicly lists HRIS integrations, HR-SFTP, Okta SCIM, SSO, OpenID Connect, SAML, and user-management integrations. Exact attributes, roles, group rules, activation states, and deprovision behavior are tenant-specific.

## Authentication

Provisioning identities are privileged and must be separate from ordinary data-read integrations. Bind one identity source as authority and document manual exceptions.

## Instructions

1. Inventory authoritative people, employment, organization, and access attributes.
2. Map identifiers and lifecycle states without using email alone as an immutable key.
3. Define joiner, mover, leave, rehire, guest, contractor, and exception behavior.
4. Stage changes and review role, policy, manager, entity, and traveler-impact deltas.
5. Apply only through the enabled integration and record acknowledgements.
6. Reconcile source authority, Navan state, downstream systems, and manual grants.

## Tool Discipline

Use Read, Glob, and Grep to inspect documentation, schemas, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Invocation alone does not authorize network access, credentials, traveler or expense data, bookings, payments, policy or identity changes, file transfers, deployments, or deletion.

## Approval Boundaries

Privileged role grants, bulk changes, authority-source changes, reactivation, manual exceptions, and destructive deprovisioning require explicit approval.

## Error Handling

- Do not delete or disable on an ambiguous identity match.
- Preserve legal and financial records while removing access.
- A provisioning success response still requires state reconciliation.

## Output

Return identity mappings, proposed changes, approvals, acknowledgements, exceptions, and reconciliation results. Identify assumptions, owners, expirations, and evidence gaps explicitly.

## Examples

- Offboard access while preserving required expense records.
- Reconcile a mover whose department changed but email did not.

## Validation

Test duplicate names, email change, rehire, manager cycle, terminated admin, manual grant, partial bulk failure, and rollback. Record expected and observed results, including fail-closed behavior.

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources and the selected tenant's in-account contract before relying on mutable endpoints, fields, entitlements, limits, or delivery behavior.
- Record tenant observations as environment-specific evidence, never universal Navan guarantees.
