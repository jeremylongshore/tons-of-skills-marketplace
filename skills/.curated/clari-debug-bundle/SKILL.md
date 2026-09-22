---
name: clari-debug-bundle
description: >-
  Analyze a Clari incident and collect a minimal support bundle with job timelines, contract fingerprints, and secret-safe evidence. Use when escalating a provider or pipeline failure. Trigger with: "collect Clari diagnostics", "build a Clari support bundle", "redact a Clari incident".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[surface-incident-id-and-time-window]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - clari
  - diagnostics
  - support
  - redaction
compatibility: 'Requires an incident identifier, authorized time window, redaction policy, and an encrypted evidence destination.'
---

# Clari Redacted Support Bundle

## Overview

A useful support bundle explains what happened without copying credentials or customer payloads. Collect identifiers, timing, states, hashes, schema summaries, and controlled samples under a manifest that is reviewable before sharing.

## Prerequisites

- Incident ID, owner, environment, surface, and affected window
- Exact endpoint and method inventory plus provider job IDs or cursors
- Approved redaction rules, retention, and sharing destination

## Instructions

### Step 1: Create the manifest

Record collector version, contract fingerprint, host, endpoint names, request fingerprints, timestamps, and system versions.

### Step 2: Collect control-plane evidence

Capture HTTP statuses, redacted response headers, error codes or IDs, job state transitions, attempts, waits, and scheduler ownership.

### Step 3: Collect data-plane summaries

Record content type, byte and row counts, field names, schema hash, and reconciliation deltas without raw revenue, identity, transcript, or recording data.

### Step 4: Collect local health

Include deployment version, checkpoint state, queue depth, destination health, and relevant redacted logs.

### Step 5: Scan and review

Search for all credential header names, token patterns, emails, names, deal values, transcript text, and signed URLs; require human review before sharing.

### Step 6: Seal and expire

Hash the bundle, encrypt it, record recipients and expiry, and delete working copies according to incident policy.

## Authentication

Never collect values for `apikey`, `partnerkey`, `X-Api-Key`, or `X-Api-Password`. If a credential may have entered any artifact, stop distribution and rotate it before continuing.

## Tool Discipline

Use Read and Grep to inspect configuration, provider contracts, fixtures, logs, schemas, and existing tests before proposing a change. Use Write or Edit only for the approved plan, implementation, test, or redacted receipt; do not issue, rotate, revoke, create, update, cancel, delete, export, ingest, or publish provider data without explicit operator approval.

## Output

- Redacted manifest and evidence inventory
- Job or cursor timeline plus schema and reconciliation summaries
- Bundle hash, reviewer, recipients, expiry, and deletion receipt

Return the exact surface, environment, resource or job identifiers, contract fingerprint, evidence, unresolved risks, and final decision without exposing credentials or sensitive customer data.

## Examples

A stuck forecast incident bundle includes the job ID, `STARTED` timeline, provider error ID, contract hash, scheduler version, and empty-result schema—but no token, forecast rows, or user email addresses.

## Error Handling

| Failure | Response |
| --- | --- |
| Scanner finds a credential or sensitive value | Quarantine the bundle, rotate if necessary, redact, and restart review. |
| Evidence lacks a job ID or cursor | Correlate through request fingerprint and timestamps; state the uncertainty explicitly. |
| Bundle is too large | Replace payloads with hashes, schemas, counts, and the smallest approved redacted sample. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Clari Revenue API reference](https://developer.clari.com/default/documentation/external_spec)
- [Clari Copilot API reference](https://api-doc.copilot.clari.com/)
- [Clari service status](https://clari.statuspage.io/)
