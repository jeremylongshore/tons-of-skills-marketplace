---
name: procore-debug-bundle
description: >-
  Produce a minimal redacted Procore diagnostic manifest for escalation without collecting credentials, customer payloads, or attachment contents. Use when an API failure needs handoff to engineering or Procore support. Trigger with: "build a Procore debug bundle", "prepare Procore support evidence", "redact Procore diagnostics".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[incident-or-request-reference]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - procore
  - diagnostics
  - redaction
compatibility: 'Requires access to sanitized integration logs and an approved encrypted destination for the final diagnostic manifest.'
---

# Redacted Procore Diagnostic Manifest

## Overview

Build a manifest of request metadata and assertions, not a raw archive. Procore support can investigate with method, URL, status, sanitized headers and body, and occurrence time; secrets and construction data increase risk without improving diagnosis.

## Prerequisites

- Incident identifier, owner, audience, retention deadline, and approved destination
- Exact failing request window and normalized route
- Organization redaction rules for identities, projects, documents, and credentials

## Instructions

### Step 1: Declare collection scope

List the exact evidence fields required for the failure class. Reject recursive log directories, database dumps, environment files, OAuth responses, and attachment collections.

### Step 2: Collect metadata

Capture UTC occurrence time, environment, method, normalized URL, status, elapsed time, API version, company and project aliases, rate headers, retry header, and application release identifier.

### Step 3: Sanitize content

Remove Authorization and destination headers, client credentials, tokens, cookies, user details, project names, query secrets, request bodies, response payloads, and signed file URLs unless a reviewed minimal fragment is essential.

### Step 4: Validate redaction

Grep the staged manifest for secret patterns and prohibited field names. Inspect every remaining value manually and replace provider identifiers with stable aliases where possible.

### Step 5: Seal and transfer

Write a checksum, collector identity, scope statement, redaction result, expiry, and access list. Transfer only through the approved encrypted channel.

### Step 6: Delete on schedule

Record the deletion owner and deadline, and preserve only the non-sensitive incident receipt after the diagnostic artifact expires.

## Authentication

This workflow never acquires or refreshes OAuth credentials. Existing Bearer tokens, client secrets, refresh tokens, webhook destination headers, cookies, and signed URLs are prohibited from the manifest.

## Tool Discipline

Use Read and Grep to inspect only the approved files and verify redaction. Use Write or Edit only for the bounded manifest and receipt; do not copy raw log trees or customer data into a new bundle.

## Output

- Collection manifest and explicit exclusions
- Redaction verification and artifact checksum
- Transfer, access, retention, and deletion receipt

Return the artifact location by approved reference, never inline its sensitive contents.

## Examples

For repeated 403 responses, the manifest includes the normalized endpoint, timestamps, status, app release, company and project aliases, and sanitized response message. It excludes the token, full request body, user names, and source log files.

## Error Handling

| Failure | Response |
| --- | --- |
| Secret pattern found | Stop transfer, quarantine the artifact, redact again, and rotate if exposure occurred. |
| Scope cannot be bounded | Escalate with metadata only; do not create a broad archive. |
| Support requests raw credentials | Refuse and provide sanctioned request metadata or a controlled reproduction. |
| Retention owner missing | Do not transfer until an owner and deletion deadline are assigned. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Procore troubleshooting](https://developers.procore.com/documentation/troubleshooting)
- [API Call Activity Report](https://developers.procore.com/documentation/api-activity-export)
- [API security overview](https://developers.procore.com/documentation/api-security-overview)
