---
name: workhuman-reference-architecture
description: 'Design a governed Workhuman architecture across HCM, recognition, rewards, workplace integrations, customer adapters, analytics, and evidence. Use when designing or reviewing the system. Trigger with "design a Workhuman architecture".'
argument-hint: "[tenant-or-program] [systems]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.4.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, workhuman, architecture, hris, governance]
model: inherit
effort: high
compatibility: Designed for Claude Code; architecture decisions affecting identity, workforce, awards, financial flows, integrations, and data governance require accountable-owner approval
---
# Governed Workhuman Reference Architecture

## Overview

Define explicit authority, trust, data, financial, and recovery boundaries so Workhuman complements rather than silently replaces HCM and customer systems.

## Prerequisites

- Tenant products, program goals, systems inventory, data classes, regions, and owners
- Current Workhuman and customer implementation contracts
- Service levels, retention, financial-control, incident, continuity, and audit requirements

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect system topology and contracts, `WebFetch` for current first-party context, and `Write` or `Edit` for diagrams, decision records, mappings, and redacted evidence.

## Current Contract

Workhuman publicly positions Workday as authority for foundational and organizational worker data in its certified integration, with Workhuman managing recognition and rewards. It also provides workplace integrations and an open API. Exact customer boundaries, routes, fields, schedules, and capabilities remain contract-specific.

## Authentication

Model human SSO, administrators, managed integrations, customer adapters, HCM principals, and downstream consumers as distinct trust zones with least privilege and explicit tenant binding.

## Instructions

1. Inventory actors, products, HCM, identity, payroll, collaboration surfaces, analytics, support, and customer-owned services.
2. Assign authority for worker identity, organization, eligibility, program policy, recognition, award, spend, redemption, payroll, and analytical derivatives.
3. Draw trust zones, data classes, directions, protocols, principals, secret stores, egress, retention, residency, and audit boundaries.
4. Put customer API access behind one contract-driven adapter with validation, idempotency, backpressure, redaction, and safe correlation.
5. Define managed-connector boundaries separately; do not duplicate vendor-owned behavior in customer code without a justified decision.
6. Specify event, polling, report, or reconciliation modes, checkpoints, duplicates, ordering, partial failure, and recovery.
7. Add approval gates for worker, program, recognition, award, financial, identity, and connector mutations.
8. Test loss of HCM, Workhuman, identity, connector, queue, analytics, and secret-provider dependencies and record degraded modes.

## Approval Boundaries

Do not designate a new system of record, duplicate sensitive data, add trust paths, or alter financial and workforce flows without architecture, security, privacy, HCM, payroll, and program approval.

## Output

Return the authority matrix, context and trust diagrams, data inventory, adapter and connector boundaries, failure model, reconciliation design, decisions, risks, and review triggers.

## Error Handling

| Condition | Response |
|---|---|
| Two systems claim the same field authority | Resolve ownership before integration design continues. |
| Contract cannot support a required flow | Record a gap and select a supported connector, report, or manual control. |
| Recovery depends on unverified writes | Redesign around checkpoints and authoritative reconciliation. |

## Example

A redacted completion receipt might look like this:

```text
worker-authority=workday; recognition-authority=workhuman; payroll=workday; workplace=managed-teams; adapter=contract-pinned; reconciliation=scheduled
```

## Resources

- [Workhuman integrations](https://www.workhuman.com/capabilities/integrations/)
- [Workhuman security and privacy](https://www.workhuman.com/why-workhuman/security-and-privacy/)
- [Workhuman Social Recognition](https://www.workhuman.com/platform/social-recognition/)

## Next Steps

Review the architecture when products, contracts, regions, systems of record, identity, or financial responsibilities change.
