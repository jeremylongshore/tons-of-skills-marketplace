---
name: flyio-sdk-patterns
description: >-
  Build a typed local adapter for the Fly.io Machines REST API with scoped auth, state waits, limits, reconciliation, and contract tests. Use when code must manage Machines or volumes. Trigger with: "wrap Machines API", "build Fly API client", "type Fly Machine states".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[language-app-and-operation-set]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - flyio
  - machines-api
  - typed-client
  - contract-testing
compatibility: 'Requires the current Machines OpenAPI contract, a supported runtime, a scoped test identity, fixtures, and a non-production integration boundary.'
---

# Typed Fly.io Machines API Adapter

## Overview

Fly.io publishes a REST API and OpenAPI reference; this workflow does not claim a provider-maintained JavaScript SDK. Generate or handwrite only a thin local adapter, keep provider fields visible, and centralize authentication, timeouts, limits, state waits, and redaction.

## Prerequisites

- Chosen operations and current OpenAPI or endpoint documentation
- Runtime and HTTP client policy, schema generator decision, and error model
- Synthetic fixtures plus an authorized non-production app for contract verification

## Instructions

### Step 1: Freeze the contract

Record base URL, operation paths, request and response schemas, state enums, response codes, and retrieval fingerprint. Preserve unknown fields for forward compatibility.

### Step 2: Define a thin transport

Centralize bearer auth, content type, request ID, timeout, retry eligibility, response parsing, and error redaction. Do not hide target app or Machine identifiers.

### Step 3: Model desired and observed state

Represent Machine ID, instance version, configuration, lifecycle state, and target state separately. Require callers to reconcile before replay.

### Step 4: Use the provider wait operation

After a mutation, wait for `started`, `stopped`, `suspended`, or `destroyed` with a bounded timeout and the required instance version where applicable.

### Step 5: Apply rate and conflict policy

Serialize conflicting actions per identifier, use documented per-action limits, retry only eligible failures, and refresh after 409, 408, or ambiguous transport results.

### Step 6: Test the adapter

Use fixture tests for every response and error class, then run an authorized read and one reversible non-production lifecycle operation with cleanup.

## Authentication

Inject `FLY_API_TOKEN` from a secret manager and send it only as the bearer header to the documented Machines API host. Keep token scope outside the client configuration file and scrub headers and Machine config secrets from exceptions.

## Tool Discipline

Use Read and Grep to inspect application configuration, deployment evidence, provider documentation, fixtures, logs, schemas, and existing tests before proposing a change. Use Write or Edit only for an approved plan, configuration, implementation, test, or redacted receipt. Do not create, deploy, scale, restart, stop, suspend, destroy, rotate, revoke, expose, or migrate live Fly.io resources without explicit operator approval.

## Output

- Contract fingerprint and supported-operation matrix
- Typed adapter with transport, state, rate, conflict, and redaction policies
- Fixture and non-production contract-test receipt with cleanup state

Return the target organization, app, environment, region set, Machine or database identifiers, source-contract fingerprint, evidence, unresolved risks, rollback state, and final decision without exposing tokens, secrets, connection strings, or customer data.

## Examples

A TypeScript service wraps get, update, start, stop, and wait without inventing an official SDK. It records the active instance version, waits for the documented target states, serializes actions per Machine, and preserves unknown response properties.

## Error Handling

| Failure | Response |
| --- | --- |
| Response schema changes | Quarantine the unknown shape, preserve raw redacted evidence, update fixtures and types, and re-run contract tests. |
| Wait returns 408 | Read current Machine and instance state; do not assume the preceding mutation failed. |
| Adapter receives 401 | Stop, verify the secret reference and token scope, and never print the bearer value. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Machines API setup](https://fly.io/docs/machines/api/working-with-machines-api/)
- [Automation and tokens](https://fly.io/docs/flyctl/integrating/)
- [App configuration](https://fly.io/docs/reference/configuration/)
- [Machines resource](https://fly.io/docs/machines/api/machines-resource/)
- [Machines API OpenAPI](https://docs.machines.dev/+external)
- [Machine states](https://fly.io/docs/machines/machine-states/)
