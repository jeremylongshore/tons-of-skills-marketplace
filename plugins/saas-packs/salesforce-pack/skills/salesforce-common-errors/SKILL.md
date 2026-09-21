---
name: salesforce-common-errors
description: 'Analyze Salesforce authorization, permission, schema, validation, locking, limit, async-job, and event-delivery failures from evidence. Use when triaging an integration. Trigger with "diagnose a Salesforce error".'
argument-hint: "[org-alias] [request-or-job-id]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, salesforce, errors, diagnostics, triage]
model: inherit
effort: high
compatibility: Designed for Claude Code; diagnostic reads and log access require the affected org owner and data-handling policy
---
# Salesforce Integration Error Triage

## Overview

Classify the failed layer, preserve request context, and test one evidence-backed hypothesis before proposing a bounded, reversible correction.

## Prerequisites

- Timestamp, environment, principal, operation, request or job ID, and redacted response
- Expected API version, object and field contract, permissions, limits, automation, and recent changes
- Incident, application, Salesforce platform, security, and data owners

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect approved repository and evidence files, `WebFetch` to re-check current first-party Salesforce documentation, and `Write` or `Edit` only for secretless plans, fixtures, configuration, and redacted receipts.

## Current Contract

Salesforce exposes documented HTTP and API errors, but the same symptom can originate from OAuth, permissions, sharing, schema, validation, automation, locks, limits, asynchronous processing, or event state. Diagnose the returned evidence in org context.

## Authentication

Use read-only diagnostic access with the approved principal or a separately authorized support principal. Do not collect tokens, session IDs, passwords, private keys, raw personal data, or broad debug logs.

## Instructions

1. Freeze the first failure timestamp, environment, release, principal, API, request or job ID, payload shape, and retry history.
2. Confirm org status, identity, API support, resource entitlement, and whether other integrations are affected.
3. Classify the layer: transport, OAuth, scope, CRUD or field access, sharing, schema, validation, automation, locking, limit, async job, or event.
4. Correlate the minimum Salesforce response, application trace, limits snapshot, metadata, job result, and recent change evidence.
5. Reproduce with a synthetic or read-only request in the lowest-risk authorized org.
6. Propose one hypothesis-specific correction and define success, stop, rollback, and no-blind-retry rules.
7. Apply only after approval, verify the original invariant, and document prevention and monitoring changes.

## Approval Boundaries

Do not reset credentials, broaden permissions, disable automation, alter records, increase capacity, or replay writes as a diagnostic shortcut.

## Output

Return the incident frame, classified layer, evidence timeline, ruled-out causes, root or leading cause, approved action, verification, and prevention owner.

## Error Handling

| Condition | Response |
|---|---|
| Request ID or first failure is unavailable | State the evidence gap and avoid assigning a definitive cause. |
| Reproduction would expose or mutate production data | Use synthetic fixtures or stop and request an approved sandbox path. |
| Outcome of a prior write is uncertain | Reconcile by stable business key before any retry. |

## Example

A redacted completion receipt might look like this:

```text
incident=SF-204; layer=field-permission; request=redacted; mutation=blocked-before-send; fix=permission-review; verification=pass
```

## Resources

- [REST status codes and errors](https://developer.salesforce.com/docs/platform/api-rest/guide/errorcodes.html)
- [Salesforce Status](https://status.salesforce.com)

## Next Steps

Run the workflow first in the lowest-risk authorized org and preserve its redacted receipt. Schedule a review against the next Salesforce seasonal release and the customer change calendar.
