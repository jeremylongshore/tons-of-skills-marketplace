---
name: canva-observability
description: 'Implement low-cardinality metrics, traces, logs, and alerts for Canva Connect workflows. Use when measuring API health, authorization failures, async-job reconciliation, queue pressure, or token rotation without exposing protected data. Trigger with: "monitor Canva", "Canva metrics", "Canva tracing".'
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[service-name-and-slo]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - canva
  - observability
  - operations
compatibility: 'Requires an approved telemetry schema, retention policy, and SLO derived from the application rather than guessed provider guarantees.'
---

# Canva Privacy-Safe Observability

## Overview

Observe logical operations and provider requests separately. Keep metrics aggregate and logs content-free; do not assume undocumented rate-limit headers or fixed Canva latency thresholds.

## Prerequisites

- Service and operation inventory plus local SLOs
- Telemetry allowlist/denylist, retention, and access controls
- Pinned endpoint/error/job contracts and incident routing

## Instructions

### Step 1: Define semantic signals

Name logical operation count, provider request count, status/provider-code class, latency distribution, job age/terminal state, queue depth, refresh result, and reconciliation outcome.

### Step 2: Control dimensions

Allow method, normalized endpoint, environment, operation type, and coarse result. Exclude user, tenant, design, asset, token, URL, job, email, and raw error dimensions.

### Step 3: Instrument the adapter

Use Write or Edit to create spans around authorized provider requests while keeping token refresh, job reconciliation, and business operations as distinct spans.

### Step 4: Measure local rate budget

Track configured admission/concurrency and observed HTTP 429 by endpoint/user class. Record response retry instructions only when actually present; do not invent headroom gauges.

### Step 5: Instrument async jobs

Measure age and terminal state from the persisted ledger, not from repeated submissions. Alert on reconciliation backlog and duplicate-attempt prevention.

### Step 6: Set evidence-based alerts

Derive thresholds from application SLOs and measured baselines, require sustained windows, link runbooks, and avoid automatic scope, retry, or mutation changes.

### Step 7: Validate redaction

Use Read and Grep against tests and sample telemetry to prove credentials, bodies, URLs, profiles, and resource identifiers cannot be emitted.

## Authentication

Canva Connect calls use Bearer access tokens obtained by a backend through OAuth 2.0 Authorization Code with SHA-256 PKCE. Request explicit least-privilege scopes, keep client secrets and tokens out of browser-visible state, and serialize refresh so the replacement single-use refresh token is stored atomically.

## Tool Discipline

Use Read and Grep for discovery and evidence. Use Write or Edit only for the approved artifact, code, configuration, test, or receipt described by this workflow; do not make an unapproved Canva-side change.

## Output

- Scoped decision or implementation artifact
- Redacted operation and validation receipt
- Failure, rollback, and follow-up ownership record

## Examples

A dashboard shows export logical operations, provider submissions, in-progress age, terminal failures, and reconciliation backlog by environment and endpoint pattern—with no user or design labels.

## Error Handling

| Failure | Response |
| --- | --- |
| Metric cardinality grows unexpectedly | Disable the new dimension and inspect label sources |
| Token or URL reaches telemetry | Contain, revoke if needed, and remediate before restoring |
| 429 signal lacks endpoint context | Fix normalized operation attribution |
| Alert threshold has no SLO basis | Keep it advisory until calibrated |

## Resources

- [First-party source notes](references/official-docs.md)
- [API request model](https://www.canva.dev/docs/connect/api-requests-responses/)
- [Connect security](https://www.canva.dev/docs/connect/guidelines/security/)
