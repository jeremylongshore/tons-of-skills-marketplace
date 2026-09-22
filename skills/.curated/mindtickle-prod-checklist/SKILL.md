---
name: mindtickle-prod-checklist
description: 'Run a production-readiness review for Mindtickle programs, identity, managed connectors, and custom adapters. Use when approaching go-live or a material scope expansion. Trigger with "review Mindtickle production readiness".'
argument-hint: "[service-or-program] [go-live-date]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, mindtickle, production-readiness, governance, operations]
model: inherit
effort: high
compatibility: Designed for Claude Code; production approval remains with customer business, security, data, identity, and service owners
---
# Mindtickle Production Readiness Gate

## Overview

Issue an evidence-backed go, conditional-go, or no-go decision across entitlement, identity, data, reliability, support, and rollback.

## Prerequisites

- A frozen scope, owners, launch window, user population, data classes, and business acceptance
- Current tenant entitlement, architecture, threat model, test results, and operational runbooks
- Named support plan, on-call coverage, communications, rollback, and evidence retention

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect evidence and configuration, `WebFetch` for current official and authorized terms, and `Write` or `Edit` for the review record and remediation evidence.

## Current Contract

Mindtickle assigns tenant administration capabilities by role and package, provides managed integrations and customer-specific technical solutions, and publishes Support and SLA terms. Production readiness must also cover the customer's identity provider, data systems, adapters, and business process.

## Authentication

Verify named principals, least privilege, tenant isolation, SSO and provisioning ownership, credential rotation, revocation, break-glass access, and evidence that no secrets enter logs or artifacts.

## Instructions

1. Confirm scope, package entitlement, tenant and environment identity, supported operations, and contract digests.
2. Review data minimization, lawful use, retention, deletion, residency commitments, export controls, and learner communications.
3. Validate SSO, lifecycle provisioning, roles, disabled-user handling, tenant isolation, and periodic access review.
4. Verify contract tests, pilot or canary evidence, capacity policy, monitoring, reconciliation, backup assumptions, and dependency failure behavior.
5. Exercise credential revocation, ambiguous write handling, partial rollout rollback, and support escalation through tabletop or non-production tests.
6. Reconcile launch population, content, schedules, notifications, and downstream mappings with their systems of record.
7. List every exception with risk owner, compensating control, expiry, and blocking status.
8. Obtain independent sign-off and record go, conditional-go, or no-go with immutable evidence links.

## Approval Boundaries

Do not waive a control, accept residual risk for another owner, enable production, or mark an untested rollback ready.

## Output

Return the reviewed scope, evidence matrix, blockers, expiring exceptions, sign-offs, decision, launch conditions, rollback state, and first operational review date.

## Error Handling

| Condition | Response |
|---|---|
| Required evidence is stale | Mark the gate failed until it is rerun against the release candidate. |
| An exception has no owner or expiry | Treat it as a blocker. |
| Support entitlement is unclear | Resolve the contracted channel and severity path before go-live. |

## Example

```text
scope=user-sync-v2; evidence=current; blockers=0; exceptions=1-expiring; approvals=security,data,service; decision=conditional-go
```

## Resources

- [Mindtickle Support Services](https://www.mindtickle.com/legal/support-services/)
- [Mindtickle Trust and shared responsibility](https://www.mindtickle.com/trust/)
- [Subscription services](https://www.mindtickle.com/legal/description-of-subscription-services/)

## Next Steps

Schedule the first access, reconciliation, and outcome reviews before opening production traffic.
