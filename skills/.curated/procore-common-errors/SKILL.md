---
name: procore-common-errors
description: >-
  Triage Procore OAuth, routing, permission, validation, pagination, throttling, and webhook failures without widening access or retrying blindly. Use when a Procore integration returns 4xx or 5xx responses, empty data, or missing deliveries. Trigger with: "debug Procore 403", "fix Procore API errors", "why is Procore returning 404".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[status-symptom-and-normalized-route]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - procore
  - troubleshooting
  - errors
compatibility: 'Requires sanitized request metadata, provider response details, and access to the relevant Procore app and endpoint documentation.'
---

# Procore Error Classification and Recovery

## Overview

Classify failures by identity, company routing, authorization, endpoint contract, business validation, throttling, or provider health. Preserve the original response and avoid treating every 404 as absence or every 5xx as safe to retry.

## Prerequisites

- Timestamp, environment, method, normalized route, status, and sanitized response
- Token alias, app version, company and project context, and operation type
- Current endpoint reference plus access to Integration Health or API activity evidence

## Instructions

### Step 1: Preserve the failure

Capture response code, headers, body shape, correlation data, and elapsed time. Redact authorization, destination headers, query secrets, names, and construction payloads.

### Step 2: Classify the layer

Map 401 to token or environment; 403 to connection, permission, tool, or project scope; 404 to route, identifier, or concealed access; 422 to business validation; 429 to rate budget; and 5xx to provider or transient infrastructure.

### Step 3: Check company routing

Verify the intended company and whether `Procore-Company-Id` is required. Audit background jobs and webhook handlers that may have lost explicit routing context.

### Step 4: Check the public contract

Confirm the route, API version, required fields, filters, enabled tool, and project membership against current documentation. Reject private or deprecated endpoints.

### Step 5: Recover narrowly

Refresh or reauthorize only for an identity failure, fix permissions only when evidence proves the missing permission, honor rate headers, and retry server errors only when the operation is safe.

### Step 6: Verify the fix

Replay the smallest sanitized case, confirm the expected status and resource boundary, and monitor the relevant Integration Health observation or API activity slice.

## Authentication

Troubleshooting uses the existing OAuth 2.0 Bearer token alias and never requests a broader token as a generic fix. Authorization Code and DMSA principals retain their existing permission models throughout diagnosis.

## Tool Discipline

Use Read and Grep to inspect logs, adapters, manifests, and provider contracts. Use Write or Edit only for the approved fix, regression test, or redacted receipt; never store tokens or copy raw customer payloads into diagnostics.

## Output

- Classified root cause with supporting provider evidence
- Narrow recovery and regression test
- Redacted before-and-after receipt

Return what failed, why, what changed, how access stayed bounded, and whether replay succeeded.

## Examples

A project record that exists returns 404. Instead of changing the URL or granting admin access, the operator checks company routing, project membership, enabled tools, and read permission, then proves the corrected scope with one read.

## Error Handling

| Failure | Response |
| --- | --- |
| Evidence lacks the original response | Reproduce one bounded request before proposing a fix. |
| 429 response | Honor `X-Rate-Limit-Reset`, queue work, and add jitter; do not hammer the endpoint. |
| Ambiguous write after timeout | Reconcile provider state before retrying the mutation. |
| Unknown or private route | Stop and replace it with a documented public endpoint or contact Procore API support. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Troubleshooting](https://developers.procore.com/documentation/troubleshooting)
- [Error code reference](https://developers.procore.com/documentation/error-reference)
- [Integration Health](https://developers.procore.com/documentation/integration-health)
