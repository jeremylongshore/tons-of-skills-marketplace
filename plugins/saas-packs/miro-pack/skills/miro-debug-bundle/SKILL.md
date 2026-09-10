---
name: miro-debug-bundle
description: "Analyze and execute this workflow: assemble a shareable Miro integration diagnostic bundle with bounded metadata and automatic redaction. Use when escalating a Miro failure. Trigger with \"build Miro debug bundle\"."
argument-hint: "[incident-id] [time-window]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- miro
- debugging
- support
model: inherit
effort: high
compatibility: Designed for Claude Code; live work requires an authorized Miro app and redacted evidence
---
# Miro Redacted Debug Bundle

## Overview

Create evidence useful to maintainers or Miro support while excluding credentials, authorization codes, board content, personal data, and unrestricted configuration; use the evidence produced here to make the next decision explicit and reviewable.

## Prerequisites

- Incident identifier and narrow UTC window
- Approved evidence destination and retention period
- Known redaction rules for identifiers, URLs, headers, and payloads

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect the repository, configuration names, adapters, tests, and evidence. Use `WebFetch` only for current official Miro documentation. Use `Write` or `Edit` after confirming the requested mode, target environment, tenant, board, and approval boundary.

## Current Contract

- Safe evidence includes versions, operation names, status/code, latency, rate headers, counts, hashes, and timestamps.
- Authorization headers, cookies, tokens, client secrets, callback query strings, and raw board payloads are never safe evidence.
- Access-token context is useful only after user/team identifiers are pseudonymized.
- Official status evidence should include observation time because incidents change.

## Authentication

For REST work, use OAuth 2.0 Authorization Code with the narrowest Miro scopes. Bind each encrypted token record to its user, application, authorized team, and granted scopes. Never print access tokens, refresh tokens, client secrets, authorization codes, or board content.

## Instructions

1. Define the incident window, failing operations, recipient, purpose, and retention.
2. Collect repository version, deployment version, app mode, safe configuration names, and dependency lock facts.
3. Extract bounded request metadata and rate headers; replace identifiers with stable incident-local hashes.
4. Record token-context match as a boolean and include no credential or raw context response.
5. Scan the bundle for bearer patterns, secrets, emails, callback codes, board text, and private URLs.
6. Review the manifest and redaction report before writing the approved artifact.

## Approval Boundaries

Do not collect raw payloads, full environment/configuration dumps, database exports, or user content without data-owner and security approval. Pause when the responsible owner or exact target is uncertain.

## Output

Return bundle path, manifest, time window, redaction counts, evidence gaps, sensitivity label, recipient, and deletion date. State what was not inspected or changed so the receipt cannot overclaim coverage.

## Error Handling

| Condition | Response |
|---|---|
| Redaction scanner matches | Quarantine the bundle and regenerate from safer fields. |
| Evidence source exceeds scope | Skip it and document the gap. |
| Timestamps disagree | Normalize to UTC and preserve original offsets. |
| Destination is not approved | Do not write or upload the bundle. |

## Examples

The example is a redacted operator receipt; identifiers are hashes or bounded labels, not board content or credentials.

```text
incident=INC-204; window=18m; requests=14; ids-hashed=9; secrets-found=0; content-fields=0; retention=7d
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Security guidelines](https://developers.miro.com/docs/security-guidelines)
- [Rate limiting](https://developers.miro.com/reference/rate-limiting)
