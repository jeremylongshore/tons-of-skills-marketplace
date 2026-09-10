---
name: miro-enterprise-rbac
description: "Audit organization, team, board, role, and Enterprise-scope access with plan-aware evidence. Use when reviewing Miro enterprise governance. Trigger with \"miro enterprise access governance\"."
argument-hint: "[organization-scope] [review-mode]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.9.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- miro
- enterprise
- rbac
model: inherit
effort: high
compatibility: Designed for Claude Code; live work requires an authorized Miro app and redacted evidence
---
# Miro Enterprise Access Governance

## Overview

Compare intended access with effective plan, app-scope, role, team, and board controls; use the evidence produced here to make the next decision explicit and reviewable.

## Prerequisites

- Approved Miro application, tenant, and board scope
- Current repository and deployment evidence
- Named owner, success criteria, and rollback or recovery boundary

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect the repository, configuration names, adapters, tests, and evidence. Use `WebFetch` only for current official Miro documentation. Use `Write` or `Edit` after confirming the requested mode, target environment, tenant, board, and approval boundary.

## Current Contract

- Enterprise scopes have distinct plan and role availability.
- v2 team endpoints are Enterprise-only and require an Enterprise-team installation.
- App scopes and user/admin roles jointly constrain access.
- Board movement permissions vary by plan and role.

## Authentication

For REST work, use OAuth 2.0 Authorization Code with the narrowest Miro scopes. Bind each encrypted token record to its user, application, authorized team, and granted scopes. Never print access tokens, refresh tokens, client secrets, authorization codes, or board content.

## Instructions

1. Define organizations, teams, boards, apps, identities, roles, and policy in scope.
2. Verify plan and scopes before Enterprise queries.
3. Collect minimum membership/settings evidence with pseudonymized people.
4. Classify excessive, missing, orphaned, conflicting, and unknown access.
5. Prepare but do not apply changes during audit mode.
6. After approved changes, re-read effective access and retain attestation evidence.

## Approval Boundaries

Role/member, session, export, legal-hold, team, and sharing-policy mutations require relevant administrator approval. Pause when the responsible owner or exact target is uncertain.

## Output

Return scope, observed contract, proposed or completed actions, verification evidence, approvals, residual risks, and next owner. State what was not inspected or changed so the receipt cannot overclaim coverage.

## Error Handling

| Condition | Response |
|---|---|
| Tenant or board context mismatches | Stop before mutation and quarantine the credential mapping. |
| Current docs contradict the implementation | Treat the official current contract as a blocker and design an explicit migration. |
| A mutation result is ambiguous | Reconcile state before retrying. |
| Required evidence is unavailable | Return a blocked decision with the smallest safe next probe. |

## Examples

The example is a redacted operator receipt; identifiers are hashes or bounded labels, not board content or credentials.

```text
teams=18; apps=7; excessive=2; orphaned=1; applied=0; plan=enterprise-verified
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Scopes](https://developers.miro.com/reference/scopes)
- [REST comparison](https://developers.miro.com/docs/rest-api-comparison-guide)
