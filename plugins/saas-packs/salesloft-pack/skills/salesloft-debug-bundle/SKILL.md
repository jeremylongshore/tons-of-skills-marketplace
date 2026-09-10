---
name: salesloft-debug-bundle
description: >-
  Build a minimal redacted Salesloft escalation bundle with contract, auth-state, rate, timing, deployment, and API Logs evidence. Use when a failure needs support or engineering review. Trigger with "Salesloft debug bundle", "Salesloft support evidence", or "Salesloft diagnostics".
argument-hint: "[repository-path] [incident-id]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- salesloft
- diagnostics
model: inherit
effort: medium
compatibility: Designed for Claude Code
---
# Salesloft Redacted Debug Bundle

## Overview

This skill produces a small evidence package that another engineer can use without receiving credentials or customer records. It separates observed facts from hypotheses.

## Prerequisites

- Incident ID, owner, timeframe, environment, and expected behavior
- Approved output directory and retention period
- Access to application logs and, when authorized, Salesloft API Logs
- A redaction review owner

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to locate bounded logs, configuration keys, and version files. Use `WebFetch` only for current official Salesloft documentation. Use `Write` or `Edit` only for the approved redacted artifact.

## Current Contract

- Capture method and path template, status, content type, latency, attempt count, and deployment revision.
- Capture auth type, expiry state, scope names, and team alias, never credential values.
- Capture `x-ratelimit-endpoint-cost` and `x-ratelimit-remaining-minute` when present.
- Salesloft API Logs can lag about five minutes and expose up to 10,000 calls or 14 days in the UI; absence is not immediate proof that no call occurred.

## Authentication

Use existing approved access. The bundle must omit Authorization headers, refresh tokens, client secrets, API keys, callback tokens, cookies, raw bodies, and prospect fields.

## Instructions

1. Freeze incident scope, UTC window, environment, and affected operation.
2. Collect only bounded application events for that window and correlation key.
3. Add redacted configuration names, dependency versions, and deployment revision.
4. Add response-envelope shape and rate metadata without record contents.
5. If authorized, compare API Logs by integration, team, endpoint, time, and status after the documented lag.
6. Scan the artifact for credential patterns and CRM fields, then record checksums.
7. Require a second review before external sharing.

## Approval Boundaries

Do not archive full environment dumps, databases, raw HTTP payloads, or unrestricted logs. External sharing requires named reviewer approval and an expiry date.

## Output

Return bundle path, file inventory, redactions, checksums, evidence timeline, hypotheses, missing evidence, reviewer, and deletion date.

## Error Handling

| Condition | Response |
|---|---|
| Secret scanner matches | Quarantine, remove the value, rotate if exposure is possible, and rebuild. |
| API Logs empty | Wait for documented lag and verify filters; do not infer no request. |
| Customer data present | Remove or aggregate it before the bundle leaves the system. |
| Evidence conflicts | Preserve both observations and label the discrepancy. |

## Examples

The example below shows the minimum redacted evidence expected from a successful invocation of this operator workflow.

```text
incident=SL-204; files=4; secret-findings=0; pii-findings=0; reviewer=pending
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Salesloft API Logs](https://developers.salesloft.com/docs/platform/guides/api-logs/)
- [Request and response format](https://developers.salesloft.com/docs/platform/api-basics/request-response-format/)
