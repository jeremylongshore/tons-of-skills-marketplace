---
name: palantir-hello-world
description: >-
  Create a minimal generated-OSDK application that performs one bounded Ontology read and optionally validates one Action. Use when proving a new Developer Console application end to end. Trigger with "Palantir hello world" or "first OSDK app".
allowed-tools: Read,Glob,Grep,Write,Edit
version: 2.0.0
argument-hint: "[developer-console-application]"
model: inherit
effort: high
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Requires current Palantir Foundry documentation and approved access for any live resource, permission, data, build, application, or deployment change
tags: [saas, palantir, foundry, osdk, getting-started]
---
# Palantir OSDK First Read and Validated Action

## Overview

Prove the smallest safe vertical slice: Developer Console application, generated OSDK, authenticated client, bounded object read, and an optional validation-only Action. Avoid mixing the Platform SDK, OSDK, transforms, and deployment in the first proof.

## Prerequisites

- Choose a non-production Foundry environment and a low-sensitivity object type with a few synthetic or approved test objects.
- Identify the application owner, Ontology owner, OSDK language, user-delegated or backend-service grant, and selected Ontology resources.
- Read `references/official-docs.md` plus the generated application-specific documentation in Developer Console.
- Prepare an approved Action only if validation-only behavior is available and no production write is required.

## Current Contract

- Developer Console creates and manages OSDK applications and generates language-specific packages for selected Ontology resources.
- The generated OSDK exposes the actual object types, links, Actions, and Functions selected for that application.
- An OSDK application authenticates with OAuth as a public/confidential user application or backend service, according to its design.
- A first read should be bounded by filters, selected properties, deterministic ordering, and pagination.

## Authentication

Use the Developer Console generated setup for the chosen grant. Keep client secrets and bearer tokens in approved local or deployment secret storage. Record grant type, scopes, restrictions, redirect behavior, and principal without recording credential values.

## Instructions

1. Create or select the Developer Console application and add only one test object type plus an approved Action if needed.

2. Generate and install the OSDK version shown by Developer Console; pin the generated package and compatible client.

3. Initialize the authenticated client using the generated setup and verify the expected principal/environment.

4. Read a small deterministic page of objects with selected properties and record pagination behavior.

5. If writeback is in scope, run the generated Action in validation-only mode, review the result, and stop before execution unless separately approved.

## Tool Discipline

- Use **Glob** to locate candidate repositories, manifests, configurations, and evidence without widening scope.
- Use **Grep** to find relevant identifiers, declarations, permissions, errors, and stale claims.
- Use **Read** to inspect the smallest required files and authoritative evidence.
- Use **Write** only for a new approved local draft, test, manifest, or evidence artifact.
- Use **Edit** only for a bounded approved change whose rollback is known.
- Do not use file tools as a substitute for authenticated Foundry operations or owner approval.

## Approval Boundaries

The Ontology owner approves selected resources; the application owner approves the OAuth client; the data owner approves test data; any Action execution requires explicit writeback approval beyond this first-read workflow.

## Output

A minimal repository or patch with pinned OSDK/client versions, environment-safe configuration, one bounded read, optional validation-only Action, test evidence, and a cleanup/rollback note.

## Error Handling

| Condition | Response |
|---|---|
| The object type is absent from the generated package | Select and publish it in Developer Console, then regenerate; do not create a handwritten substitute. |
| OAuth succeeds but the read is forbidden | Check application restrictions and principal permissions without widening both at once. |
| The query returns too much data | Add filters, properties, page size, and deterministic ordering before proceeding. |
| Action validation reports errors | Present the generated validation result and stop execution. |

## Examples

### Example 1

Generate a TypeScript OSDK for one `Equipment` object type, load a deterministic first page containing only approved properties, and print identifiers rather than sensitive values.

### Example 2

Add a generated `UpdateStatus` Action to a test application, call validation-only with a synthetic object, review the validation result, and leave actual execution disabled.

## Validation

- The package is generated from the target Developer Console application and pinned.
- The client authenticates to the intended Foundry environment and principal.
- The read is bounded, deterministic, and uses approved properties.
- No secret or protected object value is committed or logged.
- An Action, if present, remains validation-only unless execution has a separate receipt.

## Resources

- [Official documentation and contract notes](references/official-docs.md)
- Re-check the dated contract before any live operation.
- Treat unresolved or changed vendor behavior as a stop condition.
