---
name: palantir-reference-architecture
description: >-
  Design a production Foundry architecture spanning data pipelines, Ontology, OSDK or Platform APIs, deployment, governance, and operations. Use when defining a new platform integration or reviewing an existing one. Trigger with "Palantir architecture".
allowed-tools: Read,Glob,Grep,Write,Edit
version: 2.0.0
argument-hint: "[system-or-workflow]"
model: inherit
effort: high
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Requires current Palantir Foundry documentation and approved access for any live resource, permission, data, build, application, or deployment change
tags: [saas, palantir, foundry, architecture, integration]
---
# Palantir Foundry Integration Architecture

## Overview

Start from business decisions and data authority, then map each responsibility to a Foundry primitive. Keep ingestion, transformation, Ontology semantics, application access, deployment, and telemetry independently governable.

## Prerequisites

- Identify users, decisions, source systems, data owners, update/writeback semantics, service objectives, compliance boundaries, and recovery needs.
- Inventory current and proposed Foundry projects, datasets, transforms, Ontology entities, applications, products, modules, and external integrations.
- Read `references/official-docs.md` and resolve target-enrollment feature availability with platform owners.
- Declare trust boundaries and authoritative systems before drawing components.

## Current Contract

- Python transforms provide batch/incremental pipelines with multiple compute engines and data expectations.
- The Ontology represents domain objects, links, Actions, and Functions; OSDK applications receive a generated subset of it.
- Platform SDKs expose broader Foundry/AIP REST APIs, while OSDKs provide application-specific Ontology contracts.
- DevOps/Marketplace and Compute Modules cover different release-managed and interactive-container deployment needs.

## Authentication

Define user-delegated and service authentication at each application boundary. Record OAuth grants, principals, scopes, Developer Console restrictions, secret storage, rotation, and revocation without placing credential values in the architecture artifact.

## Instructions

1. Define capabilities, owners, authoritative data, side effects, latency/freshness objectives, and failure domains.

2. Place ingestion and transformations into projects with explicit inputs, outputs, lineage, expectations, and compute choices.

3. Model domain semantics and writeback in the Ontology, including object/property security and Action validation.

4. Choose generated OSDK or Platform SDK per application boundary and constrain OAuth scopes, restrictions, and principal permissions.

5. Choose DevOps product, Developer Console application, or Compute Module deployment, then add metrics, governed logs, audit evidence, and rollback.

## Tool Discipline

- Use **Glob** to locate candidate repositories, manifests, configurations, and evidence without widening scope.
- Use **Grep** to find relevant identifiers, declarations, permissions, errors, and stale claims.
- Use **Read** to inspect the smallest required files and authoritative evidence.
- Use **Write** only for a new approved local draft, test, manifest, or evidence artifact.
- Use **Edit** only for a bounded approved change whose rollback is known.
- Do not use file tools as a substitute for authenticated Foundry operations or owner approval.

## Approval Boundaries

Domain and data owners approve semantics and writeback; security owners approve boundaries and controls; platform owners approve deployment primitives; operations owners approve service objectives and recovery.

## Output

A decision record, context/component/data-flow diagrams, responsibility and authority matrix, data contracts, access model, API/SDK choice, deployment topology, failure analysis, observability design, and staged rollout.

## Error Handling

| Condition | Response |
|---|---|
| One service owns ingestion, policy, writeback, and release | Separate responsibilities and failure domains before scaling the design. |
| The architecture depends on handwritten Ontology API names | Anchor it to generated OSDK/application metadata. |
| Granular security is assumed to propagate downstream | Add mandatory controls or redesign downstream handling. |
| No rollback exists for schema or Ontology changes | Stage compatibility and dual-read/write behavior before promotion. |

## Examples

### Example 1

Design a supplier-risk workflow with connector ingestion, incremental transforms, governed datasets, supplier Ontology objects, validated Actions, a generated OSDK application, and release-managed environments.

### Example 2

Review a container integration by deciding whether it belongs in a Compute Module, mapping OAuth/resource restrictions, data flows, replica behavior, logs, and prior-image rollback.

## Validation

- Every component has one responsibility, owner, authority, and failure behavior.
- Data lineage and writeback semantics are explicit.
- SDK and deployment choices match current Foundry contracts.
- Positive/negative access and downstream control propagation are testable.
- Service objectives, alerts, recovery, and version rollback are complete.

## Resources

- [Official documentation and contract notes](references/official-docs.md)
- Re-check the dated contract before any live operation.
- Treat unresolved or changed vendor behavior as a stop condition.
