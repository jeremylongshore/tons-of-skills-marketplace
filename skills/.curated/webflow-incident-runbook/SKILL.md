---
name: webflow-incident-runbook
description: >-
  Triage and recover a Webflow integration incident with read-only evidence, write freezes, and verified recovery. Use when handling auth failures, 429s, 5xx errors, webhook loss, bad publication, or Cloud deploy failure. Trigger with "Webflow incident", "Webflow outage", or "Webflow rollback".
argument-hint: "[project-path] [incident-id] [environment]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- webflow
- incident-response
- reliability
model: inherit
effort: medium
compatibility: Designed for Claude Code
---
# Webflow Incident Response

## Overview

This skill produces a repo-grounded Webflow plan or implementation. It treats current official documentation and the target project's installed versions as authority, keeps discovery read-only, and separates preparation from live mutation.

## Prerequisites

- A named target repository or project path and permission to inspect it
- The intended Webflow environment and non-secret resource identities, or a plan to discover them read-only
- Access to current official Webflow documentation; credentials stay in the user's existing secret store

## Tool Discipline

Use `Read` for repository instructions and relevant files, `Glob` to inventory manifests and Webflow integration paths, and `Grep` to locate API hosts, IDs, scopes, and credential names. Use `WebFetch` only for current official Webflow documentation. Use `Write` for a new user-requested artifact and `Edit` for minimal changes to existing files after the evidence pass.

## Current Contract

- 401, 403, 429, and 5xx conditions require different action; rotating tokens is not a universal first response.
- An uncertain write must be reconciled by reading current resource state before retry.
- Webhook failures are retried only a bounded number of times and redirects, non-200s, TLS errors, and timeouts fail delivery.
- Cloud recovery must reference a specific deployment and terminal status; a previous successful deployment can be an explicit rollback target.

## Authentication

Authenticate Data API calls with a bearer token selected for the integration: a site token for controlled single-site work, a workspace token only for its supported workspace/read use cases, or OAuth for user-authorized applications. Derive scopes from the exact endpoints. Never read, echo, persist, or place token values in commands, patches, examples, logs, or reports.

## Workflow

1. Declare severity, affected environment/sites, user impact, start time, incident owner, and whether live writes are frozen.
2. Check Webflow status and your own service independently; capture redacted structured errors, headers, deployment IDs, and webhook evidence.
3. Classify the failure: identity/auth, permission, budget, Webflow service, application, webhook, content state, or deployment.
4. Contain without guessing: pause workers, stop publication, serve an approved cached fallback, or isolate the failing tenant.
5. Apply one evidence-backed remediation with a rollback. Reconcile every uncertain write before resuming.
6. Verify read and write paths, staged/live state, webhook delivery, rate headroom, and public routes; record timeline and follow-up actions.

## Approval Boundaries

Default to read-only inspection. Before any create, update, delete, publish, unpublish, archive, deploy, token revoke, or webhook registration, show the exact environment and resource IDs, the proposed change, validation method, and rollback or compensating action. Proceed only when the user's request clearly authorizes that mutation; require a fresh explicit approval for production publication or destructive work.

## Output

Return the inspected project and versions, verified Webflow identities, relevant endpoint and scope contract, changes proposed or made, validation evidence, live-mutation status, rollback readiness, and remaining risks. Distinguish documented fact, repository evidence, and inference.

## Error Handling

| Condition | Response |
|---|---|
| 401/403 | Verify token type, revocation, identity, and endpoint scope before considering rotation. |
| 429 | Honor `Retry-After`, coordinate shared-key workers, and reduce concurrency. |
| Bad live content | Freeze further publishes and execute the approved item-level or deployment recovery plan. |

## Examples

For a 429 storm, freeze nonessential workers, record per-key headers and callers, honor `Retry-After`, restore a shared queue below the plan budget, and verify headroom before reopening writes.

## Resources

- [Official Webflow references](references/official-docs.md)
- [Webflow developer documentation](https://developers.webflow.com/)
- [Data API v2 index](https://developers.webflow.com/data/v2.0.0/llms.txt)
