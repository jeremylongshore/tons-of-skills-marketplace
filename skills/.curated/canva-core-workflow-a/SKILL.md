---
name: canva-core-workflow-a
description: 'Create an authorized Canva design and export it through a reconciled asynchronous job. Use when performing design creation, supported-format selection, export polling, and safe result handling. Trigger with: "create Canva design", "export Canva design", "poll Canva export".'
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[design-intent-and-export-format]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - canva
  - design
  - operations
compatibility: 'Requires an authorized test or production user, explicit design scopes, and approved content/retention policy.'
---

# Canva Design and Export Workflow

## Overview

Keep design creation, user editing, export submission, job reconciliation, and result delivery as separate recorded operations. Query current supported export formats instead of hard-coding a universal list.

## Prerequisites

- Approved design purpose, owner, input rights, and destination
- Explicit design scopes and resource authorization
- Pinned endpoint contract and result-data retention decision

## Instructions

### Step 1: Authorize the request

Resolve tenant, user, design purpose, required explicit scopes, content rights, and whether a new design is permitted.

### Step 2: Create once

Persist an application operation key before submitting the design request. Store only the returned opaque design reference and approved URLs under policy.

### Step 3: Confirm user handoff

Present the correct view or edit surface only to the authorized user. Do not treat creation as evidence that downstream export is allowed.

### Step 4: Discover formats

Query the design export-formats endpoint when available and validate the requested format/options against that response and current OpenAPI.

### Step 5: Submit and poll export

Persist the export job ID, poll the existing job with bounded exponential backoff, and stop on success, failed, or the local timeout budget.

### Step 6: Deliver and expire

Validate content type and destination, keep result URLs out of logs, honor response/provider expiry evidence, and record cleanup or retention.

## Authentication

Canva Connect calls use Bearer access tokens obtained by a backend through OAuth 2.0 Authorization Code with SHA-256 PKCE. Request explicit least-privilege scopes, keep client secrets and tokens out of browser-visible state, and serialize refresh so the replacement single-use refresh token is stored atomically.

## Tool Discipline

Use Read and Grep for discovery and evidence. Use Write or Edit only for the approved artifact, code, configuration, test, or receipt described by this workflow; do not make an unapproved Canva-side change.

## Output

- Scoped decision or implementation artifact
- Redacted operation and validation receipt
- Failure, rollback, and follow-up ownership record

## Examples

A user creates an approved presentation, edits it in Canva, then requests PDF export. The service checks available formats, submits one job, reconciles its ID, and delivers the result through an access-controlled application route.

## Error Handling

| Failure | Response |
| --- | --- |
| Format unavailable | Return the current supported choices without submitting |
| Export remains in progress | Stop at the local budget and continue reconciliation asynchronously |
| Design ownership changed | Fail closed and require a new authorization decision |
| Result URL reaches logs | Revoke access where possible and remediate redaction |

## Resources

- [First-party source notes](references/official-docs.md)
- [Design APIs](https://www.canva.dev/docs/connect/api-reference/designs/)
- [Export APIs](https://www.canva.dev/docs/connect/api-reference/exports/)
