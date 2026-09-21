---
name: canva-debug-bundle
description: 'Assemble a minimal Canva Connect diagnostic bundle without credentials, customer content, raw payloads, or full headers. Use when preparing an incident handoff or provider escalation. Trigger with: "Canva debug bundle", "collect Canva evidence", "sanitize Canva diagnostics".'
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[incident-id-and-approved-output-path]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - canva
  - debugging
  - operations
compatibility: 'Collection requires an incident ID, approved evidence destination, retention period, and reviewer.'
---

# Canva Redacted Debug Bundle

## Overview

Prefer references and classifications over raw data. The bundle should prove configuration and failure state while remaining safe to share with authorized responders.

## Prerequisites

- Incident ID, UTC window, affected endpoint pattern, and deployment revision
- Approved evidence path, reviewer, retention, and deletion time
- Redaction denylist and current data-classification policy

## Instructions

### Step 1: Freeze a manifest

List each proposed artifact, purpose, source, classification, redaction rule, owner, and retention before collecting it.

### Step 2: Collect local versions

Use Read and Grep to capture application/runtime version, pinned OpenAPI checksum, deployment/config revision, and feature flags without environment values.

### Step 3: Collect failure envelopes

Record aggregate status/provider-code counts, endpoint patterns, opaque request/job references, and sanitized timestamps. Do not collect bodies or user/resource IDs.

### Step 4: Add bounded connectivity evidence

If authorized, record DNS/TLS outcome and one non-mutating test-user status check. Exclude Authorization and response headers beyond an explicit safe allowlist.

### Step 5: Review before packaging

Use Write or Edit to build the manifest and summary, scan for credential formats, URLs, personal data, and design content, then require a second-person review.

### Step 6: Seal and expire

Hash the reviewed files, record access controls and deletion time, transfer through the approved channel, and verify deletion after closure.

## Authentication

Canva Connect calls use Bearer access tokens obtained by a backend through OAuth 2.0 Authorization Code with SHA-256 PKCE. Request explicit least-privilege scopes, keep client secrets and tokens out of browser-visible state, and serialize refresh so the replacement single-use refresh token is stored atomically.

## Tool Discipline

Use Read and Grep for discovery and evidence. Use Write or Edit only for the approved artifact, code, configuration, test, or receipt described by this workflow; do not make an unapproved Canva-side change.

## Output

- Scoped decision or implementation artifact
- Redacted operation and validation receipt
- Failure, rollback, and follow-up ownership record

## Examples

A support bundle contains the release SHA, OpenAPI checksum, endpoint/status histogram, opaque export job reference, and sanitized timeline—never the export body, URL, token, or profile.

## Error Handling

| Failure | Response |
| --- | --- |
| Artifact purpose is unclear | Exclude it from the bundle |
| Redaction cannot be proven | Do not package or share the file |
| Live probe needs broader scope | Skip it and document the evidence gap |
| Bundle retention expires | Delete it and record the disposal receipt |

## Resources

- [First-party source notes](references/official-docs.md)
- [Connect security](https://www.canva.dev/docs/connect/guidelines/security/)
- [Error responses](https://www.canva.dev/docs/connect/error-responses/)
