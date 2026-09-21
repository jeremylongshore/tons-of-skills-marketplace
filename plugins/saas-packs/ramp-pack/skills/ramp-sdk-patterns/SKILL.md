---
name: ramp-sdk-patterns
description: >-
  Build a small typed Ramp Developer API adapter with secure token management, pagination, structured errors, rate control, idempotency, and schema drift checks. Use when replacing scattered raw requests in application code. Trigger with "Ramp API client" or "Ramp SDK patterns".
allowed-tools: Read,Glob,Grep,Write,Edit
version: 2.0.0
argument-hint: "[integration-or-environment]"
model: inherit
effort: high
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Requires current Ramp Developer API documentation and approved access for any live financial, card, identity, accounting, application, or configuration change
tags: [saas, ramp, client, api, reliability]
---
# Typed Ramp API Client Patterns

## Overview

Generate or handcraft only the surface the application needs. Wrap transport concerns once, expose business-safe methods, and keep the official OpenAPI checksum next to the generated or reviewed client.

## Prerequisites

- Identify the Ramp application, environment, business entities, affected data and workflows, accountable owner, and rollback boundary.
- Read `references/official-docs.md` and re-check endpoint schemas, scopes, limits, and support status before a live operation.
- Use synthetic fixtures or Ramp sandbox until production access and business effects are explicitly approved.
- Prepare approved secret storage and a sanitized evidence location.

## Current Contract

- Ramp publishes an OpenAPI schema and plain-text current documentation; client code must track the exact reviewed contract.
- The API base uses `/developer/v1`; token acquisition, resource paths, and special surfaces such as Vault may use distinct hosts or controls.
- List pagination, monetary values, errors, idempotency, and deferred tasks are endpoint-specific.
- Unknown fields are not uniformly handled, so outgoing requests need schema validation.

## Authentication

Centralize the approved OAuth grant and server-side bearer-token lifecycle in the adapter. Cache tokens only in protected memory or an approved secret mechanism, refresh before expiry, and bind every client instance to one explicit Ramp environment and minimum scope set.

## Instructions

1. Inventory required endpoint/verb/scope pairs and select the smallest generated or handwritten client surface.

2. Centralize environment allowlists, token caching before expiry, redacted headers, timeouts, shared rate budget, trace-ID capture, and structured `error_v2` parsing.

3. Implement reusable cursor iteration that yields committed pages and preserves empty-page, continuation, cancellation, and resume behavior.

4. Require typed integer monetary values with currency, endpoint-specific idempotency keys for writes, and explicit deferred-task or reconciliation results.

5. Pin the OpenAPI checksum, test success and failure fixtures, and produce a reviewed diff before regenerating or exposing new operations.

## Tool Discipline

- Use **Glob** to locate candidate code, manifests, fixtures, and evidence without widening scope.
- Use **Grep** to find relevant endpoints, fields, permissions, identifiers, errors, and stale assumptions.
- Use **Read** to inspect the smallest required local files and authoritative evidence.
- Use **Write** only for a new approved local draft, test, configuration, or evidence artifact.
- Use **Edit** only for a bounded approved change with a known rollback.
- Local file tools do not authorize a Ramp operation or replace owner approval.

## Approval Boundaries

Application owners approve the client surface; security approves credential handling; finance/data owners approve exported write methods.

## Output

A minimal client interface, endpoint/scope manifest, contract checksum, transport policy, pagination and money types, retry/idempotency matrix, and deterministic tests.

## Error Handling

| Condition | Response |
|---|---|
| Generated code exposes every endpoint | Wrap and export only approved capabilities; generation is not authorization. |
| Token refresh stampedes | Use single-flight acquisition with early refresh and never log the token. |
| A retry duplicates a write | Reconcile by idempotency/source identifier and redesign the method to return an explicit commit state. |

## Examples

### Example 1

Create a read-only transaction iterator that resumes from the last durably committed cursor and surfaces Ramp trace IDs.

### Example 2

Wrap accounting sync submission so a caller must provide an idempotency key and receive a typed success/failure receipt.

## Validation

- Every exported method maps to a reviewed endpoint, scope, data owner, and error contract.
- Hosts and tokens cannot cross environments.
- Pagination, money, retries, timeouts, idempotency, and deferred states have tests.
- Contract drift fails visibly and never regenerates silently.

## Resources

- [Official documentation and contract notes](references/official-docs.md)
- Re-check the dated contract and current OpenAPI schema before any live request.
- Treat unresolved vendor behavior, authority, or financial state as a stop condition.
