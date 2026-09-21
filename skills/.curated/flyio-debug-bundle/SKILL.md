---
name: flyio-debug-bundle
description: >-
  Collect a bounded, redacted Fly.io support bundle for release, Machine, health, volume, network, and platform incidents. Use when escalating a reproducible problem. Trigger with: "build Fly debug bundle", "collect Fly support evidence", "sanitize Fly incident data".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[app-environment-and-incident-window]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - flyio
  - diagnostics
  - support
  - redaction
compatibility: 'Requires read access to the affected app, an incident time window, a secure evidence destination, and approval for any log or configuration collection.'
---

# Fly.io Redacted Support Evidence

## Overview

Create a minimal evidence package that preserves diagnostic value without copying tokens, secret values, connection strings, full customer payloads, or unbounded logs. Every artifact needs source, timestamp, scope, redaction rule, and collection status.

## Prerequisites

- Incident ID, owner, app, environment, regions, and time window
- Approved secure destination with retention and access controls
- Redaction rules for identifiers, logs, environment, network, and customer content

## Instructions

### Step 1: Define the evidence manifest

List requested artifacts, collection commands or APIs, owners, time bounds, redaction transformations, and expected hashes before gathering data.

### Step 2: Capture release and configuration state

Record flyctl version, release or image identity, configuration hash, process groups, services, health definitions, and recent change references without including secrets.

### Step 3: Capture Machine and health state

Collect aggregate status, Machine IDs or approved pseudonyms, regions, lifecycle and instance-version state, checks, restarts, and relevant exit metadata.

### Step 4: Capture bounded logs and platform context

Use the smallest incident window, remove sensitive fields, note truncation, and record provider status separately from application evidence.

### Step 5: Capture storage and network topology

Record volume IDs or pseudonyms, regions, attachments, snapshot state, public allocations, and private DNS expectations; exclude credentials and packet contents.

### Step 6: Seal and review

Hash the sanitized artifacts, have the incident owner review the manifest, and publish only to the approved destination with expiry metadata.

## Authentication

Collect with a read-only token where possible. Never place `FLY_API_TOKEN`, app secret values, database URLs, WireGuard private keys, registry credentials, or raw environment dumps in the bundle. Treat deploy access as sensitive because deployed code can read runtime secrets.

## Tool Discipline

Use Read and Grep to inspect application configuration, deployment evidence, provider documentation, fixtures, logs, schemas, and existing tests before proposing a change. Use Write or Edit only for an approved plan, configuration, implementation, test, or redacted receipt. Do not create, deploy, scale, restart, stop, suspend, destroy, rotate, revoke, expose, or migrate live Fly.io resources without explicit operator approval.

## Output

- Evidence manifest with scope, source, timestamps, hashes, and redaction rules
- Sanitized release, configuration, Machine, health, log, volume, and network artifacts
- Collection failures, gaps, escalation question, retention owner, and deletion date

Return the target organization, app, environment, region set, Machine or database identifiers, source-contract fingerprint, evidence, unresolved risks, rollback state, and final decision without exposing tokens, secrets, connection strings, or customer data.

## Examples

For a Machine restart loop in one region, the bundle includes the release image, redacted config, Machine state history, health transitions, a five-minute sanitized log window, volume attachment metadata, and hashes. It omits environment values and full log history.

## Error Handling

| Failure | Response |
| --- | --- |
| Collection command fails | Record the failure and missing artifact; do not replace it with guessed data. |
| Secret is detected | Quarantine the bundle, rotate if exposure is possible, re-redact from the source, and issue a new hash. |
| Bundle is too large | Narrow the time and resource scope; do not archive an entire production log stream. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Machines API setup](https://fly.io/docs/machines/api/working-with-machines-api/)
- [Automation and tokens](https://fly.io/docs/flyctl/integrating/)
- [App configuration](https://fly.io/docs/reference/configuration/)
- [Machine states](https://fly.io/docs/machines/machine-states/)
- [Monitoring](https://fly.io/docs/monitoring/)
- [Health checks](https://fly.io/docs/reference/health-checks/)
- [Fly Volumes](https://fly.io/docs/volumes/)
