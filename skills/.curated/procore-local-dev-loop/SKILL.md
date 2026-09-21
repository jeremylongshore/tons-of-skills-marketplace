---
name: procore-local-dev-loop
description: >-
  Build a deterministic Procore integration loop with fixtures, a Developer Sandbox, and explicit mutation cleanup. Use when developing endpoint adapters, reproducing provider failures, or testing pagination and retry logic locally. Trigger with: "set up Procore local development", "test Procore with fixtures", "reproduce a Procore API bug".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[endpoint-or-failure-case]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - procore
  - sandbox
  - testing
compatibility: 'Requires local test tooling and, for provider tests, a Procore Developer Sandbox with sandbox OAuth credentials.'
---

# Procore Deterministic Development Loop

## Overview

Separate fast fixture tests from deliberate provider tests. A Developer Sandbox supplies isolated seed data and separate OAuth credentials, but it is not a production replica and cannot be casually refreshed, so tests must own their records and cleanup.

## Prerequisites

- Endpoint contract and failure case under test
- Sanitized request and response fixtures with stable identifiers
- Developer Sandbox app, sandbox credentials, and a dedicated test project
- Cleanup rule for every test-created Procore record

## Instructions

### Step 1: Define the contract

Capture method, normalized route, required headers, request schema, expected status, pagination metadata, and error shape. Keep provider-generated IDs outside golden assertions.

### Step 2: Build fixture tests

Exercise token expiry, permission denial, hidden-resource 404, validation failure, throttling, and server retry behavior without network access. Assert that secrets and construction payloads are redacted.

### Step 3: Isolate provider tests

Point live tests only at `login-sandbox.procore.com` and `sandbox.procore.com` with sandbox credentials. Refuse production hosts in local and CI test profiles.

### Step 4: Create bounded data

Prefix test artifacts with a run identifier, record every created ID, and clean up in reverse dependency order. Do not assume the Developer Sandbox can be reset.

### Step 5: Reconcile fixtures

When the official endpoint behavior changes, review the API reference and changelog, update the adapter first, then deliberately re-record only sanitized fixtures.

## Authentication

Live sandbox tests use a sandbox OAuth 2.0 Bearer token. Production credentials and tokens are forbidden in the development profile, and recorded fixtures must contain neither credentials nor tokens.

## Tool Discipline

Use Read and Grep to inspect code, fixtures, and endpoint documentation. Use Write or Edit only for the approved adapter, fixture, test, cleanup manifest, or receipt; provider mutations require a sandbox-only guard and cleanup path.

## Output

- Endpoint contract and sanitized fixture set
- Offline test results plus bounded sandbox-test results
- Created-resource and cleanup receipt

Return fixture provenance, sandbox identifiers, assertions, cleanup outcome, and any documented provider drift.

## Examples

An RFI adapter test replays sanitized 401, 403, 404, 422, and 429 fixtures offline. A separate sandbox case creates one prefixed RFI, verifies its response shape, records its ID, and removes it during teardown.

## Error Handling

| Failure | Response |
| --- | --- |
| Production host detected | Fail closed before token acquisition or request construction. |
| Sandbox fixture drifts | Compare the current endpoint reference and changelog before updating expectations. |
| Cleanup fails | Preserve the exact resource IDs and assign a sandbox cleanup owner. |
| Secret appears in fixture | Quarantine the artifact, rotate if necessary, and replace it with a synthetic value. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Procore sandboxes](https://developers.procore.com/documentation/development-environments)
- [Troubleshooting](https://developers.procore.com/documentation/troubleshooting)
- [REST API lifecycle](https://developers.procore.com/documentation/rest-api-lifecycle)
