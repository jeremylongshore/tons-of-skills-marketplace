---
name: algolia-data-handling
description: >-
  Design and audit the data lifecycle for records and user events sent to Algolia. Use when minimizing indexed fields, handling deletion requests, or documenting retention and privacy boundaries. Trigger with "Algolia privacy", "delete Algolia user data", or "index data review".
argument-hint: "[repository-path] [dataset-or-request-id]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- algolia
- privacy
model: inherit
effort: medium
compatibility: Designed for Claude Code
---
# Algolia Data Handling Review

## Overview

This skill maps which data leaves the source system, how it becomes searchable records or events, and how correction and deletion propagate. It does not claim legal compliance; it produces technical evidence for the responsible privacy owner.

## Prerequisites

- A named repository, environment, and Algolia application or index in scope
- The local lockfile and installed client types as implementation authority
- A safe read-only query or explicitly disposable test target
- Current first-party documentation for any provider behavior that affects the change

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect local code, configuration names, tests, and dependency versions. Use `WebFetch` only for current official Algolia documentation. Use `Write` or `Edit` only after identifying the target files, constraints, and verification plan.

## Current Contract

- Index only fields required for retrieval, ranking, filtering, display, or approved analytics.
- Treat `attributesToRetrieve` as response shaping, not as a substitute for excluding sensitive data from records.
- Keep source-system identity mappings so corrections and deletions are reproducible.
- Handle record deletion and Insights user-token deletion as separate surfaces with separate evidence.

## Authentication

Use a restricted backend write key for record changes and the documented authorization for user-data deletion. Never include raw secrets or direct personal identifiers in logs or example events.

## Instructions

1. Inventory record fields, derived attributes, event fields, user tokens, environments, and downstream exports.
2. Classify each field by purpose, sensitivity, source authority, and deletion requirement.
3. Remove unnecessary fields before indexing and test that UI and ranking behavior still work.
4. Implement idempotent correction and deletion paths with request IDs and target indices.
5. Verify absence using bounded lookups and preserve evidence without retaining the deleted value.
6. Document retention ownership, incident escalation, and gaps for privacy or legal review.

## Approval Boundaries

Do not make legal conclusions, bulk-delete records, change retention policy, or expose protected values while verifying a request.

## Output

Return the data-flow map, field inventory, minimization changes, deletion/correction procedure, verification evidence, unresolved provider retention questions, and named policy owner.

## Error Handling

| Condition | Response |
|---|---|
| Identity mapping missing | Stop and reconcile the source identity before deletion. |
| Deletion task incomplete | Retain the task ID and verify state before closing. |
| Event token contains PII | Stop sending it and escalate remediation. |
| Policy answer unavailable | Record the question for the privacy owner or provider. |

## Examples

Use this compact input and expected handoff to calibrate scope and evidence quality.

Input:

```text
request=privacy-123; surfaces=records,events; indices=customer_search
```

Expected handoff:

```text
records=removed-and-verified; events=requested; legal-determination=not-made
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Security best practices](https://www.algolia.com/doc/guides/security/security-best-practices)
- [Delete user token events](https://www.algolia.com/doc/rest-api/insights/delete-user-token)
- [API keys](https://www.algolia.com/doc/guides/security/api-keys)
