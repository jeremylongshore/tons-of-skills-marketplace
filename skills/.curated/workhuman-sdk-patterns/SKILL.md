---
name: workhuman-sdk-patterns
description: 'Design a typed Workhuman integration adapter from customer-authorized API or connector contracts without assuming a public SDK. Use when creating reusable client boundaries. Trigger with "design a Workhuman adapter".'
argument-hint: "[contract-path] [language]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.4.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, workhuman, adapter, contracts, sdk]
model: inherit
effort: high
compatibility: Designed for Claude Code; generated clients and production calls require customer-authorized contracts and credentials
---
# Workhuman Contract-Driven Adapter Patterns

## Overview

Create a narrow, testable boundary around documented tenant capabilities while keeping vendor transport, business policy, and systems of record separate.

## Prerequisites

- A current customer-authorized API schema, managed-connector mapping, or integration specification
- Defined operations, data classifications, owners, and compatibility window
- Synthetic fixtures for all supported results and failures

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect contracts and consumers, `WebFetch` for current first-party context, and `Write` or `Edit` for types, adapter code, tests, and redacted receipts.

## Current Contract

Workhuman describes an open API but does not publish a universal public SDK or stable route catalogue on the cited public pages. Generate or hand-build only from customer-authorized artifacts and pin the artifact identity.

## Authentication

Inject the documented authorization provider at runtime. Keep secret acquisition outside the adapter, prevent cross-tenant reuse, and redact authorization and workforce data from errors.

## Instructions

1. Inventory required operations and map each to an exact authorized contract section and owning system.
2. Pin the schema or mapping fingerprint, environment, tenant, acquisition date, and compatibility promise.
3. Generate types when the artifact supports it; otherwise define minimal request and response types without speculative fields.
4. Separate transport, authentication, serialization, retry, idempotency, policy, and business orchestration.
5. Preserve vendor status and safe correlation fields in a normalized error union.
6. Validate response envelopes, tolerate documented optional fields, and reject unsafe type coercion.
7. Test duplicates, partial application, timeouts, throttling, revoked authorization, schema drift, and retry eligibility.
8. Expose only the operations required by the approved workflow and document deprecation ownership.

## Approval Boundaries

Do not add undocumented operations, generate from untrusted schemas, publish customer artifacts, or execute tenant writes while building the adapter.

## Output

Return the pinned contract identity, operation map, typed boundary, auth injection point, error model, fixture coverage, compatibility policy, and unresolved fields.

## Error Handling

| Condition | Response |
|---|---|
| Contract has no stable version | Pin its digest and retrieval date and require explicit review before regeneration. |
| Response contains an unknown field | Preserve it in safe telemetry and assess compatibility; do not silently remap meaning. |
| Write outcome is ambiguous | Stop automatic retry until idempotency or reconciliation proves safety. |

## Example

A redacted completion receipt might look like this:

```text
artifact=customer-openapi@sha256:...; operations=3; auth=injected; fixtures=14; unknown-fields=tolerated; ambiguous-writes=blocked
```

## Resources

- [Workhuman integrations and open API](https://www.workhuman.com/capabilities/integrations/)
- [Workhuman security and privacy](https://www.workhuman.com/why-workhuman/security-and-privacy/)

## Next Steps

Use the adapter in the local and CI lanes before proposing a canary tenant deployment.
