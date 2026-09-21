---
name: procore-sdk-patterns
description: >-
  Design a thin Procore REST client that preserves endpoint-specific versions, company routing, pagination links, errors, and rate headers. Use when building or reviewing a shared HTTP adapter instead of copying ad hoc requests. Trigger with: "build a Procore client", "review Procore SDK patterns", "standardize Procore API calls".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[language-and-endpoint-set]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - procore
  - rest-client
  - reliability
compatibility: 'Requires an HTTP client with access to documented Procore REST endpoints and a caller-supplied OAuth token provider.'
---

# Procore Contract-Preserving REST Client

## Overview

Keep the client transport-focused and endpoint versions explicit. Procore resources use multiple REST versions, endpoint-specific page limits, company routing requirements, and actionable response headers that a generic JSON wrapper must not erase.

## Prerequisites

- Enumerated public endpoints and their current reference versions
- Token-provider interface that never exposes client secrets to callers
- Typed error, pagination, rate-budget, and redaction contracts

## Instructions

### Step 1: Model requests explicitly

Represent HTTP method, full documented route, API version, company ID, project ID, query parameters, and body separately. Reject private or guessed routes.

### Step 2: Centralize safe headers

Add the Bearer token at dispatch time. Carry `Procore-Company-Id` from explicit request context where required, and never infer company routing from a cached payload.

### Step 3: Preserve response metadata

Return status, parsed body, request correlation data, `Link`, `Total`, `Per-Page`, `X-Rate-Limit-*`, and `Retry-After` to higher layers.

### Step 4: Bound retries

Retry only safe reads or mutations with a proven idempotency design. Honor reset or retry headers, add jitter, cap attempts, and surface the final provider response.

### Step 5: Test endpoint adapters

Give each resource adapter contract fixtures for success, pagination, permission denial, validation errors, throttling, and server failure. Keep business workflows outside the transport.

## Authentication

The client receives OAuth 2.0 Bearer tokens from an external token provider and injects them only at request dispatch. It must not accept client secrets as ordinary endpoint parameters or log authorization headers.

## Tool Discipline

Use Read and Grep to inspect existing transports, endpoint references, and call sites. Use Write or Edit only for the approved client, adapter, tests, or receipt; do not silently rewrite business workflows or provider data.

## Output

- Typed transport and endpoint adapter boundary
- Pagination, throttling, error, and redaction tests
- Endpoint-version inventory and upgrade ownership

Return which response contracts are preserved and which endpoints remain outside the client.

## Examples

A submittals adapter selects the documented submittals version explicitly and returns Link-header pagination to the caller. The shared transport adds routing and auth headers, but it does not pretend all resources share that version or page size.

## Error Handling

| Failure | Response |
| --- | --- |
| Undocumented route requested | Reject locally and require a public API reference. |
| Company context missing | Fail before dispatch when the endpoint requires company routing. |
| 429 or 503 response | Honor provider timing headers, enqueue work, and retry only within the bounded policy. |
| Ambiguous mutation outcome | Stop automatic retry and reconcile the resource before another write. |

## Resources

- [First-party source notes](references/official-docs.md)
- [REST API overview](https://developers.procore.com/documentation/rest-api-overview)
- [Pagination](https://developers.procore.com/documentation/pagination)
- [Rate limiting](https://developers.procore.com/documentation/rate-limiting)
