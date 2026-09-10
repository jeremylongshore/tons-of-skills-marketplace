---
name: attio-prod-checklist
description: >-
  Run an evidence-based production-readiness review for an Attio integration across identity, scopes, data ownership, retries, webhooks, observability, rollback, and support. Use when preparing to enable production Attio traffic. Trigger with "Attio production checklist", "Attio go-live", or "review Attio release".
argument-hint: "[repository-path] [release-id]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.7.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- attio
- production
model: inherit
effort: high
compatibility: Designed for Claude Code
---
# Attio Production Readiness Review

## Overview

This skill produces a release decision from repository and operational evidence. A checked box without a receipt is unresolved, not complete.

## Prerequisites

- Exact artifact, environment, workspace, and release owner
- Endpoint inventory with methods and required scopes
- Data ownership, retention, and deletion policy
- Monitoring, incident, rollback, and support paths

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect auth, mappings, tests, workflows, observability, and rollback code. Use `WebFetch` only for current official Attio documentation. Use `Write` or `Edit` only to remediate a named gap with verification.

## Current Contract

- Authentication must match the tenancy model and use endpoint-derived least privilege.
- Record and entry identity, owned fields, and destructive boundaries must be explicit.
- Retries must honor `Retry-After` and exclude permanent request failures.
- Webhook receivers need raw-body HMAC verification and idempotent processing.
- Pagination mode must be confirmed endpoint by endpoint.

## Authentication

Verify secret location, workspace or tenant binding, scopes, rotation owner, revocation procedure, and absence from logs and artifacts. Use Bearer authentication for REST requests.

## Instructions

1. Bind the review to the exact artifact, environment, workspace, and endpoint inventory.
2. Verify contract tests, schema discovery, field ownership, identity, and pagination termination.
3. Verify credential storage, endpoint scopes, tenant isolation, rotation, and redaction.
4. Verify timeouts, bounded retries, read/write traffic controls, and 429 handling.
5. For webhooks, verify HTTPS, raw-body signature checks, idempotency keys, quick acknowledgement, and replay-safe workers.
6. Exercise read-only smoke, approved canary, alert path, rollback, and recovery evidence.
7. Record PASS, FAIL, or explicitly accepted risk for every item and name the approver.

## Approval Boundaries

Only the release owner may accept unresolved data-loss, authorization, privacy, or rollback risk. Do not convert missing evidence into PASS.

## Output

Return the bound release identity, control matrix with receipts, failed gates, accepted risks, approvers, and final GO or NO-GO decision.

## Error Handling

| Condition | Response |
|---|---|
| Artifact or workspace is unbound | Return NO-GO. |
| Scope evidence is missing | Return NO-GO until endpoint mapping exists. |
| Webhook replay is untested | Disable webhook-driven mutation or return NO-GO. |
| Rollback cannot be exercised | Limit rollout or return NO-GO. |

## Examples

Input:

```text
release=exact-sha; workspace=production-alias; canary=approved-record
```

Expected handoff:

```text
decision=NO-GO; blocker=missing webhook replay proof; owner=integration-team
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Authentication](https://docs.attio.com/rest-api/guides/authentication)
- [Rate limiting](https://docs.attio.com/rest-api/guides/rate-limiting)
- [Configuring webhooks](https://docs.attio.com/rest-api/guides/webhooks)
