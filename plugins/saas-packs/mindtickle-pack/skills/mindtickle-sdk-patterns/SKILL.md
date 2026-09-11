---
name: mindtickle-sdk-patterns
description: 'Build a typed, tenant-scoped Mindtickle adapter from customer-authorized API artifacts without assuming a public SDK. Use when implementing Content, User, or Reporting API access. Trigger with "design a Mindtickle adapter".'
argument-hint: "[contract-path] [language]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, mindtickle, api, adapter, contract-testing]
model: inherit
effort: high
compatibility: Designed for Claude Code; API artifacts and credentials must be supplied by an authorized customer or Mindtickle representative
---
# Contract-First Mindtickle Adapter Patterns

## Overview

Turn an authorized tenant API contract into a narrow adapter with explicit operations, validation, retries, tenancy, and evidence—without fabricating an SDK or route.

## Prerequisites

- A versioned tenant API artifact with provenance, permitted operations, and data classification
- Confirmed authentication, environment, capacity, support, and change-notification contracts
- Test fixtures that contain no production secrets or learner PII

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect contract artifacts and code, `WebFetch` only for authorized current documentation, and `Write` or `Edit` for adapter code, fixtures, and redacted receipts.

## Current Contract

Public Mindtickle material confirms REST-based Content, User, and Reporting APIs but does not define a universal public SDK, base URL, route set, or credential header. Treat the tenant artifact as the executable authority and record its digest and expiry.

## Authentication

Inject credentials through the approved runtime secret provider. Bind configuration to one tenant and environment, redact request logs, and reject startup when tenant, host, or credential provenance is ambiguous.

## Instructions

1. Inventory only documented operations needed for the business workflow and classify each read, write, idempotency, and privacy property.
2. Freeze the source artifact digest, tenant, environment, auth scheme, schemas, pagination, errors, and capacity signals.
3. Generate or handwrite internal transport types behind a product-specific interface; never leak vendor payloads into domain logic.
4. Validate requests and responses at the boundary and reject undocumented fields or status assumptions.
5. Implement bounded retries only for documented transient conditions, with idempotency or reconciliation for writes.
6. Add fixtures for success, authorization failure, validation failure, pagination, throttling signals, timeout ambiguity, and schema drift.
7. Produce a mutation preview and require approval before the first tenant write.
8. Capture contract digest, test results, deployed adapter version, and rollback compatibility.

## Approval Boundaries

Do not reverse engineer tenant traffic, scrape the authenticated UI, publish confidential API artifacts, add undocumented operations, or run writes without resource-owner approval.

## Output

Return the contract inventory and digest, adapter boundary, auth and tenant controls, fixture coverage, retry/reconciliation policy, mutation preview, and rollback plan.

## Error Handling

| Condition | Response |
|---|---|
| Runtime response violates the contract | Quarantine the payload, stop writes, and open a contract clarification. |
| Write times out ambiguously | Reconcile through a documented read or support receipt before retrying. |
| Only marketing documentation exists | Produce an interface proposal and vendor questions; do not implement network calls. |

## Example

```text
contract-sha256=...; tenant-bound=true; operations=3-read,1-write; fixtures=7-pass; first-write=approval-required
```

## Resources

- [Mindtickle integrations and API families](https://www.mindtickle.com/platform/integrations/)
- [Professional services scope](https://www.mindtickle.com/legal/professional-services-scope-and-services-description/)

## Next Steps

Wire the frozen contract fixtures into CI and rehearse rollback against the previous adapter version.
