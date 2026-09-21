---
name: palantir-sdk-patterns
description: >-
  Implement resilient Palantir clients by choosing generated OSDK or Platform SDK, pinning contracts, and bounding authentication, pagination, retries, and writes. Use when building shared Foundry client code. Trigger with "Palantir SDK patterns".
allowed-tools: Read,Glob,Grep,Write,Edit
version: 2.0.0
argument-hint: "[application-or-client-library]"
model: inherit
effort: high
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Requires current Palantir Foundry documentation and approved access for any live resource, permission, data, build, application, or deployment change
tags: [saas, palantir, foundry, sdk, client-design]
---
# Palantir SDK Boundary and Client Patterns

## Overview

Keep application-specific Ontology access in the generated OSDK and broader platform operations in the Platform SDK. Wrap transport concerns without hiding the generated entity contract, OAuth authority, request identifiers, or Action validation.

## Prerequisites

- Identify the application job, language, required Ontology entities or Platform API operations, write behavior, and owner.
- Select the target Developer Console application or current official Platform SDK package and pin its version.
- Read `references/official-docs.md`, generated application documentation, and relevant migration guide.
- Define request deadlines, page bounds, retryable statuses, idempotency, telemetry, and secret storage.

## Current Contract

- OSDK packages are generated for selected Ontology resources and support application-specific typed access.
- Official Python and TypeScript Platform SDKs wrap Foundry/AIP REST APIs for broader platform operations.
- Authentication authority is the intersection of OAuth scope, Developer Console restrictions, and principal permissions.
- Generated OSDK versions can change call syntax; migration guides are part of the upgrade contract.

## Authentication

Inject an approved token provider or OAuth client into the boundary; never accept a raw long-lived token as ordinary configuration. Log grant/principal identifiers and request IDs where permitted, but never bearer tokens, client secrets, object values, or protected payloads.

## Instructions

1. Write a decision record choosing OSDK or Platform SDK and list the exact required resources or operations.

2. Expose one client boundary that owns token acquisition, deadlines, request correlation, retry classification, and telemetry.

3. Implement deterministic pagination and property selection; return continuation state rather than silently loading every page.

4. Keep generated object, Action, and Function definitions visible to callers and validate Actions before approved execution.

5. Add contract tests for auth denial, restrictions, page continuation, `429`/`503`, non-retryable errors, validation failures, and SDK upgrades.

## Tool Discipline

- Use **Glob** to locate candidate repositories, manifests, configurations, and evidence without widening scope.
- Use **Grep** to find relevant identifiers, declarations, permissions, errors, and stale claims.
- Use **Read** to inspect the smallest required files and authoritative evidence.
- Use **Write** only for a new approved local draft, test, manifest, or evidence artifact.
- Use **Edit** only for a bounded approved change whose rollback is known.
- Do not use file tools as a substitute for authenticated Foundry operations or owner approval.

## Approval Boundaries

Application and platform owners approve the selected API surface; security owners approve token handling; data owners approve returned properties and writeback. Shared-client abstraction does not authorize new endpoints.

## Output

An SDK decision, pinned dependencies, typed client boundary, auth provider, pagination/retry policy, generated-contract usage, tests, telemetry/redaction rules, and upgrade procedure.

## Error Handling

| Condition | Response |
|---|---|
| A wrapper accepts arbitrary endpoint paths | Replace it with typed/generated operations or an explicitly reviewed Platform API surface. |
| A helper loads all pages | Return bounded pages or stream with cancellation and total-work limits. |
| A write is retried automatically | Require documented idempotency or reconciliation before retry. |
| Generated definitions change | Treat it as a contract migration and update tests plus call sites together. |

## Examples

### Example 1

Build a TypeScript OSDK client boundary that accepts a token provider, requests selected properties, returns continuation state, preserves generated Action validation, and emits redacted request metrics.

### Example 2

Build a Python Platform SDK service for one approved API group with Client Credentials auth, bounded pagination, retry only for transient responses, and request-ID capture.

## Validation

- SDK choice and Developer Console restrictions match the required surface.
- All dependencies and generated packages are pinned.
- Pagination, deadlines, cancellation, retries, and idempotency are tested.
- Logs and errors contain no secrets or protected payloads.
- Upgrade tests prove the exact new generated or Platform SDK contract.

## Resources

- [Official documentation and contract notes](references/official-docs.md)
- Re-check the dated contract before any live operation.
- Treat unresolved or changed vendor behavior as a stop condition.
