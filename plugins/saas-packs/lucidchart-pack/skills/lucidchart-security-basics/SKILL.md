---
name: lucidchart-security-basics
description: 'Threat-model and harden Lucid API, Standard Import, editor extension, and data connector integrations. Use when reviewing secrets, scopes, data flows, or release security. Trigger with "secure Lucid integration".'
argument-hint: "[project-path] [surface]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, lucidchart, security, oauth, least-privilege]
model: inherit
effort: high
compatibility: Designed for Claude Code; credential, scope, data-retention, publication, and production-remediation decisions require security and resource-owner approval
---
# Lucid Integration Security Baseline

## Overview

Establish least privilege, safe data handling, trustworthy package boundaries, and auditable operations for the exact Lucid integration surface.

## Prerequisites

- Architecture and data-flow inventory with classifications and owners
- Credential/principal and extension-scope inventory
- Repository, artifact, deployment, logging, retention, and incident evidence

## Tool Discipline

Use `Read`, `Glob`, and `Grep` for bounded static inspection, `WebFetch` for current Lucid security contracts, and `Write` or `Edit` only for approved local remediation and redacted reports.

## Current Contract

Lucid exposes multiple credential classes, operation-specific scopes/headers, Standard Import archives, editor-extension scopes, and optional connector runtimes. Each creates distinct trust boundaries; an extension bundle is not a safe place for confidential credentials.

## Authentication

Map API keys and OAuth user/account tokens to an owner, exact scopes/resources, storage, expiration, rotation, revocation, and audit trail. Validate OAuth redirect URIs and state. Never log tokens, authorization codes, refresh tokens, cookies, or signed URLs.

## Instructions

1. Pin the reviewed revision and enumerate actors, components, data stores, network edges, documents, and source systems.
2. Re-fetch authentication, scope, header, and surface-specific official docs.
3. Search tracked files and build artifacts for credentials, unsafe environment files, overly broad scopes, sensitive fixtures, and unredacted logs.
4. Threat-model credential theft, malicious imports, archive traversal/expansion, injected source data, cross-account access, connector compromise, replay, and supply-chain drift.
5. Validate inputs, archive paths/sizes/types, stable IDs, outputs, redirects, state, authorization, tenant boundaries, and redaction.
6. Verify pinned dependencies, reproducible builds, artifact provenance, change review, secretless CI, and rollback.
7. Rank findings by exploitability and impact; propose reversible fixes with owners and evidence.
8. Present credential, scope, retention, or production changes for explicit approval and verify remediation independently.

## Approval Boundaries

Do not inspect secret values, rotate/revoke credentials, alter scopes, delete data, change retention, or publish security-sensitive changes without authorization.

## Output

Return surfaces, trust boundaries, principal/scope matrix, findings with evidence, severity, remediation, approvals, verification, and residual risk.

## Error Handling

| Condition | Response |
|---|---|
| Active secret appears in tracked data | Stop exposure, avoid repeating it, and escalate rotation through the owner. |
| Scope requirement is unclear | Deny the capability until the exact documented scope is established. |
| Archive or source data is untrusted | Quarantine and validate offline before any upload or rendering. |

## Example

```text
surface=extension+connector; critical=0; high=1; bundle-secrets=0; least-scope=partial; production-mutations=0
```

## Resources

- [Official documentation map](references/official-docs.md)

## Next Steps

Remediate highest-risk findings, rotate through accountable owners, and rerun the same evidence-backed checks.
