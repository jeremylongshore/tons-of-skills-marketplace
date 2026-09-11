---
name: lucidchart-debug-bundle
description: 'Assemble a redacted, reproducible Lucid integration diagnostic bundle. Use when an API, Standard Import, extension, export, or data connector failure needs escalation. Trigger with "build Lucid debug bundle".'
argument-hint: "[project-path] [incident-id]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, lucidchart, debugging, diagnostics, support]
model: inherit
effort: medium
compatibility: Designed for Claude Code; bundle sharing requires data-owner approval and a secure approved support channel
---
# Redacted Lucid Debug Bundle

## Overview
Create a minimal evidence package that reproduces a Lucid failure while excluding credentials, sensitive document content, and unnecessary personal data.

## Prerequisites
- Incident identifier, time window, affected component, and expected behavior
- Approval to inspect relevant local artifacts and sanitized responses
- A clean output directory outside application source and secret stores

## Tool Discipline
Use `Read`, `Glob`, and `Grep` to collect bounded evidence, `WebFetch` for current contract comparison, and `Write` or `Edit` only inside the declared bundle directory.

## Current Contract
Useful evidence differs by surface: REST requests need method, path family, safe headers, status and request identifiers; Standard Import needs archive structure and sanitized samples; extensions/connectors need versions, manifests, build output, and minimal fixtures.

## Authentication
Never copy `Authorization`, cookies, API keys, OAuth codes, refresh tokens, client secrets, signed URLs, or raw environment files. Replace sensitive identifiers consistently so relationships remain diagnosable.

## Instructions
1. Declare incident scope, bundle path, retention, recipients, and exclusion rules.
2. Inventory candidate files and reject caches, dependencies, binaries, full documents, and unrelated logs by default.
3. Capture tool and SDK versions, safe manifest fields, operation category, sanitized request/response metadata, and exact timestamps.
4. For imports, include a structurally equivalent minimal archive or manifest—not protected production content.
5. For extension/connector failures, add a synthetic fixture and the smallest failing build/test receipt.
6. Scan recursively for token patterns, credentials, emails, personal data, and document content; manually review hits.
7. Write a manifest with file digests, provenance, redactions, reproduction steps, expected/actual behavior, and gaps.
8. Obtain approval before transmitting; record destination and deletion date.

## Approval Boundaries
Do not collect from production, contact Lucid support, or transmit the bundle without incident and data-owner authorization.

## Output
Return bundle path, manifest digest, files included/excluded, redaction results, reproduction status, evidence gaps, and sharing approval.

## Error Handling
| Condition | Response |
|---|---|
| Secret scanner reports a hit | Remove or irreversibly redact it, then rescan the entire bundle. |
| Failure cannot be reproduced | Preserve timestamps and safe request identifiers; label hypotheses. |
| Minimal fixture still contains sensitive data | Replace it with synthetic structure before sharing. |

## Example
```text
incident=LUCID-42; files=8; secrets=0; pii=0; reproduction=pass; manifest-sha256=...; shared=no
```

## Resources
- [Official documentation map](references/official-docs.md)

## Next Steps
Share only through the approved support channel, then enforce the recorded retention deadline.
