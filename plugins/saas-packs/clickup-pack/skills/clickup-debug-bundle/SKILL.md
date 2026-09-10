---
name: clickup-debug-bundle
description: >-
  Collect a minimal redacted ClickUp connectivity and contract bundle without task bodies, tokens, or webhook secrets. Use when escalating a ClickUp API incident. Trigger with "ClickUp debug bundle", "ClickUp diagnostics", or "collect ClickUp evidence".
argument-hint: "[incident-id] [output-directory]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- clickup
- diagnostics
model: inherit
effort: high
compatibility: Designed for Claude Code; live collection requires authorized ClickUp access and local retention controls
---
# ClickUp Redacted Diagnostic Bundle

## Overview

Create supportable evidence while preventing a troubleshooting artifact from becoming a second sensitive-data store. Make every included field explainable to the named reviewer.

## Prerequisites

- An incident identifier, approved output directory, retention deadline, and named reviewer
- A scoped credential stored outside command history and artifact content
- An allow-list of read-only probes and fields

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect the repository, adapters, configuration names, tests, and evidence. Use `WebFetch` only for current official ClickUp documentation. Use `Write` or `Edit` after confirming the target file, Workspace boundary, and requested mode.

## Current Contract

- Useful evidence includes status, endpoint version, latency, response type, sanitized error code, and rate headers.
- `GET /api/v2/user` and `GET /api/v2/team` can prove identity and authorized Workspaces without reading task content.
- Provider status is separate from tenant authorization and application behavior.
- Authorization headers, response bodies, user emails, task names, comments, attachments, and webhook secrets are excluded.

## Authentication

Use a personal token only for accountable individual/testing work or OAuth Authorization Code for a user-facing integration. Inject the token server-side through a governed secret reference, send it in `Authorization`, verify authorized Workspace IDs, and never print the token, OAuth client secret, or webhook secret.

## Instructions

1. Confirm incident scope, collection owner, field allow-list, output path, and deletion deadline.
2. Inspect local configuration names and versions without printing values.
3. Run bounded read-only identity/workspace and status probes; capture only approved metadata.
4. Record sanitized rate headers, status codes, timings, schema digests, and local adapter versions.
5. Scan the bundle for credential and content patterns; require human review before sharing.
6. Hash, transfer through the approved channel, and delete or retain on schedule.

## Approval Boundaries

Do not add raw headers, full environment dumps, task payloads, member records, or attachments to make the bundle more convenient.

## Output

Return bundle path, SHA-256, included field classes, excluded classes, scan result, reviewer, sharing decision, and deletion deadline.

## Error Handling

| Condition | Response |
|---|---|
| Redaction scan finds a secret | Do not share; quarantine, rotate, and regenerate. |
| Probe would read work content | Skip it and record the evidence gap. |
| Output directory is uncontrolled | Refuse collection until a governed location exists. |
| Incident scope expands | Obtain a new collection approval. |

## Examples

The example below is a redacted operator receipt; it contains no task text, member data, credential, or webhook secret.

```text
incident=CU-142; probes=3; task-bodies=0; secrets=0; sha256=recorded; review=approved; delete-by=2026-09-17
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [ClickUp status](https://status.clickup.com/)
- [Authentication](https://developer.clickup.com/docs/authentication)
- [Rate limits](https://developer.clickup.com/docs/rate-limits)
