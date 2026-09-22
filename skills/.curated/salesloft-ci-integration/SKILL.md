---
name: salesloft-ci-integration
description: >-
  Gate Salesloft integration changes with offline contract fixtures and an optional fork-safe read-only smoke lane. Use when wiring CI for auth, pagination, errors, rate limits, or webhooks. Trigger with "Salesloft CI", "Salesloft contract tests", or "Salesloft GitHub Actions".
argument-hint: "[repository-path] [ci-provider]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- salesloft
- ci
model: inherit
effort: medium
compatibility: Designed for Claude Code
---
# Salesloft Contract CI

## Overview

This skill keeps pull-request validation deterministic and secretless while retaining a separately authorized live smoke check. It prevents CI from creating people or cadence memberships as a connectivity test.

## Prerequisites

- A repository with a test runner and identified HTTP adapter
- Sanitized success and failure fixtures
- Protected CI environment for any live credential
- Named owner for contract drift and smoke failures

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect workflows, test commands, adapters, and secret references. Use `WebFetch` only for official Salesloft contracts. Use `Write` or `Edit` after confirming the CI file and repository conventions.

## Current Contract

- Offline fixtures cover `data`, list `metadata`, singular `error`, field-keyed `errors`, and rate headers.
- Webhook tests sign exact raw bytes with SHA-1 HMAC and the fixture callback token.
- Untrusted fork workflows receive no Salesloft secret.
- The optional live lane performs one bounded read such as `GET /v2/me` and logs no response body.

## Authentication

Store a least-privilege read credential only in a protected environment. Pin it to a non-production or explicitly approved team and rotate it through the owning Salesloft flow.

## Instructions

1. Map required unit, contract, security, and static checks to CI jobs.
2. Run sanitized fixture tests on every pull request with no external dependency.
3. Assert secret redaction, tenant binding, pagination termination, bounded retries, and raw-body signature behavior.
4. Disable live jobs for fork-originated and untrusted events.
5. Run the live read-only smoke only after protected-environment authorization.
6. Make contract drift and live failures visible without leaking body or credential data.

## Approval Boundaries

Do not expose repository secrets to fork code, print API responses, or perform Salesloft writes from the default CI lane. A new live environment or scope needs owner approval.

## Output

Return workflow paths, trigger matrix, fixture coverage, secret boundary, live-lane guard, commands, results, and unresolved failures.

## Error Handling

| Condition | Response |
|---|---|
| Fork requests secret | Skip the live lane and run fixtures only. |
| Live 401/403 | Fail clearly and rotate or correct scope outside the log. |
| Live 429 | Stop; do not turn CI into a retry storm. |
| Fixture drift | Update contract and consumer together with an official-source receipt. |

## Examples

The example below shows the minimum redacted evidence expected from a successful invocation of this operator workflow.

```text
pr-fixtures=pass; fork-secrets=0; live-smoke=protected; writes=0
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Request and response format](https://developers.salesloft.com/docs/platform/api-basics/request-response-format/)
- [Webhook delivery headers](https://developers.salesloft.com/docs/platform/webhooks/delivery-headers/)
