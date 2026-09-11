---
name: lucidchart-common-errors
description: 'Triage Lucid authentication, scope, version, import, export, extension, and connector failures from bounded evidence. Use when a Lucid integration fails. Trigger with "troubleshoot Lucid".'
argument-hint: "[symptom] [integration-kind]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, lucidchart, troubleshooting, oauth, diagnostics]
model: inherit
effort: medium
compatibility: Designed for Claude Code; live diagnosis requires authorized Lucid evidence and approval from the document, application, connector, or account owner
---
# Lucid Integration Error Triage

## Overview
Identify the failing layer before changing credentials, scopes, documents, packages, or connector state.

## Prerequisites
- A redacted request ID, timestamp, status, integration kind, endpoint or command, and API/package version
- Expected token type and scopes from the exact official operation page
- Permission to inspect the relevant repository and Lucid project

## Tool Discipline
Use `Read`, `Glob`, and `Grep` for local evidence, `WebFetch` for official Lucid contracts and status, and `Write` or `Edit` only for approved fixes or redacted receipts.

## Current Contract
- 401 can reflect invalid or revoked credentials; 403 can reflect token type, scope, resource access, or endpoint rules.
- 429 behavior and limits are endpoint-specific; never substitute a pack-wide quota.
- Standard Import, REST resources, editor extensions, and data connectors have different failure surfaces.

## Authentication
Never collect raw tokens, secrets, authorization codes, cookies, or complete request headers. Confirm only credential class, grant, scope names, issuer environment, rotation state, and a redacted fingerprint.

## Instructions
1. Establish the last known good time and whether Lucid status reports an incident.
2. Classify the layer: network, auth, authorization, version, payload, document permission, extension build, or connector callback.
3. Compare token type, scopes, endpoint, method, content type, and `Lucid-Api-Version` with the exact current operation page.
4. For imports, inspect archive paths, `document.json`, IDs, product, size, and media references without uploading customer content.
5. For extensions, inspect manifest scopes, package versions, build output, developer mode, and browser console evidence.
6. Reproduce with the smallest sanitized fixture and one reversible action.
7. Record the proven cause, fix, verification, rollback, and evidence gaps.

## Approval Boundaries
Do not broaden scopes, rotate credentials, alter sharing, upload documents, replay callbacks, or publish packages without owner approval.

## Output
Return symptom, layer, evidence, ruled-out causes, confirmed cause, bounded fix, verification, rollback, and owner actions.

## Error Handling
| Condition | Response |
|---|---|
| Evidence contains a secret | Stop, redact, rotate through the owner, and do not retain it. |
| Endpoint contract differs from memory | Treat current official documentation as authoritative. |
| Cause remains ambiguous | Return competing hypotheses and the smallest discriminating test. |

## Example
```text
layer=authorization; status=403; token=user; expected-scope=lucidchart.document.content:readonly; secret-retained=no; next=owner-reconsent
```

## Resources
- [Official documentation map](references/official-docs.md)

## Next Steps
Turn a confirmed recurring failure into a sanitized regression test.
