---
name: flyio-reference-architecture
description: >-
  Design a Fly.io multi-region architecture with explicit routing, Machine, data, private-network, observability, and recovery boundaries. Use when reviewing a production topology. Trigger with: "architect app on Fly", "design multi-region Fly service", "review Fly platform topology".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[workload-regions-and-data-contract]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - flyio
  - architecture
  - multi-region
  - resilience
compatibility: 'Requires workload and data requirements, service objectives, approved regions, dependency ownership, and a cost and recovery model.'
---

# Fly.io Multi-Region Application Architecture

## Overview

Compose Fly.io primitives without implying global state that the platform does not provide. Anycast and Fly Proxy route toward Machines, 6PN connects services inside an organization, Machines and volumes are regional, and Managed Postgres has its own supported-region and recovery contract.

## Prerequisites

- Users, traffic, latency, availability, residency, recovery, and consistency requirements
- Service and process-group boundaries plus external dependencies
- Current provider regions, capacity, pricing, and Managed Postgres availability

## Instructions

### Step 1: Partition stateless and stateful work

Separate request-serving, workers, scheduled tasks, caches, durable databases, and region-local files. Name the system of record for every data class.

### Step 2: Design routing and placement

Choose primary and secondary regions from observed users, dependency location, residency, and capacity. Document Fly Proxy, public IP, Flycast, or dynamic routing behavior.

### Step 3: Design the Machine fleet

Set process groups, VM resources, Machine counts, health checks, deployment strategy, autostart, shutdown, and failure-domain expectations per region.

### Step 4: Design data explicitly

Use Managed Postgres where its service contract fits. Use volumes only with software-managed replication and recovery or for disposable regional state; never present one volume as multi-region storage.

### Step 5: Design private and external connectivity

Map 6PN names, organization boundaries, WireGuard peers, outbound requirements, certificates, DNS, and third-party trust zones.

### Step 6: Prove resilience and operations

Exercise regional and dependency failure, deploy rollback, database restore, volume restore, secret rotation, monitoring, cost controls, and ownership handoff.

## Authentication

Use separate scoped identities for deployment, observation, database access, and external integrations. Protect 6PN and WireGuard credentials, App secrets, and database URLs; private networking narrows reachability but does not replace application authentication.

## Tool Discipline

Use Read and Grep to inspect application configuration, deployment evidence, provider documentation, fixtures, logs, schemas, and existing tests before proposing a change. Use Write or Edit only for an approved plan, configuration, implementation, test, or redacted receipt. Do not create, deploy, scale, restart, stop, suspend, destroy, rotate, revoke, expose, or migrate live Fly.io resources without explicit operator approval.

## Output

- Architecture diagram and authority map
- Region, routing, Machine, data, identity, observability, cost, and recovery decisions
- Failure-mode exercises with measured recovery and unresolved risks

Return the target organization, app, environment, region set, Machine or database identifiers, source-contract fingerprint, evidence, unresolved risks, rollback state, and final decision without exposing tokens, secrets, connection strings, or customer data.

## Examples

A global API runs stateless Machines in three evidence-selected regions while writes stay close to Managed Postgres in a supported primary region. Fly Proxy routing, read behavior, failure fallback, and database recovery are explicit; a cache volume is treated as disposable regional state.

## Error Handling

| Failure | Response |
| --- | --- |
| Topology assumes global volume storage | Replace the assumption with Managed Postgres, an external replicated store, or application-managed replication. |
| Region lacks required service or capacity | Choose from current provider data and revisit latency, residency, and recovery tradeoffs. |
| Private path crosses organizations | Use an explicitly approved inter-network mechanism and application authentication; same-organization 6PN assumptions do not apply. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Machines API setup](https://fly.io/docs/machines/api/working-with-machines-api/)
- [Automation and tokens](https://fly.io/docs/flyctl/integrating/)
- [App configuration](https://fly.io/docs/reference/configuration/)
- [Regions](https://fly.io/docs/reference/regions/)
- [Private networking](https://fly.io/docs/networking/private-networking/)
- [Managed Postgres](https://fly.io/docs/mpg/)
- [Fly Volumes](https://fly.io/docs/volumes/)
