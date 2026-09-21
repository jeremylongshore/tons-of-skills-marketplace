---
name: salesforce-hello-world
description: 'Verify a Salesforce org connection with version discovery, identity evidence, and a read-only resource probe before previewing any mutation. Use when running first connections and smoke tests. Trigger with "test Salesforce safely".'
argument-hint: "[org-alias] [object]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, salesforce, smoke-test, rest-api, discovery]
model: inherit
effort: medium
compatibility: Designed for Claude Code; record creation or update requires object owner approval and a non-production test target
---
# Salesforce Read-Only Capability Proof

## Overview

Prove the selected principal, org, API version, object entitlement, and field visibility before any record mutation is considered.

## Prerequisites

- An authorized non-production org and secret reference
- Expected org identity, principal, object, fields, and business owner
- Current REST API and authorization documentation

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect approved repository and evidence files, `WebFetch` to re-check current first-party Salesforce documentation, and `Write` or `Edit` only for secretless plans, fixtures, configuration, and redacted receipts.

## Current Contract

The REST Versions resource lets a client discover versions instead of hard-coding one. Resources, objects, fields, CRUD, sharing, and limits remain org- and principal-specific.

## Authentication

Use the approved OAuth client and principal from the onboarding decision. Keep access and refresh tokens out of commands, files, prompts, logs, screenshots, and receipts.

## Instructions

1. Record the expected org, environment, principal, My Domain, object, fields, and success criteria.
2. Resolve credentials only through the approved secret mechanism and verify the returned org identity.
3. List supported REST versions and select a supported version allowed by the customer contract.
4. Discover available resources, then inspect object metadata and field accessibility for the intended read.
5. Run one bounded read-only query with non-sensitive fields and an explicit row limit.
6. Preview any proposed create or update with validation, duplicate, automation, ownership, and rollback effects.
7. Return a redacted receipt and request separate approval before executing a mutation.

## Approval Boundaries

Do not create, update, delete, undelete, merge, or expose records during the proof. Any mutation requires object-owner approval and a recoverable test case.

## Output

Return org and principal verification, selected API version, visible resource and field evidence, query result counts, mutation preview, and next approval.

## Error Handling

| Condition | Response |
|---|---|
| Org identity differs from expectation | Stop and revoke or isolate the credential before any further request. |
| Object or field is unavailable | Treat the metadata response as authoritative for this principal and revise the request. |
| Read triggers sensitive-data exposure | Discard the data securely and repeat with minimum non-sensitive fields. |

## Example

A redacted completion receipt might look like this:

```text
org=developer-sandbox; identity=matched; api=discovered-supported; object=Account; fields=minimum; rows=1; mutation=not-run
```

## Resources

- [List REST API versions](https://developer.salesforce.com/docs/platform/api-rest/guide/dome-versions.html)
- [REST API introduction](https://developer.salesforce.com/docs/platform/api-rest/guide/intro-rest.html)

## Next Steps

Run the workflow first in the lowest-risk authorized org and preserve its redacted receipt. Schedule a review against the next Salesforce seasonal release and the customer change calendar.
