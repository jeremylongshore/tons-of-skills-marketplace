---
name: clari-sdk-patterns
description: >-
  Build and validate a typed local Clari REST client with bounded retries, job polling, pagination, and redaction. Use when standardizing application code around public contracts. Trigger with: "build a Clari client", "wrap the Clari API", "type Clari responses".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[surface-language-and-owned-endpoints]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - clari
  - client-library
  - rest
  - typed-contracts
compatibility: 'Requires a pinned Clari API contract and an HTTP client with timeout, retry, TLS, and structured logging controls; no official public Clari SDK is assumed.'
---

# Typed Clari REST Client Patterns

## Overview

Wrap only the endpoints the application owns instead of inventing a broad unofficial SDK. Keep Revenue, v2 ingestion, and Copilot clients separate so their base URLs, headers, limits, schemas, and mutation policies cannot bleed across boundaries.

## Prerequisites

- Endpoint inventory and pinned first-party contract fingerprint
- Language-native HTTP and schema-validation libraries
- Defined timeout, retry, logging, and secret-redaction policies

## Instructions

### Step 1: Split clients by surface

Create separate Revenue, ingestion, and Copilot transports with immutable base URLs and header builders.

### Step 2: Model request and response types

Represent identifiers, timestamps, pagination, export job states, error bodies, and optional fields explicitly; reject unknown destructive actions by default.

### Step 3: Centralize transport policy

Set connect and response timeouts, user-agent identity, bounded retries for eligible transient failures, and correlation metadata without logging credentials or payloads.

### Step 4: Implement job primitives

Expose queue, status, cancel, and result operations as an explicit state machine; do not hide long-running work behind an unbounded method.

### Step 5: Validate at the boundary

Schema-check provider responses before domain mapping and preserve the redacted original error ID when validation fails.

### Step 6: Prove compatibility

Run offline contract tests, one non-production read smoke test, and a rollback test against the previously pinned client version.

## Authentication

Construct `apikey`, `partnerkey`, `X-Api-Key`, and `X-Api-Password` headers only inside the matching transport. Accept secret references rather than literal values and guarantee header redaction in errors, traces, and snapshots.

## Tool Discipline

Use Read and Grep to inspect configuration, provider contracts, fixtures, logs, schemas, and existing tests before proposing a change. Use Write or Edit only for the approved plan, implementation, test, or redacted receipt; do not issue, rotate, revoke, create, update, cancel, delete, export, ingest, or publish provider data without explicit operator approval.

## Output

- Endpoint-scoped typed client and surface-specific transport policy
- Contract, retry, state-machine, and redaction tests
- Compatibility matrix tied to provider contract fingerprints

Return the exact surface, environment, resource or job identifiers, contract fingerprint, evidence, unresolved risks, and final decision without exposing credentials or sensitive customer data.

## Examples

A Revenue client returns a typed job handle from a forecast request and requires the caller to poll to `DONE` before fetching results. A separate Copilot client cannot access or serialize the Revenue token.

## Error Handling

| Failure | Response |
| --- | --- |
| Response fails schema validation | Preserve a redacted sample and contract fingerprint, then stop downstream loading. |
| Retry repeats a mutation | Require an explicit idempotency decision and operator review; never assume POST or PUT is safe to replay. |
| Wrong credential reaches a surface | Fail before network I/O through separate credential types and header builders. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Clari Revenue API reference](https://developer.clari.com/default/documentation/external_spec)
- [Clari Copilot API reference](https://api-doc.copilot.clari.com/)
