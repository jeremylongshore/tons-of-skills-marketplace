---
name: miro-security-basics
description: "Audit and harden repository-side Miro OAuth, session, storage, scope, logging, and board-data controls against common integration failures. Use when security-reviewing a Miro app. Trigger with \"secure Miro integration\"."
argument-hint: "[environment] [threat-scope]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.9.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- miro
- security
- oauth
model: inherit
effort: high
compatibility: Designed for Claude Code; live work requires an authorized Miro app and redacted evidence
---
# Miro Integration Security Baseline

## Overview

Apply a minimum security baseline tied to Miro's supported authorization model and the app's actual data flows. Eliminate obsolete webhook assumptions from the threat model; use the evidence produced here to make the next decision explicit and reviewable.

## Prerequisites

- Data-flow and trust-boundary diagram
- App configuration, scopes, token mode, and storage design
- Threat model and approved data-retention policy

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect the repository, configuration names, adapters, tests, and evidence. Use `WebFetch` only for current official Miro documentation. Use `Write` or `Edit` after confirming the requested mode, target environment, tenant, board, and approval boundary. These declared tools do not call authenticated Miro APIs or deployment CLIs; implement client, configuration, and test changes, then return exact operator commands or an approval-gated handoff for live execution.

## Current Contract

- Miro requires OAuth 2.0 for REST apps and tells Marketplace apps not to request user credentials.
- Every request must be authenticated and authorized; stored Miro user data requires its own access control.
- Session cookies should be `HttpOnly` and `Secure`; OAuth callbacks require session-bound state validation.
- The retired experimental webhook service provides no current server-to-server signature contract to implement.

## Authentication

For REST work, use OAuth 2.0 Authorization Code with the narrowest Miro scopes. Bind each encrypted token record to its user, application, authorized team, and granted scopes. Never print access tokens, refresh tokens, client secrets, authorization codes, or board content.

## Instructions

1. Map entry points, OAuth redirects, sessions, tokens, board data, logs, exports, and administrators.
2. Minimize scopes and verify authorization again at each server-side tenant/resource boundary.
3. Encrypt tokens at rest, restrict decryption, serialize refresh rotation, and provide revocation/deletion paths.
4. Set secure cookie, CSRF, frame/origin, redirect, input-validation, and outbound-host controls appropriate to the app.
5. Redact credentials and content from telemetry; scan dependencies and production bundles for accidental exposure.
6. Test cross-tenant denial, revoked tokens, stale sessions, malformed inputs, and data deletion; record residual risks.

## Approval Boundaries

Do not add scopes, retain board content, weaken cookie/CSRF controls, or introduce an experimental platform dependency without security and data-owner approval. Pause when the responsible owner or exact target is uncertain.

## Output

Return threat boundaries, scope diff, control evidence, negative-test results, data-retention map, open risks, and remediation owners. State what was not inspected or changed so the receipt cannot overclaim coverage.

## Error Handling

| Condition | Response |
|---|---|
| Cross-tenant read succeeds | Disable the affected path and treat it as a security incident. |
| Credential appears in logs | Restrict access, rotate/revoke it, purge under policy, and repair redaction. |
| State validation is absent | Block OAuth completion until it is implemented. |
| Unsupported event contract is assumed | Remove the claim and redesign around supported reads or in-board events. |

## Examples

The example is a redacted operator receipt; identifiers are hashes or bounded labels, not board content or credentials.

```text
scopes=boards:read; state=verified; tokens=encrypted; tenant-negative-tests=passed; log-secrets=0; residual=2-low
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Security guidelines](https://developers.miro.com/docs/security-guidelines)
- [Scopes](https://developers.miro.com/reference/scopes)
