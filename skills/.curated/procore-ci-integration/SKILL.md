---
name: procore-ci-integration
description: >-
  Gate Procore adapters in CI with offline contract fixtures, host and secret guards, pagination tests, retry safety, and optional bounded sandbox checks. Use when adding endpoints or preventing integration regressions. Trigger with: "test Procore in CI", "add Procore contract tests", "gate a Procore adapter".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[adapter-and-ci-system]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - procore
  - continuous-integration
  - contract-testing
compatibility: 'Requires a CI runner, sanitized fixtures, and optional isolated Procore Developer Sandbox credentials for protected provider tests.'
---

# Procore Adapter CI Contract

## Overview

Make offline fixtures the default CI denominator and isolate credentialed sandbox tests behind explicit protection. The gate should detect endpoint drift, first-page-only bugs, unsafe retries, tenant-routing loss, and secret leakage without mutating production.

## Prerequisites

- Resource adapter inventory and current public endpoint references
- Sanitized success and failure fixtures with provenance
- Protected sandbox credential source and cleanup owner for optional live tests

## Instructions

### Step 1: Define contract cases

Cover required headers, request and response shapes, API version, pagination links, 401, 403, hidden 404, 422, 429, 503, and timeout behavior for each changed adapter.

### Step 2: Add safety guards

Fail if a test selects production hosts, lacks explicit company context where required, prints Authorization data, or enables provider mutations outside a protected sandbox job.

### Step 3: Test pagination and retries

Verify Link navigation reaches every fixture page and stops without `next`. Assert reset and retry headers control timing and writes are not replayed without reconciliation.

### Step 4: Validate fixtures

Grep for secret patterns, customer identifiers, time-sensitive assertions, and undocumented routes. Require reviewed provenance when a fixture changes.

### Step 5: Run bounded provider checks

Use a Developer Sandbox only when protected credentials are present. Create uniquely prefixed test data, record IDs, and clean it up; otherwise report the provider lane as skipped.

### Step 6: Emit a gate receipt

Record release identifier, adapter set, fixture hashes, offline results, provider-lane status, cleanup result, and known gaps.

## Authentication

Offline tests use synthetic tokens only. Optional provider checks obtain a sandbox OAuth 2.0 Bearer token from protected CI secrets, never expose it, and categorically reject production credentials and hosts.

## Tool Discipline

Use Read and Grep to inspect adapters, fixtures, workflows, and logs. Use Write or Edit only for the approved test, fixture, CI configuration, or receipt; do not add unconditional network or production mutation steps.

## Output

- Offline endpoint and failure contract gate
- Secret, host, routing, pagination, and retry safety results
- Optional sandbox-test and cleanup receipt

Return deterministic pass or fail, explicit skips, artifact hashes, and the exact adapter that regressed.

## Examples

A pull request changing the RFI adapter replays sanitized success and error fixtures, proves Link pagination, and rejects production hosts. A protected nightly sandbox job creates one prefixed record and confirms cleanup without affecting required offline CI.

## Error Handling

| Failure | Response |
| --- | --- |
| Sandbox credential absent | Skip the optional provider lane explicitly; keep offline gates required. |
| Fixture contains sensitive data | Quarantine and replace it before CI artifacts are uploaded. |
| Cleanup fails | Fail the provider lane and assign the recorded IDs to a sandbox cleanup owner. |
| Live reference changed | Review adapter and fixture together; do not auto-accept provider drift. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Procore sandboxes](https://developers.procore.com/documentation/development-environments)
- [Error code reference](https://developers.procore.com/documentation/error-reference)
- [API lifecycle](https://developers.procore.com/documentation/rest-api-lifecycle)
