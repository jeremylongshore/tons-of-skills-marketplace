---
name: clari-local-dev-loop
description: >-
  Build and test a Clari integration locally with redacted fixtures and a deterministic job simulator. Use when developing without spending quota or exposing customer data. Trigger with: "mock Clari locally", "build Clari fixtures", "test Clari offline".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[surface-contract-and-fixture-set]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - clari
  - local-development
  - fixtures
  - contract-testing
compatibility: 'Requires a local test runner, approved synthetic or irreversibly redacted fixtures, and a pinned provider contract snapshot.'
---

# Clari Offline Contract Development Loop

## Overview

Make offline development the default and live provider calls an explicit integration stage. Model the provider’s authentication headers, job transitions, pagination, error objects, and schema drift without storing secrets or production records.

## Prerequisites

- Chosen Clari surface and pinned contract version or fingerprint
- Synthetic fixtures covering success, empty, partial, and failure responses
- Local secret scanning and test-data classification rules

## Instructions

### Step 1: Define the contract boundary

List endpoints, headers, request fields, response fields, job states, and pagination semantics used by the integration.

### Step 2: Build synthetic fixtures

Create minimal payloads that preserve shapes and identifiers while containing no real people, accounts, calls, forecasts, or deal values.

### Step 3: Simulate state transitions

Make the test server move deterministically through queued, running, completed, aborted, rate-limited, and timed-out paths.

### Step 4: Exercise adapters

Run parser, schema, retry, pagination, idempotency, and redaction tests against the simulator with network access disabled.

### Step 5: Add one gated live smoke test

Use a dedicated non-production identity and the smallest read-only request; skip it unless credentials and explicit integration-test approval are present.

### Step 6: Refresh deliberately

When the provider contract changes, review the diff, update fixtures and assertions together, and retain the old failing fixture as migration evidence.

## Authentication

Offline tests must use obvious dummy values. A gated live test may read credentials from the approved secret manager at runtime, but must never serialize headers or provider payloads into test output.

## Tool Discipline

Use Read and Grep to inspect configuration, provider contracts, fixtures, logs, schemas, and existing tests before proposing a change. Use Write or Edit only for the approved plan, implementation, test, or redacted receipt; do not issue, rotate, revoke, create, update, cancel, delete, export, ingest, or publish provider data without explicit operator approval.

## Output

- Pinned endpoint and schema contract manifest
- Synthetic fixture set with provenance and data-classification receipt
- Offline test report plus separately identified live-smoke result

Return the exact surface, environment, resource or job identifiers, contract fingerprint, evidence, unresolved risks, and final decision without exposing credentials or sensitive customer data.

## Examples

A local export client receives synthetic `SCHEDULED`, `STARTED`, and `DONE` responses, then a 429 and an `ABORTED` job. CI proves bounded retry and redaction without consuming a Clari export.

## Error Handling

| Failure | Response |
| --- | --- |
| Fixture contains real customer data | Quarantine and remove it, rotate any exposed credential, and replace it with generated values. |
| Mock diverges from the provider contract | Pin the current contract fingerprint and add a regression fixture for the observed delta. |
| Live smoke runs unexpectedly | Fail closed unless an explicit environment gate and non-production credential are both present. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Clari Revenue API reference](https://developer.clari.com/default/documentation/external_spec)
- [Clari Copilot API reference](https://api-doc.copilot.clari.com/)
