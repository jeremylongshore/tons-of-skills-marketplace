---
name: palantir-upgrade-migration
description: >-
  Upgrade a Palantir OSDK, Platform SDK, generated application, or release-managed product through pinned contracts and reversible stages. Use when adopting a new SDK generation or product version. Trigger with "upgrade Palantir SDK".
allowed-tools: Read,Glob,Grep,Write,Edit
version: 2.0.0
argument-hint: "[package-or-product-version]"
model: inherit
effort: high
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Requires current Palantir Foundry documentation and approved access for any live resource, permission, data, build, application, or deployment change
tags: [saas, palantir, foundry, upgrade, migration]
---
# Palantir SDK and Application Upgrade

## Overview

Treat generated OSDK changes and official Platform SDK releases as contract migrations. Freeze the old and new artifacts, read the relevant migration guide or release notes, update one boundary, and prove compatibility in a non-production environment.

## Prerequisites

- Identify the current and target package/product versions, generated Developer Console application, language/runtime, call sites, owners, and target environments.
- Capture lockfiles, generated metadata, OAuth restrictions, tests, representative queries/Actions, and prior product or image version.
- Read `references/official-docs.md` and the language-specific migration guide or official release history.
- Prepare a branch and non-production installation with a documented downgrade.

## Current Contract

- Generated OSDK packages are tied to selected Ontology resources and compatible client versions.
- TypeScript OSDK migration guides document syntax changes for object access, Actions, batch Actions, and Functions/queries.
- Official Platform SDK repositories publish immutable releases and generated API changes.
- DevOps/Marketplace release management can promote and roll back versioned products across environments.

## Authentication

Do not change grant type, scopes, resource restrictions, service-user permissions, or secrets as an incidental SDK upgrade. If an auth change is required, review and test it as a separate security migration.

## Instructions

1. Freeze the old state and create a compatibility inventory of imports, generated entities, operations, scopes, runtime, and tests.

2. Review official migration/release evidence and classify source, generated-code, runtime, and behavior changes.

3. Update the pinned SDK/client or product on a branch without unrelated refactors.

4. Run unit/contract tests plus representative reads, pagination, Actions in validation-only mode, auth denials, throttling, and error mapping.

5. Install in non-production, compare behavior and telemetry, obtain approval, promote the exact version, and retain the tested downgrade.

## Tool Discipline

- Use **Glob** to locate candidate repositories, manifests, configurations, and evidence without widening scope.
- Use **Grep** to find relevant identifiers, declarations, permissions, errors, and stale claims.
- Use **Read** to inspect the smallest required files and authoritative evidence.
- Use **Write** only for a new approved local draft, test, manifest, or evidence artifact.
- Use **Edit** only for a bounded approved change whose rollback is known.
- Do not use file tools as a substitute for authenticated Foundry operations or owner approval.

## Approval Boundaries

Application and product owners approve the version; Ontology owners approve regenerated resources; security owners approve any separately proposed auth change; production owners approve promotion and downgrade windows.

## Output

An old/new contract inventory, release evidence, dependency diff, code changes, test matrix, non-production receipt, approvals, exact promoted version, observation, and downgrade procedure.

## Error Handling

| Condition | Response |
|---|---|
| Generated symbols disappear | Confirm Developer Console selections and published Ontology changes before adapting code. |
| Tests pass but access expands | Block promotion and compare scopes, restrictions, principal permissions, and selected resources. |
| A transitive dependency changes runtime behavior | Pin or update the dependency deliberately and extend the contract tests. |
| Downgrade cannot restore compatibility | Keep production on the old version and redesign the migration sequence. |

## Examples

### Example 1

Move a TypeScript OSDK application to a new generated package by applying the documented Action/query syntax changes, pinning a compatible client, and validating reads plus validation-only Actions.

### Example 2

Upgrade the Python Platform SDK on a branch, compare generated endpoint models and errors, run bounded API contract tests, deploy to test, and retain the previous lockfile and product version.

## Validation

- The old and target artifacts are immutable and identifiable.
- Only documented or reviewed contract changes are included.
- Auth authority and selected resources do not expand unintentionally.
- Representative success, denial, pagination, retry, and Action-validation paths pass.
- The downgrade is tested against the prior compatible dependencies and environment.

## Resources

- [Official documentation and contract notes](references/official-docs.md)
- Re-check the dated contract before any live operation.
- Treat unresolved or changed vendor behavior as a stop condition.
