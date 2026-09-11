---
name: bamboohr-ci-integration
description: >-
  Build CI gates for a BambooHR connector using current OpenAPI contracts,
  synthetic HR fixtures, secret scanning, and an opt-in tenant smoke test. Use
  when adding regression coverage or blocking unsafe releases. Trigger with
  "BambooHR CI", "BambooHR contract tests", or "test BambooHR integration".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<repository-path> [unit|contract|smoke]"
version: 1.5.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, hr, bamboohr, ci, testing]
model: inherit
effort: high
compatibility: Designed for Claude Code
---
# BambooHR CI Contract

## Overview

Create a fail-closed test lane that proves request construction, schema handling,
redaction, retries, and tenant isolation without placing production BambooHR
credentials or employee records in routine CI.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The tenant, identity, and data scope only when approved live work is in scope.
- The current evidence register plus customer-specific permissions and agreements.

## Current Contract

Use the pinned OpenAPI from BambooHR's official SDK repository as the endpoint
and schema authority. Record the upstream commit and review diffs before updating
the pin. Dataset v1 and legacy report deprecations must be regression assertions,
not silently normalized away.

## Authentication

Unit and contract tests use synthetic credentials that can never authenticate.
An optional live smoke job uses a dedicated least-privilege identity in an
approved test tenant, is disabled for forks, and never exposes secrets to pull-
request code or artifacts.

## Instructions

1. Inspect the repository's runtime, test framework, CI provider, generated-code
   policy, and secret-scanning rules.
2. Add synthetic unit tests for tenant validation, auth header creation,
   token-refresh persistence, redaction, error typing, retry boundaries, and
   idempotency decisions.
3. Pin BambooHR's official OpenAPI commit and add contract tests for only the
   operations the application uses. Alert on removed operations, auth changes,
   changed required fields, response/status drift, or new deprecations.
4. Use invented names and values in fixtures. Include adversarial cases for
   cross-tenant IDs, permission-denied fields, oversized pages, webhook replay,
   malformed signatures, and PII-like strings that must be redacted.
5. Make formatting, static analysis, tests, contract diff, secret scan, and
   artifact scan required. Upload only reports proven free of payload data.
6. If a live smoke is justified, make it manually dispatched or protected-
   environment gated, read-only, body-discarding, time-bounded, and non-forked.
7. Fail the release on any required gate; do not convert schema/security failures
   to advisory because BambooHR is temporarily unavailable.

## Tool Discipline

Use Read, Glob, and Grep to inspect existing CI and tests. Use Write/Edit only
for approved workflows, fixtures, and assertions. This skill does not run CI,
create secrets, call a tenant, or change repository settings.

## Approval Boundaries

Require approval before adding a dependency, enabling a live smoke, changing a
required check, uploading artifacts, or granting CI access to a tenant secret.

## Output

Return CI stages and triggers, OpenAPI pin, synthetic fixture policy, required
checks, live-smoke boundary, secret exposure analysis, test results, and rollout
or repository-setting steps still awaiting approval.

## Error Handling

- Official schema changes: stop the update and require a reviewed contract diff.
- Live smoke unavailable: keep offline gates authoritative and report smoke skipped.
- Secret/PII found in artifact: fail, quarantine, and remove the artifact.

## Examples

- "Run BambooHR tests on fork PRs" produces synthetic contract tests only.
- "Put the production API key in Actions" is redirected to a protected test identity.

## Resources

Read [official evidence](references/official-docs.md) before pinning the contract.
