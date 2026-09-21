---
name: salesforce-enterprise-rbac
description: 'Review and govern Salesforce enterprise access across profiles, permission sets and groups, sharing, field access, OAuth apps, SSO, and privileged roles. Use when designing access. Trigger with "review Salesforce access".'
argument-hint: "[org-alias] [persona-or-integration]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, salesforce, rbac, permission-sets, sharing]
model: inherit
effort: high
compatibility: Designed for Claude Code; access, SSO, sharing, app policy, and privileged-role changes require identity, security, admin, and data-owner approval
---
# Salesforce Enterprise Access and Sharing Governance

## Overview

Build least privilege from job and workload needs through app authorization, org permissions, object and field access, record sharing, and periodic review.

## Prerequisites

- Personas and integration workloads, business functions, data classes, orgs, environments, and owners
- Current profiles, permission sets and groups, licenses, roles, sharing defaults and rules, field access, queues, and app policies
- Identity lifecycle, SSO and MFA, privileged access, break-glass, segregation, recertification, and audit requirements

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect approved repository and evidence files, `WebFetch` to re-check current first-party Salesforce documentation, and `Write` or `Edit` only for secretless plans, fixtures, configuration, and redacted receipts.

## Current Contract

Salesforce authorization is layered: identity and app policy, license and profile baseline, permission sets or groups, object CRUD, field access, record sharing, and contextual controls. Effective access must be measured in the target org and user context.

## Authentication

Separate human, integration, deployment, monitoring, support, and break-glass principals. Bind each to approved SSO or OAuth policy, minimum scope, lifecycle, rotation or recertification, revocation, and audit evidence.

## Instructions

1. Define personas and workloads with allowed actions, data, records, environments, hours, and business owners.
2. Inventory effective licenses, profiles, permissions, permission-set groups, roles, sharing defaults and rules, field access, and client apps.
3. Build an entitlement matrix from business need to effective access and identify inherited, overlapping, elevated, dormant, and conflicting grants.
4. Design the minimum profile baseline plus permission sets or groups and record-sharing model; keep integration access separate from users.
5. Test allowed and denied object, field, record, API, event, export, deployment, and admin paths with representative principals.
6. Present assignment, removal, sharing, SSO, app-policy, and break-glass changes for approval and canary them in non-production.
7. Recalculate effective access, review logs, revoke obsolete grants, and schedule owner-attested recertification.

## Approval Boundaries

Do not assign licenses, permissions, groups, roles, sharing rules, app access, SSO policy, or privileged roles without identity, admin, security, and data owners.

## Output

Return the persona matrix, effective-access inventory, gaps and conflicts, target model, denied-path tests, approved changes, revocation proof, and recertification schedule.

## Error Handling

| Condition | Response |
|---|---|
| Permission calculation differs from user behavior | Test the exact user context, sharing, license, session, and app policy before changing grants. |
| Broad profile masks permission-set design | Reduce through a planned migration and prove denied paths before removal. |
| Orphaned integration principal is found | Disable or quarantine through the incident and owner process, then rotate related credentials. |

## Example

A redacted completion receipt might look like this:

```text
persona=case-agent; baseline=minimal; permission-groups=2; sharing=role+rule; denied-tests=pass; excess-grants=3-removed
```

## Resources

- [Permission sets overview](https://help.salesforce.com/s/articleView?id=sf.perm_sets_overview.htm)
- [Salesforce sharing rules](https://help.salesforce.com/s/articleView?id=sf.security_sharing_rules.htm)

## Next Steps

Run the workflow first in the lowest-risk authorized org and preserve its redacted receipt. Schedule a review against the next Salesforce seasonal release and the customer change calendar.
