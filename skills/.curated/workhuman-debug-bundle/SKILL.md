---
name: workhuman-debug-bundle
description: 'Assemble a privacy-safe Workhuman support bundle with contract, configuration, timeline, and correlation evidence. Use when escalating a tenant or managed-integration issue. Trigger with "build a Workhuman debug bundle".'
argument-hint: "[incident-id] [time-window]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.4.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, workhuman, diagnostics, privacy, support]
model: inherit
effort: high
compatibility: Designed for Claude Code; collection and disclosure must follow customer privacy, retention, legal, security, and Workhuman support rules
---
# Privacy-Safe Workhuman Support Bundle

## Overview

Create the minimum reproducible evidence package needed by customer teams or Workhuman support without exposing workforce data, messages, awards, balances, or credentials.

## Prerequisites

- Incident identifier, bounded time window, tenant and environment, symptom, severity, and support owner
- Customer classification, retention, disclosure, and legal requirements
- Current contract or connector documentation and an approved sharing channel

## Tool Discipline

Use `Read`, `Glob`, and `Grep` for local evidence discovery, `WebFetch` to verify current vendor context, and `Write` or `Edit` only inside an access-controlled redacted bundle.

## Current Contract

Workhuman processes workforce, recognition, reward, and integration data and publishes privacy and security commitments. Support evidence must follow the customer's agreement and support process; public pages do not authorize unrestricted log or payload sharing.

## Authentication

Do not collect credentials, authorization headers, session cookies, client secrets, signed URLs, or reusable tokens. Hash or truncate identifiers only when the receiving owner confirms that they remain useful.

## Instructions

1. Define the diagnostic question, audience, time window, allowed data classes, retention, and deletion owner.
2. Inventory candidate logs, configuration, contract fingerprints, deployment history, connector runs, reports, and safe correlation fields.
3. Exclude names, recognition messages, employment details, balances, addresses, financial data, secrets, raw payloads, and unrelated tenants.
4. Create a UTC timeline containing expected behavior, actual behavior, last success, first failure, changes, retries, and partial effects.
5. Include secretless topology, environment and version identifiers, schema digests, counts, sanitized statuses, and synthetic reproduction steps.
6. Run pattern and manual redaction review; record excluded classes and the reviewer.
7. Package a manifest with hashes, purpose, audience, expiry, and approved transfer channel.
8. Obtain disclosure approval before sending and record receipt and deletion expectations.

## Approval Boundaries

Do not query extra personal data, widen the incident window, decrypt archives, or send the bundle outside approved channels without privacy and support-owner approval.

## Output

Return the redacted timeline, safe configuration and topology, reproduction, schema and correlation evidence, manifest hashes, redaction proof, approvers, expiry, and transfer receipt.

## Error Handling

| Condition | Response |
|---|---|
| Necessary evidence is personal data | Minimize or tokenize it and obtain explicit disclosure authorization. |
| Bundle cannot reproduce the issue | State the limitation and request one narrowly defined additional artifact. |
| Secret scan finds a credential | Quarantine the bundle, rotate if exposed, redact, and rescan. |

## Example

A redacted completion receipt might look like this:

```text
incident=WH-42; window=15m; records=redacted-counts-only; secrets=0; manifest=sha256:...; approved=privacy+support; expires=7d
```

## Resources

- [Workhuman security and privacy](https://www.workhuman.com/why-workhuman/security-and-privacy/)
- [Workhuman privacy policy](https://www.workhuman.com/privacy-policy/)

## Next Steps

Track the vendor response against the manifest and delete the bundle at the approved expiry.
