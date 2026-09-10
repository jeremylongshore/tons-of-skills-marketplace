---
name: webflow-data-handling
description: >-
  Design data minimization, retention, access, and deletion workflows for Webflow forms, ecommerce, CMS, logs, and webhooks. Use when personal data enters an integration or compliance evidence is needed. Trigger with "Webflow privacy", "Webflow data retention", or "delete Webflow user data".
argument-hint: "[project-path] [data-flow]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- webflow
- privacy
- data-governance
model: inherit
effort: medium
compatibility: Designed for Claude Code
---
# Webflow Data Governance

## Overview

This skill produces a repo-grounded Webflow plan or implementation. It treats current official documentation and the target project's installed versions as authority, keeps discovery read-only, and separates preparation from live mutation.

## Prerequisites

- A named target repository or project path and permission to inspect it
- The intended Webflow environment and non-secret resource identities, or a plan to discover them read-only
- Access to current official Webflow documentation; credentials stay in the user's existing secret store

## Tool Discipline

Use `Read` for repository instructions and relevant files, `Glob` to inventory manifests and Webflow integration paths, and `Grep` to locate API hosts, IDs, scopes, and credential names. Use `WebFetch` only for current official Webflow documentation. Use `Write` for a new user-requested artifact and `Edit` for minimal changes to existing files after the evidence pass.

## Current Contract

- Form submissions and ecommerce payloads can contain direct identifiers, free text, addresses, and order data; treat schemas as sensitive until classified.
- Webflow scopes control API access but do not define your legal basis, retention period, or downstream processor obligations.
- Deletion, unpublishing, and archiving have different effects. A compliance workflow must target the correct resource and verify downstream copies.
- Generated examples are operational guidance, not legal advice; policy decisions require the organization's approved legal and security owners.

## Authentication

Authenticate Data API calls with a bearer token selected for the integration: a site token for controlled single-site work, a workspace token only for its supported workspace/read use cases, or OAuth for user-authorized applications. Derive scopes from the exact endpoints. Never read, echo, persist, or place token values in commands, patches, examples, logs, or reports.

## Workflow

1. Inventory fields, event payloads, storage, logs, caches, exports, subprocessors, retention, and access roles for each data flow.
2. Classify required versus optional data and remove collection or persistence that the stated purpose does not need.
3. Redact sensitive fields before logs, traces, debug bundles, fixtures, and dead-letter queues.
4. Define access/export/delete requests as authenticated workflows with resource IDs, approvals, downstream propagation, and receipts.
5. Implement retention in each storage layer and test expiration plus legal-hold exceptions defined by policy.
6. Verify with synthetic data and report uncovered systems or unresolved policy choices to the accountable owner.

## Approval Boundaries

Default to read-only inspection. Before any create, update, delete, publish, unpublish, archive, deploy, token revoke, or webhook registration, show the exact environment and resource IDs, the proposed change, validation method, and rollback or compensating action. Proceed only when the user's request clearly authorizes that mutation; require a fresh explicit approval for production publication or destructive work.

## Output

Return the inspected project and versions, verified Webflow identities, relevant endpoint and scope contract, changes proposed or made, validation evidence, live-mutation status, rollback readiness, and remaining risks. Distinguish documented fact, repository evidence, and inference.

## Error Handling

| Condition | Response |
|---|---|
| Subject identity uncertain | Do not export or delete; escalate to the approved identity-verification process. |
| Deletion partially fails | Preserve per-system receipts and retry only after reconciling current state. |
| Policy undefined | Stop at inventory and options; do not invent a legal retention period. |

## Examples

For form submissions, retain only fields required for follow-up, redact payloads from logs, map downstream CRM copies, and make deletion an authenticated, approved, receipt-producing workflow.

## Resources

- [Official Webflow references](references/official-docs.md)
- [Webflow developer documentation](https://developers.webflow.com/)
- [Data API v2 index](https://developers.webflow.com/data/v2.0.0/llms.txt)
