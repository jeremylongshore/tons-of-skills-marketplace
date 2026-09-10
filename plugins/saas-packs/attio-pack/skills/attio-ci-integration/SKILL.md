---
name: attio-ci-integration
description: >-
  Build a bounded CI contract gate for an Attio integration using fixtures, schema checks, and an optional read-only smoke request. Use when Attio changes need pull-request evidence without mutating CRM data. Trigger with "Attio CI", "test Attio integration", or "Attio pull request gate".
argument-hint: "[repository-path] [test-command]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- attio
- ci
model: inherit
effort: medium
compatibility: Designed for Claude Code
---
# Attio Contract Gate for CI

## Overview

This skill turns an Attio integration change into deterministic pull-request evidence. It separates offline contract tests from an explicitly enabled read-only API smoke test.

## Prerequisites

- A named repository and existing test runner
- Sanitized Attio response fixtures or generated contract fixtures
- A separately scoped CI credential only if a live smoke test is approved
- The endpoint's current required scopes and pagination contract

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect workflows, fixtures, client code, and secret names. Use `WebFetch` only for current official Attio documentation. Use `Write` or `Edit` only after identifying the target files, constraints, and verification plan.

## Current Contract

- Test the `https://api.attio.com/v2` response envelope and application-owned normalization separately.
- Treat pagination as endpoint-specific: some endpoints use `limit` and `offset`; others return `pagination.next_cursor`.
- Keep mutation tests offline unless a dedicated disposable workspace and cleanup plan are approved.
- Never expose an access token in logs, snapshots, test names, or artifacts.

## Authentication

Use a single-workspace access token for one controlled workspace or OAuth for a multi-workspace app. Grant only the endpoint scopes required by the smoke test and pass the token through the CI secret store as a Bearer credential.

## Instructions

1. Inspect the changed endpoints, request methods, scopes, and response shapes.
2. Add fixture tests for success, structured Attio errors, pagination termination, and retry classification.
3. Validate that snapshots redact tokens, record values, webhook secrets, and personal data.
4. Add a disabled-by-default live job that performs only an approved read request such as listing objects.
5. Require explicit environment configuration before that job runs; skip it cleanly on forks.
6. Record the exact test command, fixture revision, and live-smoke disposition in the PR evidence.

## Approval Boundaries

Do not create, update, or delete records from ordinary PR CI. A mutation smoke test requires a named disposable workspace, bounded fixtures, cleanup verification, and repository-owner approval.

## Output

Return the endpoint contract matrix, fixture coverage, redaction result, workflow change, local command result, and live-smoke status.

## Error Handling

| Condition | Response |
|---|---|
| Fork has no secret | Skip only the live job; keep offline tests required. |
| Fixture differs from docs | Confirm the live endpoint and refresh the fixture deliberately. |
| Smoke returns 403 | Check the endpoint's required scopes; do not broaden blindly. |
| Mutation detected | Fail the job and remove the mutating request. |

## Examples

Input:

```text
change=record-query-filter; live-smoke=read-only; fork-policy=skip-secret-job
```

Expected handoff:

```text
fixtures=pass; redaction=pass; live-read=pass; writes=none
```

This result proves the pull-request gate exercised the contract without receiving mutation authority.

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [REST API overview](https://docs.attio.com/rest-api/overview)
- [Authentication](https://docs.attio.com/rest-api/guides/authentication)
- [Pagination](https://docs.attio.com/rest-api/guides/pagination)
