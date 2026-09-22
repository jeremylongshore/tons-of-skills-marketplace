---
name: algolia-common-errors
description: >-
  Diagnose Algolia request, credential, index, task, and query failures from concrete evidence. Use when an integration returns 4xx or 5xx responses, stale results, or unexpected empty hits. Trigger with "debug Algolia error", "Algolia 403", or "Algolia search failed".
argument-hint: "[repository-path] [error-or-request-id]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- algolia
- debugging
model: inherit
effort: medium
compatibility: Designed for Claude Code
---
# Algolia Error Triage

## Overview

This skill turns an Algolia symptom into a reproducible diagnosis. It favors the response status, message, request ID, client version, operation, and target index over generic error folklore.

## Prerequisites

- A named repository, environment, and Algolia application or index in scope
- The local lockfile and installed client types as implementation authority
- A safe read-only query or explicitly disposable test target
- Current first-party documentation for any provider behavior that affects the change

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect local code, configuration names, tests, and dependency versions. Use `WebFetch` only for current official Algolia documentation. Use `Write` or `Edit` only after identifying the target files, constraints, and verification plan.

## Current Contract

- A 403 is an authorization fact, not proof that an unrestricted key is required.
- A successful write is asynchronous; compare the returned task ID and wait behavior before calling data stale.
- A 404 can identify a missing index, application, route, or regional endpoint; preserve the full response.
- A 429 must be interpreted from the returned message and current plan or key restrictions, not from a guessed universal quota.

## Authentication

Inspect only redacted key metadata and ACL intent. Never print, paste, or replace a credential with an Admin key merely to make a failing request succeed.

## Instructions

1. Capture the smallest failing call, status, message, request ID, application ID suffix, index name, and package version.
2. Classify the operation as search, indexing, settings, key management, analytics, or events.
3. Compare the operation with the intended key ACLs and index restrictions.
4. Reproduce against a safe test index or read-only query with the same client boundary.
5. Check task completion, index spelling, filters, attributes, and environment routing in that order.
6. Apply one correction, rerun the minimal reproduction, and record before-and-after evidence.

## Approval Boundaries

Do not broaden ACLs, rotate keys, change production settings, or replay writes until the target and failure class are confirmed.

## Output

Return the symptom, evidence, root-cause hypothesis, ruled-out alternatives, minimum fix, verification result, and any remaining uncertainty.

## Error Handling

| Condition | Response |
|---|---|
| 401 or 403 | Verify application/key pairing and required ACL; do not escalate privilege blindly. |
| 404 | Confirm endpoint, application, and exact index name. |
| 429 | Honor the response and measure request pressure before adding bounded retry. |
| Stale result | Wait for the specific task and verify the queried index. |

## Examples

Use this compact input and expected handoff to calibrate scope and evidence quality.

Input:

```text
operation=saveObjects; status=403; index=products_stage
```

Expected handoff:

```text
cause=missing-addObject-ACL; fix=request-scoped-key; admin-key-used=no
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [API keys](https://www.algolia.com/doc/guides/security/api-keys)
- [JavaScript API client](https://www.algolia.com/doc/libraries/javascript)
- [Algolia status](https://status.algolia.com/)
