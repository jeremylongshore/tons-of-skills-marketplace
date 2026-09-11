---
name: instantly-security-basics
description: >-
  Harden Instantly API v2 keys, scopes, tenant boundaries, logs, webhooks, and operational access. Use when operating security basics workflows. Trigger with "instantly security basics", "Instantly API", or "Instantly integration".
argument-hint: "[repository-path] [workspace]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.13.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- instantly
- security-basics
model: inherit
effort: high
compatibility: Designed for Claude Code; live verification requires network access and an approved Instantly workspace and API v2 key
---
# Instantly Integration Security Baseline

## Overview

Produce a verified security baseline with least privilege and explicit remediation approvals. Record assumptions, evidence, approval state, and rollback ownership so another operator can reproduce the result.

## Prerequisites

- The target repository, Instantly workspace, environment, and accountable owner
- Current security, privacy, compliance, capacity, and change-control requirements
- An approved API v2 key only when a bounded live verification is necessary

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect code, configuration, and evidence. Use `WebFetch` only for current first-party Instantly documentation and package metadata. Use `Write` or `Edit` only when implementation was requested and exact target files are known; never write credentials, lead data, email content, or unrestricted environment output.

## Current Contract

- Keys are bearer credentials displayed once; store them only in approved server-side secret systems.
- Scopes can be resource/action-specific and revoked through API-key controls.
- Webhook payloads can contain sensitive lead and message content; the public guide does not establish a signature secret.

## Authentication

Use an API v2 key as `Authorization: Bearer <key>` against `https://api.instantly.ai/api/v2`. Grant only the endpoint-specific scopes needed, inject the key from an approved server-side secret manager, and never print, persist, commit, or place it in a URL. Treat key creation, rotation, revocation, member changes, workspace delegation, and production access as owner-approved actions.

## Instructions

1. Inventory secrets, scopes, members, service identities, workspace-group delegation, and webhook destinations.
2. Remove browser exposure, query-string keys, plaintext configs, and unrestricted environment logging.
3. Map each call to least-privilege scopes and validate denied operations.
4. Enforce TLS, request-size bounds, schema validation, idempotency, and payload minimization at webhook receivers.
5. Review audit logs and establish key rotation/revocation and incident ownership.
6. Prepare changes with blast radius, approval, verification, and rollback evidence.

## Approval Boundaries

Do not create, rotate, reveal, or revoke keys; invite or remove members; delegate across workspaces; connect sending accounts; create or activate campaigns; import or delete leads; change suppression or retention; register, patch, resume, or delete webhooks; alter plans or paid capacity; transmit diagnostics; or perform another production mutation without explicit approval from the accountable owner. Keep diagnosis read-only unless implementation was requested.

## Output

Return the workspace-safe scope, files and contracts inspected, exact API v2 routes and required scopes, evidence collected, validation result, sensitive fields redacted, remaining risk, accountable owner, approval state, and rollback or next action.

## Error Handling

| Condition | Response |
|---|---|
| `401` | Stop and verify that the bearer key exists, is current, and was not revoked. |
| `403` | Stop and compare the operation with its exact required scope; do not broaden to `all:all` by default. |
| `429` | Coordinate the workspace-wide budget, honor endpoint overrides, and bound retries. |
| Schema or tenant mismatch | Fail closed, preserve redacted evidence, and do not retry a mutation. |

## Examples

Use a compact handoff that makes scope, mutation authority, and evidence reviewable.

Input:

```text
mode=audit; secrets=references-only; webhook-signature=not-assumed
```

Expected handoff:

```text
findings=prioritized; credentials=redacted; changes=awaiting-owner
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Instantly API v2 documentation](https://developer.instantly.ai/)
- [Instantly API v2 OpenAPI document](https://api.instantly.ai/openapi/api_v2.json)
