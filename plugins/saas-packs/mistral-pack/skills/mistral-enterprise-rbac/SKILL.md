---
name: mistral-enterprise-rbac
description: >-
  Design Mistral organization, workspace, role, service-account, workload-identity, and application RBAC boundaries. Use when governing enterprise access. Trigger with "Mistral RBAC", "manage Mistral workspaces", or "audit Mistral service access".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<organization> <workspace-model> <identity-source>"
version: 1.14.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, mistral, rbac]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live or external Mistral actions require network access and explicit approval"
---
# Mistral Enterprise Access Governance

## Overview

Separate provider administration from application authorization. Provider controls govern resources/capacity; the application still enforces users, tenants, data, and tools.

## Prerequisites

- An identity source, joiner/mover/leaver process, and access owner.
- Organization/workspace inventory, role catalog, service identities, and break-glass policy.
- Current roles, service-account, workload-identity, and audit evidence.

## Current Contract

Mistral documents workspaces, groups, roles, service accounts, workload identity, keys, and audit logs. Exact entitlements and plan access come from current admin evidence.

## Authentication

Prefer approved non-human service identities. API keys authenticate provider calls but never substitute for application user identity or tenant authorization.

## Instructions

1. Inventory users, groups, roles, service accounts, workload identities, keys, and membership.
2. Map least-privilege provider permissions and separate billing, security, and runtime duties.
3. Define app roles/tenant checks separately for prompts, files, retrieval, tools, and output.
4. Set provisioning, review, expiration, rotation, revocation, and break-glass controls.
5. Verify audit coverage for critical admin actions and evidence retention.
6. Test joiner, mover, leaver, compromised service, wrong workspace, and emergency access.

## Tool Discipline

Use Read, Glob, and Grep to inspect code, locks, configuration, tests, and evidence. Use Write and Edit only for approved repository changes. Invocation alone does not authorize network calls, paid usage, uploads, stateful resources, admin mutations, deployments, or deletion.

## Approval Boundaries

Any user, group, role, workspace, service account, workload identity, key, or break-glass mutation requires authorized administration.

## Error Handling

- Broad workspace roles expose resources even when UI hides them.
- Shared human keys defeat attribution/offboarding.
- Provider RBAC cannot protect an app tool that skips app authorization.

## Output

Return identity/workspace matrix, provider/app role separation, lifecycle controls, audit coverage, toxic combinations, approvals, and rollback.

## Examples

- Give runtime only needed provider access while app enforces tenant retrieval.
- Offboard a user and verify service credentials remain independently owned.

## Validation

Review effective permissions, test cross-workspace and cross-tenant denial, rotate and revoke a test identity, and verify audit and break-glass expiry. Record every expected denial.

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources before relying on mutable endpoints, models, limits, prices, preview status, or retention.
- Record live account observations as environment-specific evidence, not universal Mistral guarantees.
