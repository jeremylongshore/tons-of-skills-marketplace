---
name: salesforce-sdk-patterns
description: 'Build a version-negotiated Salesforce adapter around the customer-selected CLI or client library with typed boundaries and contract tests. Use when standardizing application access. Trigger with "design a Salesforce adapter".'
argument-hint: "[repository] [adapter-path]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, salesforce, adapter, sdk, typescript]
model: inherit
effort: high
compatibility: Designed for Claude Code; dependency changes and live API probes require application owner and Salesforce admin approval
---
# Salesforce Typed Adapter and Client-Library Boundary

## Overview

Contain library churn and org-specific schema behind a small adapter whose types, API version, permissions, retries, and evidence are explicit.

## Prerequisites

- Repository, runtime, supported environments, and selected Salesforce library or CLI
- Current dependency lock, org schema evidence, API support policy, and error samples
- Application, Salesforce platform, security, and data owners

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect approved repository and evidence files, `WebFetch` to re-check current first-party Salesforce documentation, and `Write` or `Edit` only for secretless plans, fixtures, configuration, and redacted receipts.

## Current Contract

Salesforce publishes versioned API contracts, while third-party client libraries have independent release and support policies. Object and field shapes remain customer-specific, so generated or handwritten types must be tied to dated metadata evidence.

## Authentication

Accept an authenticated client or secret reference from the approved authorization layer. The adapter must not invent a password fallback, persist tokens, broaden scopes, or choose a production org implicitly.

## Instructions

1. Inventory direct Salesforce calls, library versions, API versions, objects, fields, mutations, retries, and error handling.
2. Define a narrow adapter interface for identity, metadata discovery, reads, bounded writes, async jobs, and limits.
3. Bind types to dated object metadata or a governed schema snapshot and label nullable, encrypted, formula, and inaccessible fields.
4. Centralize pagination, request IDs, timeouts, idempotency keys or external IDs, error normalization, and redaction.
5. Add contract fixtures for success, partial failure, token expiry, permission denial, schema drift, limits, and timeouts.
6. Test the adapter without a live org, then run approved read-only and sandbox mutation probes.
7. Migrate callers incrementally and retain a reversible compatibility boundary until evidence is complete.

## Approval Boundaries

Do not upgrade dependencies, change API versions, regenerate broad schemas, or perform live writes without code owner, platform owner, and data owner approval.

## Output

Return the adapter contract, dependency and API matrix, schema provenance, fixture coverage, migration plan, live probe receipt, and rollback boundary.

## Error Handling

| Condition | Response |
|---|---|
| Library behavior differs from Salesforce documentation | Pin the discrepancy, reproduce at the raw API boundary, and escalate upstream before broad rollout. |
| Schema snapshot is stale | Block generated-type use until metadata is refreshed and reviewed. |
| Caller bypasses the adapter | Fail the policy check or document a time-bounded exception with an owner. |

## Example

A redacted completion receipt might look like this:

```text
adapter=SalesforceGateway; api=discovered-supported; schema=dated; fixtures=8; sandbox-write=approved-pass; bypasses=0
```

## Resources

- [Salesforce REST API EOL policy](https://developer.salesforce.com/docs/platform/api-rest/guide/api-rest-eol.html)
- [REST API resources](https://developer.salesforce.com/docs/platform/api-rest/guide/resources-list.html)

## Next Steps

Run the workflow first in the lowest-risk authorized org and preserve its redacted receipt. Schedule a review against the next Salesforce seasonal release and the customer change calendar.
