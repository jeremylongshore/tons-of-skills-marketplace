---
name: coderabbit-enterprise-rbac
description: >-
  Design and audit roles, seats, API access, and administrative separation for an enterprise organization. Use when this operator task needs a current, evidence-backed
  CodeRabbit workflow. Trigger with "audit CodeRabbit RBAC".
allowed-tools: Read,Glob,Grep,Write,Edit
version: 2.0.0
argument-hint: "[target] [evidence-or-scope]"
model: inherit
effort: high
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Requires current CodeRabbit documentation and approved access for any live organization, repository, billing, or API change
tags: [saas, coderabbit, enterprise, rbac, access-control]
---
# CodeRabbit Enterprise RBAC

## Overview

Use CodeRabbit native administrative roles instead of inferring all access from the Git provider. Map developer seats and administrative authority separately.

## Prerequisites

- Identify the CodeRabbit organization, Git provider, repository, plan, and accountable owner.
- Read `references/official-docs.md` and re-check any time-sensitive contract before execution.
- Use synthetic or read-only evidence until the approval boundary is satisfied.
- Preserve the repository's independent CI, security, and human-review requirements.

## Current Contract

- Built-in roles are Admin, Member, and Billing Admin.
- CodeRabbit roles are independent of Git roles after initial assignment.
- Billing Admin does not consume a seat and cannot edit role matrices.
- Enterprise custom roles expose granular permissions.

## Authentication

Treat Git-provider sessions, CodeRabbit web sessions, CLI credentials, and CodeRabbit API keys as separate credentials. Use only an already-approved session or secret-manager reference, never print a secret, and do not place credentials in `.coderabbit.yaml`, source files, logs, or deliverables.

## Instructions

1. Inventory users, provider roles, CodeRabbit roles, seats, keys, and repo access.

2. Map job functions to least privilege across settings, billing, reports, API, and logs.

3. Find toxic combinations, stale admins, unused seats, and unmanaged keys.

4. Draft changes with partial-success handling, rollback, and recertification.

## Tool Discipline

- Use **Glob** to locate candidate configuration and evidence files without widening scope.
- Use **Grep** to find relevant fields, commands, identifiers, and stale claims.
- Use **Read** to inspect the smallest required files and authoritative evidence.
- Use **Write** only for a new approved local draft or evidence artifact.
- Use **Edit** only for a bounded approved change whose rollback is known.
- Do not use these file tools as a substitute for authenticated CodeRabbit or provider operations.

## Approval Boundaries

Require an authorized CodeRabbit Admin and security owner before role, seat, default-role, or key changes. Keep analysis and drafts local until approval is explicit, and record who approved the action and its scope.

## Output

An access matrix, least-privilege target, exceptions, approved change set, and recertification schedule. Include source dates, unknowns, and the exact boundary between observed fact and recommendation.

## Error Handling

| Condition | Response |
|---|---|
| Current contract is unclear or docs disagree | Stop mutation, cite both sources, and request owner resolution. |
| Required access or approval is missing | Produce a draft and evidence plan only. |
| Validation or pilot behavior differs from expectation | Restore the prior state and retain the failed evidence. |
| Output contains secrets or private code | Stop, quarantine the artifact, redact it, and notify the data owner. |

## Examples

### Example 1

Separate billing duties using Billing Admin.

### Example 2

Create an Enterprise read-only audit custom role.

## Validation

- Confirm every claim against the dated sources in `references/official-docs.md`.
- Verify the requested scope, owner, approval, happy path, failure path, and rollback.
- Re-read the effective configuration or provider state after any approved change.
- Report unsupported fields, undocumented endpoints, and unverified assumptions as failures.

## Resources

- [Official documentation and contract notes](references/official-docs.md)
- Re-check the dated contract before any live operation.
- Treat unresolved or changed vendor behavior as a stop condition.
