---
name: clari-ci-integration
description: >-
  Validate a Clari integration in CI with offline OpenAPI-derived contracts, synthetic job lifecycles, schema drift checks, and secret scanning. Use when adding release gates. Trigger with: "add Clari CI", "test the Clari contract", "gate a Clari release".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[client-package-and-contract-snapshot]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - clari
  - ci
  - contract-testing
  - quality-gates
compatibility: 'Requires a CI runner, synthetic fixtures, a pinned first-party contract fingerprint, and a separately gated non-production credential for optional smoke tests.'
---

# Clari Contract Validation in CI

## Overview

Keep the required CI lane deterministic and credential-free. Test only owned endpoints and transformations offline, while running any provider-connected smoke test as an explicit, non-blocking or separately authorized environment gate.

## Prerequisites

- Pinned endpoint and schema manifest for each used surface
- Synthetic fixtures for success, empty, throttled, aborted, malformed, and drifted responses
- Secret scanner and artifact-retention policy

## Instructions

### Step 1: Pin the contract evidence

Record provider URL, contract version, content fingerprint, extraction date, and the subset of operations the integration owns.

### Step 2: Test request construction

Assert exact hosts, methods, paths, headers by name, payload schemas, timeouts, and prohibited mutation defaults.

### Step 3: Test lifecycle behavior

Simulate queue, poll, terminal result, cancellation, pagination, 429, timeout, and restart from durable state.

### Step 4: Test data gates

Assert schema validation, reconciliation, unknown-field quarantine, redaction, and atomic publication behavior.

### Step 5: Scan outputs

Fail on credential patterns, real customer fixtures, unredacted headers, or sensitive payloads in logs and snapshots.

### Step 6: Separate live smoke testing

If authorized, run one minimal non-production read with a short timeout and store only a redacted receipt outside the deterministic required lane.

## Authentication

Required CI must use dummy credentials and no provider network access. Any live smoke credential comes from protected environment secrets, is restricted to non-production reads, and is never available to forked or untrusted jobs.

## Tool Discipline

Use Read and Grep to inspect configuration, provider contracts, fixtures, logs, schemas, and existing tests before proposing a change. Use Write or Edit only for the approved plan, implementation, test, or redacted receipt; do not issue, rotate, revoke, create, update, cancel, delete, export, ingest, or publish provider data without explicit operator approval.

## Output

- Deterministic contract-test and schema-diff reports
- Secret and test-data hygiene results
- Optional live-smoke receipt clearly separated from required CI

Return the exact surface, environment, resource or job identifiers, contract fingerprint, evidence, unresolved risks, and final decision without exposing credentials or sensitive customer data.

## Examples

A pull request proves forecast job-state handling and warehouse rollback entirely from synthetic fixtures. A protected post-merge job performs one `/admin/limits` read and publishes only status and timestamp.

## Error Handling

| Failure | Response |
| --- | --- |
| Contract fingerprint changes | Fail the drift gate until a human reviews endpoints, schemas, limits, and migration impact. |
| A secret-like value is detected | Block artifacts and rotate the credential if it could be real. |
| Live smoke is unavailable | Keep deterministic CI authoritative and report the environment check separately. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Clari Revenue API reference](https://developer.clari.com/default/documentation/external_spec)
- [Clari Copilot API reference](https://api-doc.copilot.clari.com/)
