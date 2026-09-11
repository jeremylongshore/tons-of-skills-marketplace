---
name: salesforce-architecture-variants
description: 'Analyze Salesforce direct API, middleware, event-driven, replicated-data, and hybrid integration architectures against explicit constraints. Use when making architecture decisions. Trigger with "compare Salesforce architectures".'
argument-hint: "[use-case] [constraints]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, salesforce, architecture, decision-record, integration-patterns]
model: inherit
effort: high
compatibility: Designed for Claude Code; new vendors, data movement, trust boundaries, and production architecture require enterprise approval
---
# Salesforce Integration Architecture Variants

## Overview

Produce a falsifiable architecture decision that explains why one interaction pattern fits each use case and which tradeoffs remain.

## Prerequisites

- Use cases, business invariants, sources of truth, consumers, latency, volume, ordering, consistency, and recovery needs
- Org products, APIs, events, limits, identities, data classes, residency, retention, support, and existing platforms
- Security, operability, cost, skills, vendor, migration, lock-in, disaster recovery, and change-control constraints

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect approved repository and evidence files, `WebFetch` to re-check current first-party Salesforce documentation, and `Write` or `Edit` only for secretless plans, fixtures, configuration, and redacted receipts.

## Current Contract

Salesforce documents remote process, batch, data synchronization, and event integration patterns. Direct REST, composite, bulk, Pub/Sub or CDC, middleware, event relay, and replicated read models differ in coupling, consistency, capacity, and recovery.

## Authentication

Model client apps, OAuth flows, principals, scopes, CRUD and field access, sharing, secret custody, rotation, revocation, and break-glass separately for every variant.

## Instructions

1. Write decision drivers and non-negotiable invariants before naming a preferred technology.
2. Model direct synchronous API, managed or customer middleware, Salesforce events, scheduled bulk, replicated data, and hybrid variants.
3. For each, trace authority, data and event flow, transactions, ordering, idempotency, limits, failure isolation, reconciliation, and recovery.
4. Evaluate security, privacy, residency, audit, operability, latency, throughput, cost, skills, vendor support, and lock-in with evidence.
5. Run threat, failure, capacity, data-correctness, and migration exercises against the leading variants.
6. Prototype the riskiest assumption with synthetic data in the lowest-risk authorized environment.
7. Record the decision, rejected alternatives, evidence, uncertainty, conditions that invalidate it, migration stages, and review date.

## Approval Boundaries

Do not select a vendor, create trust, replicate data, establish new system authority, or start production implementation without architecture and owners.

## Output

Return the driver matrix, diagrams, variant scores with evidence, prototype result, decision and dissent, risks, migration and rollback plan, and review triggers.

## Error Handling

| Condition | Response |
|---|---|
| All variants score the same | Refine measurable drivers and constraints instead of choosing by preference. |
| A variant lacks reconciliation | Mark it non-viable for mutable business data until a source-of-truth recovery path exists. |
| Key entitlement or capacity is unknown | Keep the decision provisional and obtain current org evidence. |

## Example

A redacted completion receipt might look like this:

```text
usecase=inventory-view; chosen=replicated-read; writes=source-only; freshness=5m; reconcile=daily; invalidator=latency-under-30s
```

## Resources

- [Salesforce integration patterns](https://developer.salesforce.com/docs/atlas.en-us.integration_patterns_and_practices.meta/integration_patterns_and_practices/)
- [Salesforce Pub/Sub API](https://developer.salesforce.com/docs/platform/pub-sub-api/overview)

## Next Steps

Run the workflow first in the lowest-risk authorized org and preserve its redacted receipt. Schedule a review against the next Salesforce seasonal release and the customer change calendar.
