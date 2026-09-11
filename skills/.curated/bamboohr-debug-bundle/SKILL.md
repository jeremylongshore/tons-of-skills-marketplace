---
name: bamboohr-debug-bundle
description: >-
  Assemble a PII-minimized BambooHR diagnostic receipt using request IDs,
  statuses, timing, version facts, and redacted configuration. Use when
  escalating an API incident or preparing a support case. Trigger with
  "BambooHR debug bundle", "BambooHR support evidence", or "BambooHR request ID".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<incident-id> <time-window>"
version: 1.5.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, hr, bamboohr, diagnostics, privacy]
model: inherit
effort: high
compatibility: Designed for Claude Code
---
# BambooHR Privacy-Safe Debug Receipt

## Overview

Create evidence sufficient to reproduce and route a BambooHR failure without
packaging employee records, credentials, tokens, raw request/response bodies,
webhook payloads, or environment dumps.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The tenant, identity, and data scope only when approved live work is in scope.
- The current evidence register plus customer-specific permissions and agreements.

## Current Contract

The official Python SDK surfaces a request ID from `x-request-id`,
`x-bamboohr-request-id`, or `request-id` and includes a secure log filter for
sensitive headers and URL parameters. These controls do not make arbitrary
application logs safe; verify the emitted artifact field by field.

## Authentication

Diagnostics may record only auth mode, credential owner alias, token/key age,
and last rotation time. Never include Authorization headers, API keys, client
secrets, refresh/access tokens, cookie values, or webhook private keys.

## Instructions

1. Define incident ID, tenant alias, UTC window, operation, expected result,
   actual status, impact, and evidence recipient.
2. Locate only bounded logs for the affected request IDs. Do not grep or export
   an entire environment, home directory, database, or log bucket.
3. Produce a manifest containing application version/commit, SDK or adapter
   version, endpoint template without IDs/query values, auth mode, timeout,
   configured retry count, status, latency, request IDs, and safe aggregate counts.
   Do not retain the response body.
4. Replace tenant, employee, file, benefit, applicant, and webhook identifiers
   with stable incident-local aliases. Remove bodies and free-text errors that
   may echo BambooHR's response content.
5. Scan the proposed receipt for secret formats, email addresses, government
   IDs, dates of birth, addresses, compensation, health/benefit data, and URLs
   containing query values. Review manually after automated scanning.
6. Write a checksum and explicit inclusion/exclusion list. Keep the artifact
   local until the data owner approves its recipient and retention.
7. Prefer a directory or JSON/Markdown receipt. Do not create a broad tarball by
   default; archive only the reviewed manifest if the support channel requires it.

## Tool Discipline

Use Read, Glob, and Grep only against the approved paths and time window. Use
Write/Edit to create the minimal receipt and redaction tests. Do not use shell
archive or network tools under this skill.

## Approval Boundaries

Require approval before reading production logs, writing a diagnostic artifact,
including any pseudonymized employee fact, or sending evidence to BambooHR or a
third party. Creation does not authorize transmission.

## Output

Return receipt path, checksum, incident window, request IDs, included safe fields,
excluded sensitive classes, scanner/manual-review result, approved recipient,
retention deadline, and transmission status.

## Error Handling

- Suspected secret or PII in output: stop, quarantine locally, and rebuild from
  the allowlist; do not attempt line-by-line salvage for transmission.
- Missing request ID: correlate on a narrow timestamp/operation window and label
  the result lower confidence.
- Recipient asks for raw payload: escalate to the data owner/security process.

## Examples

- "Zip all BambooHR logs" becomes a manifest-first, allowlisted receipt.
- "Support needs the failing employee JSON" substitutes request ID, status, and schema.

## Resources

Read [official evidence](references/official-docs.md) before collecting evidence.
