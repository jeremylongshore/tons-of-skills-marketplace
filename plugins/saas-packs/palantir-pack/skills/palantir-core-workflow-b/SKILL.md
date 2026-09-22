---
name: palantir-core-workflow-b
description: >-
  Build and verify an Ontology-backed application with a generated OSDK, bounded object queries, and validated Actions. Use when implementing object reads, links, aggregations, Functions, or writeback. Trigger with "Palantir OSDK" or "Ontology Action".
allowed-tools: Read,Glob,Grep,Write,Edit
version: 2.0.0
argument-hint: "[developer-console-application]"
model: inherit
effort: high
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Requires current Palantir Foundry documentation and approved access for any live resource, permission, data, build, application, or deployment change
tags: [saas, palantir, foundry, ontology, osdk]
---
# Palantir Ontology Application Workflow

## Overview

Use the generated Ontology SDK as the typed contract for a Developer Console application. Keep reads, Functions, and Actions distinct, and validate writeback before execution when the generated SDK and action support it.

## Prerequisites

- Identify the Developer Console application, Foundry environment, selected Ontology entities, grant type, application restrictions, and data owner.
- Generate or select the OSDK language and version required by the application; do not guess object, property, link, Action, or Function API names.
- Read `references/official-docs.md` and the application-specific generated documentation in Developer Console.
- Prepare test objects and a non-production Action path.

## Current Contract

- An OSDK is generated for a selected subset of an Ontology and supports TypeScript, Python, Java, and other-language generation paths.
- Application access is the intersection of the acting user or service user, OAuth scopes, and Developer Console restrictions.
- In TypeScript OSDK 2.x, generated definitions are passed to the client for object operations, Actions, and Functions.
- Action validation and returned edits are explicit options; validation-only and returned-edits modes cannot be assumed interchangeable.

## Authentication

Use the Developer Console grant chosen for the application: authorization code for user-delegated applications or client credentials for a backend service. Never embed a client secret or bearer token. Record scopes and resource restrictions separately from the Foundry permissions of the user or service user.

## Instructions

1. Define the user job and list the minimum object types, interfaces, links, Actions, and Functions the application requires.

2. Configure the Developer Console application and generate the OSDK with only those Ontology resources.

3. Implement a bounded object query with explicit filters, selected properties, deterministic ordering, and pagination.

4. Add link traversal, aggregation, or Function execution only where the generated contract requires it.

5. For writeback, validate the Action against non-production objects, review edits and validation errors, then execute only after owner approval.

## Tool Discipline

- Use **Glob** to locate candidate repositories, manifests, configurations, and evidence without widening scope.
- Use **Grep** to find relevant identifiers, declarations, permissions, errors, and stale claims.
- Use **Read** to inspect the smallest required files and authoritative evidence.
- Use **Write** only for a new approved local draft, test, manifest, or evidence artifact.
- Use **Edit** only for a bounded approved change whose rollback is known.
- Do not use file tools as a substitute for authenticated Foundry operations or owner approval.

## Approval Boundaries

The Ontology owner approves selected resources and Action semantics; the application owner approves OAuth grants and restrictions; the data owner approves production writeback. Never infer approval from SDK generation.

## Output

An application contract containing selected Ontology resources, OSDK language/version, grant type, restrictions, query bounds, Action validation evidence, observed edits, error behavior, and rollback or compensating Action.

## Error Handling

| Condition | Response |
|---|---|
| A generated symbol is missing | Regenerate the OSDK after confirming the entity is selected and published; do not hand-invent API names. |
| A query is unbounded | Add filters, property selection, ordering, and pagination before production use. |
| Action validation fails | Preserve validation details and stop; do not bypass the Ontology rule. |
| A migration changes call syntax | Use the language-specific OSDK migration guide and test the generated version as one atomic upgrade. |

## Examples

### Example 1

Create a read-only service that pages through a selected object type, follows one approved link, requests only required properties, and records the continuation behavior.

### Example 2

Implement an update flow that invokes the generated Action with validation-only first, presents validation errors or expected edits for review, and executes after explicit approval.

## Validation

- The code imports only symbols generated for the current Developer Console application.
- Queries are bounded and pagination is tested.
- Scopes, application restrictions, and user/service-user permissions are all evidenced.
- Action validation and execution are distinguishable in logs and tests.
- The exact OSDK version and generated package are pinned for the release.

## Resources

- [Official documentation and contract notes](references/official-docs.md)
- Re-check the dated contract before any live operation.
- Treat unresolved or changed vendor behavior as a stop condition.
