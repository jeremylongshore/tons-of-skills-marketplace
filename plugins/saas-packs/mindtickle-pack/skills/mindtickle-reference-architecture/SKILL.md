---
name: mindtickle-reference-architecture
description: 'Design a secure, tenant-scoped architecture for Mindtickle identity, managed connectors, APIs, data processing, and operations. Use when designing or reviewing an integration. Trigger with "design Mindtickle architecture".'
argument-hint: "[architecture-brief] [environment]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, mindtickle, architecture, tenancy, integration]
model: inherit
effort: high
compatibility: Designed for Claude Code; architecture approval belongs to customer security, data, identity, platform, and business owners
---
# Tenant-Scoped Mindtickle Integration Architecture

## Overview

Produce a decision-ready architecture that identifies every trust boundary, system of record, contract, data flow, failure mode, and operational owner.

## Prerequisites

- A business workflow, tenant and environment inventory, package entitlement, and data classification
- Current identity, connector, and tenant API artifacts with owners and provenance
- Customer security, retention, residency, reliability, and support requirements

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect repository topology and existing decisions, `WebFetch` for current official contracts, and `Write` or `Edit` for diagrams, decisions, threat models, and redacted evidence.

## Current Contract

Mindtickle supports tenant-specific access, roles, managed integrations, REST-based API families, SCIM, SAML, OpenID, and package-dependent product modules. The architecture must not assume every tenant has every module or that managed connectors and custom APIs share one authorization model.

## Authentication

Model interactive SSO, lifecycle provisioning, managed connectors, and API principals separately. Bind every principal, secret, queue, store, cache, and log to a tenant and environment with least privilege and revocation ownership.

## Instructions

1. Define scope, outcomes, non-goals, actors, systems of record, tenants, environments, and data classes.
2. Draw trust boundaries and directional flows for identity, content, users, reporting, events, administration, support, and deletion.
3. Attach an authoritative contract, owner, authentication class, and permitted operations to every external edge.
4. Choose managed integration, file exchange, tenant API, or human workflow per use case based on supportability and risk.
5. Define tenant isolation, schema validation, idempotency, reconciliation, backpressure, retention, encryption, and audit evidence.
6. Model dependency outage, identity drift, partial writes, duplicate delivery, schema drift, credential compromise, and tenant misrouting.
7. Specify service objectives, alerts, runbooks, support severity, capacity, recovery, and cost ownership.
8. Record alternatives and tradeoffs, then obtain independent security, data, platform, and business review before implementation.

## Approval Boundaries

Do not select a tenant default, combine credentials, export restricted data, introduce an unsupported integration path, or accept residual risk for another owner.

## Output

Return context and data-flow diagrams, contract registry, trust boundaries, tenancy controls, decision records, threat model, failure matrix, owners, open questions, and approval state.

## Error Handling

| Condition | Response |
|---|---|
| An external edge lacks a contract | Mark it blocked and issue vendor or customer questions. |
| Tenant context can be omitted | Redesign the boundary to fail closed before implementation. |
| Managed and custom paths overlap | Assign one source of truth and explicit reconciliation ownership. |

## Example

```text
tenants=2-isolated; identity=sso-plus-scim; reporting=tenant-api; events=polling-until-contract; contracts=all-owned; review=approved-with-one-expiring-risk
```

## Resources

- [Mindtickle integrations](https://www.mindtickle.com/platform/integrations/)
- [Mindtickle Trust](https://www.mindtickle.com/trust/)
- [Subscription services](https://www.mindtickle.com/legal/description-of-subscription-services/)

## Next Steps

Convert each approved external edge into contract fixtures, runbooks, and an independently testable deployment unit.
