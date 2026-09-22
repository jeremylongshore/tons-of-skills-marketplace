---
name: ramp-enterprise-rbac
description: >-
  Audit effective Ramp integration authority across OAuth grants, scopes, user roles, business entities, app restrictions, and spend approvals. Use when onboarding an enterprise tenant or investigating excess access. Trigger with "Ramp RBAC audit" or "Ramp least privilege".
allowed-tools: Read,Glob,Grep,Write,Edit
version: 2.0.0
argument-hint: "[integration-or-environment]"
model: inherit
effort: high
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Requires current Ramp Developer API documentation and approved access for any live financial, card, identity, accounting, application, or configuration change
tags: [saas, ramp, rbac, least-privilege, enterprise]
---
# Ramp Enterprise Authority and Scope Review

## Overview

Ramp API authority is layered. Build an effective-access matrix rather than treating an OAuth scope as the whole permission decision, and verify both allowed and denied operations per business entity.

## Prerequisites

- Identify the Ramp application, environment, business entities, affected data and workflows, accountable owner, and rollback boundary.
- Read `references/official-docs.md` and re-check endpoint schemas, scopes, limits, and support status before a live operation.
- Use synthetic fixtures or Ramp sandbox until production access and business effects are explicitly approved.
- Prepare approved secret storage and a sanitized evidence location.

## Current Contract

- Client Credentials represents an internal backend acting with application authority; Authorization Code represents an authorizing user and is required for third-party multi-tenant apps.
- Tokens are scope-bound and environment-bound, and scopes cannot be expanded after issuance.
- Only appropriately privileged users, typically Admin or Business Owner, can authorize Developer API applications.
- Resource behavior also depends on business entity, user role, object ownership, spend controls, and endpoint-specific permissions.

## Instructions

1. Inventory applications, environments, grant types, redirect URIs, client owners, scopes, authorizing or service principals, entities, subscriptions, and credential rotation.

2. Map each business operation to exact endpoint, HTTP verb, scope, entity, role, spend approval, data class, and accountable owner.

3. Remove unused scopes and stale clients, then issue new tokens because existing tokens do not acquire changed scopes.

4. Run positive tests for intended reads/writes and negative tests across an ungranted endpoint, entity, role, and environment using sandbox or approved production reads.

5. Schedule recertification and immediate review on owner departure, role change, integration expansion, credential incident, or new entity onboarding.

## Tool Discipline

- Use **Glob** to locate candidate code, manifests, fixtures, and evidence without widening scope.
- Use **Grep** to find relevant endpoints, fields, permissions, identifiers, errors, and stale assumptions.
- Use **Read** to inspect the smallest required local files and authoritative evidence.
- Use **Write** only for a new approved local draft, test, configuration, or evidence artifact.
- Use **Edit** only for a bounded approved change with a known rollback.
- Local file tools do not authorize a Ramp operation or replace owner approval.

## Approval Boundaries

Business owners approve application authorization; security approves grants and secrets; finance/data owners approve entity and spend/data authority. No audit step grants itself more access.

## Output

An effective-access matrix, client and token inventory, scope deltas, positive/negative test receipts, exceptions with expiry, and recertification ownership.

## Error Handling

| Condition | Response |
|---|---|
| A 403 remains after adding a scope | Check token reissuance, grant type, authorizing user, entity, role, and endpoint authority before broadening access again. |
| One client serves unrelated workflows | Split clients by trust boundary and lifecycle so scopes and rotation can be independently governed. |
| An owner leaves | Reassign ownership, revoke or rotate affected credentials, and repeat negative tests. |

## Examples

### Example 1

Prove an accounting client can read one entity's sync-ready objects but cannot manage cards or access a second entity.

### Example 2

Replace a broad shared client with separate read-only analytics and controlled accounting-write applications.

## Validation

- Every scope and effective permission maps to a current business operation and owner.
- New tokens are issued after scope changes and old credentials are revoked.
- Negative tests cover endpoints, entities, roles, and environments.
- Exceptions have compensating controls, approvers, and expiration.

## Resources

- [Official documentation and contract notes](references/official-docs.md)
- Re-check the dated contract and current OpenAPI schema before any live request.
- Treat unresolved vendor behavior, authority, or financial state as a stop condition.
