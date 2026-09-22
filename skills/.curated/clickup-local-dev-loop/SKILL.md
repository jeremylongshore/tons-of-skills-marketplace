---
name: clickup-local-dev-loop
description: >-
  Develop ClickUp adapters with a fake transport, schema fixtures, deterministic clocks, and an opt-in bounded live probe. Use when iterating without mutating a real Workspace. Trigger with "ClickUp local dev", "mock ClickUp API", or "ClickUp fixtures".
argument-hint: "[repository-path] [offline|live-probe]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- clickup
- development
model: inherit
effort: high
compatibility: Designed for Claude Code; ordinary tests are offline and the live probe needs a non-production credential
---
# ClickUp Deterministic Local Development

## Overview

Keep the fast loop offline while preserving exact provider shapes and a deliberate path to detect real API drift.

## Prerequisites

- A transport interface around all ClickUp HTTP calls
- Sanitized fixtures derived from documented v2/v3 schemas, including nulls and errors
- A deterministic clock, fake queue, and optional isolated Workspace for a live read

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect the repository, adapters, configuration names, tests, and evidence. Use `WebFetch` only for current official ClickUp documentation. Use `Write` or `Edit` after confirming the target file, Workspace boundary, and requested mode.

## Current Contract

- Fixtures preserve string/number/null differences in task and webhook payloads.
- Separate base paths and schemas for v2 and selected v3 operations.
- Mock 429 headers, zero-based task pages, comment cursors, auth codes, and webhook delivery retries.
- No ordinary unit test reads a developer token or creates a ClickUp object.

## Authentication

Use a personal token only for accountable individual/testing work or OAuth Authorization Code for a user-facing integration. Inject the token server-side through a governed secret reference, send it in `Authorization`, verify authorized Workspace IDs, and never print the token, OAuth client secret, or webhook secret.

## Instructions

1. Inventory direct HTTP calls and route them through an injectable transport.
2. Create fixtures for identity, Workspace, tasks, pages, Custom Fields, webhooks, errors, and rate headers.
3. Freeze time and IDs; make request order, retry jitter, and queue outcomes deterministic.
4. Test raw-body HMAC verification, redaction, Workspace guards, and partial-write recovery.
5. Add an explicit live-probe command limited to read-only identity/Workspace calls.
6. Run offline tests by default and record any provider drift found by the live probe.

## Approval Boundaries

Do not record production responses, use personal work data as fixtures, or enable writes in the default local/test path.

## Output

Return fixture provenance, offline coverage, direct-call violations, deterministic test result, live-probe result, and drift. Distinguish simulated success from provider-confirmed evidence.

## Error Handling

| Condition | Response |
|---|---|
| Fixture contains personal or task content | Delete/quarantine it and replace with synthetic data. |
| Direct HTTP call bypasses transport | Fail the test and refactor the boundary. |
| Live credential is absent | Skip the probe without weakening offline tests. |
| Live response drifts | Update contracts only after official-source review. |

## Examples

The example below is a redacted operator receipt; it contains no task text, member data, credential, or webhook secret.

```text
mode=offline; fixtures=14; network-calls=0; clocks=frozen; hmac-tests=pass; live-probe=skipped
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [OpenAPI specifications](https://developer.clickup.com/docs/open-api-spec)
- [Authentication](https://developer.clickup.com/docs/authentication)
- [Rate limits](https://developer.clickup.com/docs/rate-limits)
