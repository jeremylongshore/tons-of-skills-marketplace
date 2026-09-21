---
name: palantir-migration-deep-dive
description: >-
  Plan and execute a phased migration of data pipelines, Ontology applications, or external integrations into Foundry. Use when replacing a legacy system or moving workloads across Foundry environments. Trigger with "Palantir migration" or "Foundry cutover".
allowed-tools: Read,Glob,Grep,Write,Edit
version: 2.0.0
argument-hint: "[source-system-and-target-product]"
model: inherit
effort: high
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Requires current Palantir Foundry documentation and approved access for any live resource, permission, data, build, application, or deployment change
tags: [saas, palantir, foundry, migration, cutover]
---
# Palantir Foundry Migration and Cutover

## Overview

Migrate contracts and evidence, not just bytes. Inventory data semantics, identities, access controls, pipeline transactions, Ontology entities, applications, and operational dependencies before dual-running a bounded slice.

## Prerequisites

- Name source and target owners, business workflows, datasets, schemas, identities, controls, service objectives, retention, and rollback deadline.
- Choose the target Foundry primitives: connectors, transforms, Ontology resources, OSDK application, DevOps product, or Compute Module.
- Read `references/official-docs.md` and document features or resources that do not map directly.
- Establish a frozen baseline and approved non-production landing zone.

## Current Contract

- Foundry applications and resources can be packaged and promoted with DevOps and Marketplace across environment spaces.
- Developer Console application installation remaps supported parameters, but API-name consistency and dependencies still require explicit handling.
- Incremental transforms have transaction-history requirements and must reconcile with snapshot behavior.
- Access control combines project roles, mandatory controls, Ontology policies, and application restrictions.

## Authentication

Inventory source and target identities, OAuth grant types, service users, scopes, and application restrictions as separate migration contracts. Store secrets in approved managers, rotate them through a staged cutover, and never copy source credentials into the target environment.

## Instructions

1. Inventory source contracts: identifiers, schemas, update/delete semantics, volumes, SLAs, consumers, permissions, audit requirements, and failure modes.

2. Design target datasets, transforms, Ontology entities, Actions, applications, and controls with an explicit mapping for every source contract.

3. Load a bounded historical slice, then establish incremental capture or repeatable deltas with reconciliation keys.

4. Dual-run representative workflows and compare counts, aggregates, sampled records, actions, permissions, latency, and failure handling.

5. Freeze changes, reconcile final deltas, obtain owner sign-off, cut consumers over in stages, and retain the tested rollback window.

## Tool Discipline

- Use **Glob** to locate candidate repositories, manifests, configurations, and evidence without widening scope.
- Use **Grep** to find relevant identifiers, declarations, permissions, errors, and stale claims.
- Use **Read** to inspect the smallest required files and authoritative evidence.
- Use **Write** only for a new approved local draft, test, manifest, or evidence artifact.
- Use **Edit** only for a bounded approved change whose rollback is known.
- Do not use file tools as a substitute for authenticated Foundry operations or owner approval.

## Approval Boundaries

Data owners approve semantics and reconciliation; security owners approve target controls; application owners approve consumer cutover; operations owners approve freeze and rollback windows. Destructive source retirement is a separate approval after the rollback period.

## Output

A migration inventory, source-to-target mapping, control matrix, dependency graph, rehearsal results, reconciliation report, cutover timeline, owner approvals, rollback triggers, and retirement decision.

## Error Handling

| Condition | Response |
|---|---|
| A source field has no target meaning | Stop automatic mapping and obtain domain-owner resolution. |
| Dual-run results diverge | Keep consumers on the source, isolate the difference, and repeat from a known checkpoint. |
| Target permissions are broader | Block cutover until negative-access tests and mandatory controls match the approved policy. |
| Final delta exceeds the window | Abort cutover and rehearse a smaller partition or faster incremental path. |

## Examples

### Example 1

Migrate an operational dataset into transforms and an Ontology object type by baselining history, replaying incremental changes, and reconciling keys, deletes, aggregates, and access before moving readers.

### Example 2

Move an OSDK application to a release-managed environment by packaging its Developer Console application, mapping parameters and dependencies, testing OAuth/resource restrictions, and rehearsing rollback.

## Validation

- Every source contract has an owner-approved target or explicit exception.
- Historical and incremental reconciliation meet defined tolerances.
- Positive and negative access tests match policy.
- Consumers, schedules, and writeback are cut over in observable stages.
- Rollback remains executable until the approved retirement decision.

## Resources

- [Official documentation and contract notes](references/official-docs.md)
- Re-check the dated contract before any live operation.
- Treat unresolved or changed vendor behavior as a stop condition.
