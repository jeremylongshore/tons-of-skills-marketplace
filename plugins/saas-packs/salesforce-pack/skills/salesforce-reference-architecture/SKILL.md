---
name: salesforce-reference-architecture
description: 'Design a governed Salesforce integration architecture with explicit authority, identity, API, event, data, evidence, limit, and recovery boundaries. Use when conducting architecture reviews. Trigger with "design Salesforce architecture".'
argument-hint: "[system-or-domain] [constraints]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, salesforce, architecture, integration, governance]
model: inherit
effort: high
compatibility: Designed for Claude Code; architecture and production trust-boundary decisions require enterprise, security, data, and Salesforce platform approval
---
# Governed Salesforce Integration Reference Architecture

## Overview

Create an evidence-backed target architecture that names every source of truth, mutation path, principal, data class, failure boundary, and recovery mechanism.

## Prerequisites

- Business capabilities, system context, sources of truth, data owners, consumers, service objectives, and constraints
- Org topology, Salesforce products, External Client Apps or existing Connected Apps, APIs, events, limits, and entitlements
- Security, privacy, residency, retention, reconciliation, disaster recovery, support, and change-control requirements

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect approved repository and evidence files, `WebFetch` to re-check current first-party Salesforce documentation, and `Write` or `Edit` only for secretless plans, fixtures, configuration, and redacted receipts.

## Current Contract

Salesforce provides multiple synchronous, asynchronous, bulk, composite, and event integration surfaces with org-specific availability and limits. No single direct API, middleware, replicated database, or event pattern is correct for every domain.

## Authentication

Model human, integration, deployment, diagnostic, and break-glass principals separately. Bind each to an approved app, OAuth flow, minimum permissions, secret custody, rotation, revocation, and audit path.

## Instructions

1. Map systems, trust zones, sources of truth, record and event ownership, consumers, data classes, and business invariants.
2. Inventory orgs, products, editions, packages, schemas, API versions, events, limits, identities, and operational dependencies.
3. Select interaction patterns per use case: synchronous request, asynchronous bulk, composite, event, scheduled reconciliation, or replicated read model.
4. Define contracts for schema, versioning, idempotency, ordering, pagination, checkpoints, retries, dead letters, and backfills.
5. Design CRUD and field access, sharing, encryption, retention, audit, residency, redaction, support, and separation of duties.
6. Model outages, limit exhaustion, partial writes, event gaps, schema drift, wrong-org access, and disaster recovery.
7. Validate with threat, failure, capacity, cost, operability, migration, and rollback reviews and record rejected alternatives.

## Approval Boundaries

Do not establish new trust, data movement, system authority, production mutation, or vendor dependency without architecture, security, data, and business approval.

## Output

Return context and container views, authority matrix, trust and data-flow boundaries, contracts, failure scenarios, capacity and cost assumptions, decisions, risks, and migration plan.

## Error Handling

| Condition | Response |
|---|---|
| Two systems claim authority for the same field | Resolve ownership and conflict policy before implementation. |
| Recovery depends only on replay availability | Add durable reconciliation and backfill from the source of truth. |
| Entitlement or limit assumption is unverified | Mark the design provisional and obtain current org evidence. |

## Example

A redacted completion receipt might look like this:

```text
domain=orders; authority=erp; salesforce=crm-projection; writes=governed; events=cdc; reconcile=daily; recovery=tested
```

## Resources

- [Salesforce integration patterns](https://developer.salesforce.com/docs/atlas.en-us.integration_patterns_and_practices.meta/integration_patterns_and_practices/)
- [Salesforce Pub/Sub API](https://developer.salesforce.com/docs/platform/pub-sub-api/overview)

## Next Steps

Run the workflow first in the lowest-risk authorized org and preserve its redacted receipt. Schedule a review against the next Salesforce seasonal release and the customer change calendar.
