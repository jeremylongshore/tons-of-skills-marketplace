---
name: salesforce-deploy-integration
description: 'Deploy a Salesforce-connected application through immutable artifacts, environment binding, canary traffic, reconciliation, and rollback. Use when releasing adapter code. Trigger with "deploy a Salesforce integration".'
argument-hint: "[artifact] [environment]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, salesforce, deployment, adapter, rollback]
model: inherit
effort: high
compatibility: Designed for Claude Code; application deployment and production Salesforce traffic require platform, release, and org owner approval
---
# Salesforce-Connected Application Deployment

## Overview

Release customer-owned adapter code independently of Salesforce metadata while proving the target org, secrets, API contract, and business invariants.

## Prerequisites

- Immutable application artifact, source commit, dependency lock, SBOM or equivalent inventory, and deployment target
- Approved Salesforce app and principal, target-org identity, supported API contract, and secret references
- Preview environment, canary, health and business checks, capacity budget, rollback, and incident owners

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect approved repository and evidence files, `WebFetch` to re-check current first-party Salesforce documentation, and `Write` or `Edit` only for secretless plans, fixtures, configuration, and redacted receipts.

## Current Contract

A Salesforce-connected application may run on many compute platforms; Salesforce does not define one universal deployment target. The application must bind to the customer-approved org, OAuth app, API version, limits, schema, and event contract.

## Authentication

Inject only secret references through the target platform after environment approval. Never bake Salesforce tokens, keys, usernames, org IDs, or production domains into images, frontend bundles, build logs, or artifacts.

## Instructions

1. Freeze the artifact digest, source SHA, dependencies, configuration schema, Salesforce API contract, and migration set.
2. Verify target environment, org identity expectation, app type, principal, scopes, permissions, secret references, egress, and observability.
3. Deploy to preview with synthetic Salesforce fixtures and prove startup, health, timeout, redaction, idempotency, and rollback.
4. With approval, bind an authorized sandbox and run read-only plus bounded mutation contract checks.
5. Define production canary percentage or workload, time box, stop signals, shared-limit budget, and reconciliation queries.
6. Promote the same artifact, verify org identity before traffic, monitor technical and business invariants, and halt on breach.
7. Reconcile outcomes, complete or rollback, revoke temporary access, and record artifact, deployment, and verification IDs.

## Approval Boundaries

Do not deploy a different artifact, inject production secrets, route production traffic, run migrations, or expand a canary without named approval.

## Output

Return artifact and environment identity, configuration contract, sandbox proof, canary plan, deployment IDs, signals, reconciliation, rollback status, and owners.

## Error Handling

| Condition | Response |
|---|---|
| Artifact or configuration digest changed | Stop promotion and rebuild the review evidence for the new candidate. |
| Application connects to the wrong org | Cut traffic, revoke credentials, assess data exposure, and invoke incident response. |
| Salesforce limit margin drops below the approved stop signal | Pause intake and reconcile queued work before resuming. |

## Example

A redacted completion receipt might look like this:

```text
artifact=sha256-recorded; target=production; org=matched; canary=5-percent; signals=healthy; reconciled=yes; rollback=ready
```

## Resources

- [REST API introduction](https://developer.salesforce.com/docs/platform/api-rest/guide/intro-rest.html)
- [REST API limits](https://developer.salesforce.com/docs/platform/api-rest/guide/resources-limits.html)

## Next Steps

Run the workflow first in the lowest-risk authorized org and preserve its redacted receipt. Schedule a review against the next Salesforce seasonal release and the customer change calendar.
