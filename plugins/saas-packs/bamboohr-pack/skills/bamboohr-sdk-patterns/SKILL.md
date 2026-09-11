---
name: bamboohr-sdk-patterns
description: >-
  Select and wrap BambooHR's official Python or PHP SDK, or a narrow direct HTTP
  adapter, with tenant isolation and typed errors. Use when implementing a
  reusable client or replacing an unverified community package. Trigger with
  "BambooHR SDK", "BambooHR client", or "BambooHR integration patterns".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<python|php|http> <integration-path>"
version: 1.5.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, hr, bamboohr, sdk, architecture]
model: inherit
effort: high
compatibility: Designed for Claude Code
---
# BambooHR SDK and Client Patterns

## Overview

Build a small application-owned adapter around a verified BambooHR transport.
Keep BambooHR models and error details at the adapter boundary so upstream SDK
regeneration or endpoint migration does not ripple through business logic.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The tenant, identity, and data scope only when approved live work is in scope.
- The current evidence register plus customer-specific permissions and agreements.

## Current Contract

- `BambooHR/bhr-api-python` and `BambooHR/bhr-api-php` are official repositories.
- `bamboohr/api` 2.0.1 is published on Packagist.
- The Python repository documents `bamboohr-sdk` 1.0.0, but public PyPI did not
  expose that distribution on 2026-09-11 and the repository had no tag or
  release. Treat it as source-visible, not registry-proven.
- No official npm BambooHR SDK was found; a TypeScript integration should use a
  narrow HTTP adapter rather than claim an official package.

## Authentication

Expose constructors for OAuth and API-key identities, not raw headers. Bind each
client to one validated tenant subdomain. If OAuth refresh is enabled, persist
rotated tokens through the caller-owned callback; the Python SDK does not store
them across restarts.

## Instructions

1. Inventory language, package lock, existing HTTP client, and supported auth
   modes with Read, Glob, and Grep.
2. Verify the selected package in its public registry at implementation time.
   For an approved source install, pin an immutable commit and record its hash,
   license, provenance, and update owner.
3. Define an adapter with explicit operations such as `getCompanyInformation`,
   `listEmployees`, and `queryDatasetV2`; do not expose an arbitrary URL method
   to untrusted callers.
4. Normalize errors into status, operation, retryability, request ID, and a
   redacted summary. Preserve the original exception only in protected logs.
5. Keep tenant, authentication, timeout, retry budget, and user-agent immutable
   for the life of a client instance.
6. Test request construction, tenant rejection, secret redaction, typed error
   mapping, token-refresh persistence, and response-shape drift with fixtures.

## Tool Discipline

Use Read, Glob, and Grep to establish the project's language and package state.
Use Write/Edit only for the approved adapter and tests. This skill does not
authorize package installation, remote registry mutation, or live tenant calls.

## Approval Boundaries

Require approval before adding a dependency, using an unreleased commit, making
a tenant request, broadening OAuth scopes, or enabling debug logging around HR
data. Never silently fall back from OAuth to an API key.

## Output

Return the chosen transport and exact version/commit, registry verification,
adapter operations, auth and tenant boundary, error taxonomy, test results, and
remaining publication or live-test approvals.

## Error Handling

- Package absent from registry: stop; offer pinned-source review or direct HTTP.
- SDK method absent for a documented endpoint: use the generated manual client
  only after checking the current OpenAPI, or implement a bounded HTTP adapter.
- Response schema drift: quarantine the payload and fail the contract test.

## Examples

- "Install the official Python SDK" first proves public registry availability.
- "Use an npm BambooHR SDK" reports that no official package was verified and
  proposes a three-operation HTTP adapter.

## Resources

Read [official evidence](references/official-docs.md) before choosing a transport.
