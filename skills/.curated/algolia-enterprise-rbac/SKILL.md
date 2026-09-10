---
name: algolia-enterprise-rbac
description: >-
  Map workforce roles and application actors to Algolia team permissions, API-key ACLs, and secured-key restrictions. Use when reviewing least privilege, tenancy, SSO requirements, or access rotation. Trigger with "Algolia RBAC", "Algolia SSO", or "Algolia tenant access".
argument-hint: "[repository-path] [application-or-role]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.7.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- algolia
- access-control
model: inherit
effort: medium
compatibility: Designed for Claude Code
---
# Algolia Enterprise Access Design

## Overview

This skill separates human dashboard access, backend service access, browser search access, and tenant-scoped access. It verifies current account capabilities instead of assuming every plan exposes the same roles or SSO features.

## Prerequisites

- A named repository, environment, and Algolia application or index in scope
- The local lockfile and installed client types as implementation authority
- A safe read-only query or explicitly disposable test target
- Current first-party documentation for any provider behavior that affects the change

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect local code, configuration names, tests, and dependency versions. Use `WebFetch` only for current official Algolia documentation. Use `Write` or `Edit` only after identifying the target files, constraints, and verification plan.

## Current Contract

- Treat current dashboard settings and contracted features as the authority for workforce roles and SSO availability.
- Map service operations to documented API-key ACLs and index restrictions.
- Generate secured search keys only on a trusted backend and require at least one restriction.
- Model application tenancy in filters and key restrictions; do not confuse that model with provider workforce RBAC.

## Authentication

Review key descriptions, ACLs, restrictions, owners, and rotation dates without exporting secret values. Production services should use organization-owned, least-privilege keys.

## Instructions

1. Inventory human roles, service identities, browser clients, environments, indices, and tenant boundaries.
2. Capture current provider roles and SSO features from the account or contract, marking unavailable evidence.
3. Map each actor to operations, ACLs, index restrictions, validity, and credential owner.
4. Test denied and allowed operations using safe targets and redacted evidence.
5. Document joiner, mover, leaver, key rotation, break-glass, and audit-review procedures.
6. Identify excessive grants, orphaned credentials, or tenant escape paths and propose bounded remediation.

## Approval Boundaries

Do not enable SSO, change team roles, revoke keys, or alter tenant filters without owner approval and a tested recovery path.

## Output

Return the actor matrix, role and ACL mapping, current-plan evidence, denied-path tests, lifecycle controls, findings, and remediation approvals.

## Error Handling

| Condition | Response |
|---|---|
| Feature absent from current account | Record it as unavailable; do not infer entitlement. |
| Actor requires broad ACL | Split duties or document the exceptional grant. |
| Secured key has no restriction | Reject generation. |
| Role change risks lockout | Prepare and test break-glass access first. |

## Examples

Use this compact input and expected handoff to calibrate scope and evidence quality.

Input:

```text
actor=catalog-indexer; operations=save,settings; indices=products_*
```

Expected handoff:

```text
key=custom; ACL=minimum-reviewed; tenant-browser=secured-key; sso=contract-verified
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [API keys](https://www.algolia.com/doc/guides/security/api-keys)
- [Secured API keys](https://www.algolia.com/doc/guides/building-search-ui/going-further/api-keys-security/react)
- [Algolia security](https://www.algolia.com/security)
