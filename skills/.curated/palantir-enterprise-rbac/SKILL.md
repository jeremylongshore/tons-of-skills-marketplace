---
name: palantir-enterprise-rbac
description: >-
  Design and audit Foundry access using projects, group role grants, mandatory controls, and Developer Console restrictions. Use when onboarding teams, service users, or applications. Trigger with "Palantir RBAC" or "Foundry access review".
allowed-tools: Read,Glob,Grep,Write,Edit
version: 2.0.0
argument-hint: "[project-application-or-principal]"
model: inherit
effort: high
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Requires current Palantir Foundry documentation and approved access for any live resource, permission, data, build, application, or deployment change
tags: [saas, palantir, foundry, rbac, access-control]
---
# Palantir Foundry Access-Control Design

## Overview

Treat access as the intersection of several control planes. Project roles govern discretionary capabilities, mandatory controls continue to apply, and OAuth application restrictions constrain API clients independently.

## Prerequisites

- Identify the resources, projects, spaces, organizations, markings or CBAC requirements, groups, users, service users, and Developer Console applications in scope.
- Name the data owner, project owner, application owner, information-security owner, and access-review cadence.
- Read `references/official-docs.md` and use the Check access panel for concrete principals and resources.
- Begin with a read-only entitlement inventory; do not grant access while discovering it.

## Current Contract

- Default project roles are Owner, Editor, Viewer, and Discoverer, and deployments may also define custom roles.
- Palantir recommends group role grants at the project level to reduce individual-grant sprawl.
- Organizations, markings, and CBAC can deny access even when a project role is present.
- Developer Console token authority is limited by the user/service-user permissions, application restrictions, and requested OAuth scope.

## Authentication

For API clients, record the OAuth grant type, service user or delegated user, requested scopes, and Developer Console resource/operation restrictions. Never treat possession of a token as evidence that the underlying principal should have access.

## Instructions

1. Build a matrix of principal or group, project role, resource purpose, mandatory requirements, application restrictions, owner, and expiry.

2. Replace unnecessary direct user grants with reviewed group grants while preserving break-glass and accountable-owner requirements.

3. Use Check access on representative resources to explain both discretionary and mandatory requirements for each persona.

4. For service applications, restrict the Developer Console client to the minimum operations and Ontology or Platform SDK resources.

5. Run positive and negative access tests, obtain owner attestations, remove temporary access, and schedule recertification.

## Tool Discipline

- Use **Glob** to locate candidate repositories, manifests, configurations, and evidence without widening scope.
- Use **Grep** to find relevant identifiers, declarations, permissions, errors, and stale claims.
- Use **Read** to inspect the smallest required files and authoritative evidence.
- Use **Write** only for a new approved local draft, test, manifest, or evidence artifact.
- Use **Edit** only for a bounded approved change whose rollback is known.
- Do not use file tools as a substitute for authenticated Foundry operations or owner approval.

## Approval Boundaries

Project owners approve discretionary roles; security authorities approve markings, CBAC, and organization membership; application owners approve OAuth restrictions; data owners approve data access. No single approval substitutes for the others.

## Output

An entitlement matrix, direct-grant exceptions, group design, mandatory-control map, application restrictions, access-check evidence, positive/negative tests, approvals, expirations, and recertification date.

## Error Handling

| Condition | Response |
|---|---|
| A Viewer role still cannot read data | Inspect mandatory controls, dependent resources, and application restrictions before changing the role. |
| A service user can reach too much | Tighten its Foundry permissions, Developer Console restrictions, and requested scopes as separate changes. |
| Ownership is unclear | Stop grants and resolve the accountable project and data owners. |
| A direct grant is operationally necessary | Document the exception, scope, approver, expiry, and monitored break-glass procedure. |

## Examples

### Example 1

Onboard an analytics team through a group with Viewer access to one project, verify required markings separately, and use Check access to prove an unauthorized control persona remains denied.

### Example 2

Review a backend application whose service user has Editor access by reducing project permissions and constraining the Developer Console client to the exact Platform SDK operations it needs.

## Validation

- Every grant maps to a business purpose and accountable owner.
- Group roles are preferred and direct grants are explicit exceptions.
- Positive and negative personas are tested against real representative resources.
- OAuth scopes, application restrictions, and Foundry permissions are evidenced separately.
- Temporary access and exceptions have expirations and recertification.

## Resources

- [Official documentation and contract notes](references/official-docs.md)
- Re-check the dated contract before any live operation.
- Treat unresolved or changed vendor behavior as a stop condition.
