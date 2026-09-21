---
name: clari-common-errors
description: >-
  Analyze and resolve Clari authentication, authorization, job, ingestion, schema, and empty-result failures from redacted evidence. Use when an integration fails or returns incomplete data. Trigger with: "debug Clari", "triage a Clari error", "fix an empty Clari export".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[surface-endpoint-job-id-and-symptom]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - clari
  - troubleshooting
  - errors
  - diagnostics
compatibility: 'Requires a redacted request manifest, provider response status, correlation or error identifiers, and access to the matching first-party contract.'
---

# Clari API Failure Triage

## Overview

Classify the failure before retrying it. Separate transport, authentication, authorization, entitlement, quota, job-state, request-shape, schema, and data-scope failures so recovery does not create duplicate jobs or leak sensitive payloads.

## Prerequisites

- Surface, base URL, endpoint, method, timestamp, and environment
- Redacted status, headers, error code or ID, and job ID when present
- Expected hierarchy, forecast, workspace, entity, and time-window scope

## Instructions

### Step 1: Reconstruct the boundary

Confirm host, API version, method, headers by name, request shape, and the identity used without revealing credential values.

### Step 2: Classify HTTP and provider state

Distinguish 401, 403, 428, 429, 5xx, empty success, schema rejection, and non-terminal or aborted job states.

### Step 3: Check authorization and entitlement

Verify Forecast Tab access, hierarchy opt-in, product entitlement, workspace membership, partner enablement, and entity configuration.

### Step 4: Check quota and duplication risk

Read available limits when supported, inspect existing jobs, and avoid re-queuing a request whose outcome is merely unknown.

### Step 5: Reduce to a safe reproduction

Use the smallest read-only or synthetic request that preserves the failure and remove customer values from the artifact.

### Step 6: Choose recovery and prove it

Rotate or re-scope credentials, repair the request, wait for capacity, migrate schema, or escalate with a redacted receipt; then rerun exactly one bounded verification.

## Authentication

Never print `apikey`, `partnerkey`, `X-Api-Key`, or `X-Api-Password`. A 200 response with empty data is not proof of correct authorization; validate the effective hierarchy and workspace separately.

## Tool Discipline

Use Read and Grep to inspect configuration, provider contracts, fixtures, logs, schemas, and existing tests before proposing a change. Use Write or Edit only for the approved plan, implementation, test, or redacted receipt; do not issue, rotate, revoke, create, update, cancel, delete, export, ingest, or publish provider data without explicit operator approval.

## Output

- Failure classification and ruled-out causes
- Minimal redacted reproduction with contract version
- Recovery action, verification result, and escalation bundle if unresolved

Return the exact surface, environment, resource or job identifiers, contract fingerprint, evidence, unresolved risks, and final decision without exposing credentials or sensitive customer data.

## Examples

A forecast request returns no rows. The operator confirms the job was `DONE`, then finds the integration user was not opted into the requested hierarchy; access is corrected and one controlled export proves recovery.

## Error Handling

| Failure | Response |
| --- | --- |
| 401 | Verify the surface-specific headers and secret reference; rotate if exposure is suspected. |
| 403 or 428 | Check entitlement, hierarchy, partner configuration, and ingestion preconditions. |
| 429 or stuck job | Inspect limits and existing jobs, back off with jitter, and resume from the retained job ID. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Clari Revenue API reference](https://developer.clari.com/default/documentation/external_spec)
- [Clari Copilot API reference](https://api-doc.copilot.clari.com/)
- [Clari service status](https://clari.statuspage.io/)
