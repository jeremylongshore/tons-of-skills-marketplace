---
name: ideogram-enterprise-rbac
description: >-
  Map Ideogram Owner, Admin, and Member roles to application-owned tenant, budget, key, media, publishing, and audit permissions. Use when designing or reviewing enterprise access control. Trigger with "design Ideogram RBAC", "audit Ideogram team roles", or "separate Ideogram duties".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<team> <application-roles> <environment>"
version: 1.11.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, ideogram, access-control]
model: inherit
effort: high
compatibility: "Designed for Claude Code; team and key mutations require authorized administrators"
---
# Ideogram Enterprise Access Control

## Overview

Keep Ideogram team administration distinct from application authorization. Vendor roles govern a shared team boundary, while the application must enforce tenant, use-case, spend, upload, generation, review, publication, retention, and incident permissions.

## Prerequisites

- Ideogram team inventory, role holders, keys, billing owner, environments, and emergency contacts.
- Application identity provider, tenant model, service identities, permission catalog, and audit requirements.
- Joiner, mover, leaver, key rotation, access review, and break-glass processes.

## Current Contract

Ideogram documents Owner, Admin, and Member team roles. Team members share keys, credits, and billing context; separate keys do not inherently provide per-user or per-environment vendor budgets. Avoid inventing finer Ideogram permissions that the application must actually enforce.

## Authentication

Store each server-side `IDEOGRAM_API_KEY` in the approved secret manager and send it only as `Api-Key` to `https://api.ideogram.ai`. Users authenticate to the application; only constrained service identities reach the vendor adapter.

## Instructions

1. Inventory vendor role holders, keys, credit authority, environments, application roles, service identities, and asset stores.
2. Define vendor Owner, Admin, and Member responsibilities from current first-party documentation.
3. Build an application permission matrix for request, upload, transform, train, spend, review, publish, export, delete, key administration, and incident actions.
4. Enforce tenant and environment scope at the gateway, queue, async state, webhook, storage, and publisher.
5. Separate requester, approver, publisher, billing administrator, key administrator, and auditor where risk warrants.
6. Test denied access, cross-tenant object access, wrong-environment key use, leaver removal, key rotation, and break-glass expiry.
7. Record periodic review evidence and remediate stale identities or excessive service authority.

## Tool Discipline

Use Read, Glob, and Grep for manifests, policy, identity mappings, and audit evidence. Use Write and Edit for approved policy or tests. Do not change team members, roles, keys, billing, or production identities by invocation alone.

## Approval Boundaries

Require authorized administrators for vendor membership, role, key, and billing changes. Require application and data owners for tenant permissions, publication, retention, and deletion. Break-glass access must expire and be reviewed.

## Error Handling

- Do not claim application permissions are enforced by a coarse vendor team role.
- Revoke or rotate authority after a leaver or credible key exposure, then verify every consumer.
- Deny ambiguous tenant or environment context before queueing paid work.

## Output

Return vendor-role and application-permission matrices, identities, scopes, separation-of-duty findings, tests, exceptions, owners, remediation, review date, and rollback. Exclude keys and personal or media content.

## Examples

- A Member may use the shared team context, while only an application Publisher can release an approved tenant asset.
- A billing Admin controls credit; a service identity receives only bounded generation authority through the gateway.

## Validation

Test every allow and deny edge, cross-tenant and cross-environment access, deprovisioning, rotation, audit completeness, and break-glass expiry. Confirm no role grants direct browser access to the vendor key.

## Resources

- [Current first-party evidence map](references/official-docs.md) — use the dated endpoint, webhook, billing, team, and training links as the contract index for this workflow.
- Recheck the endpoint-specific page and current OpenAPI description before relying on an enum, limit, beta feature, or lifecycle claim.
- Record live observations as environment-specific evidence, not as universal vendor guarantees.
