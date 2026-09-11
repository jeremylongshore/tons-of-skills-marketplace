---
name: lucidchart-deploy-integration
description: 'Package, validate, stage, publish, and roll back a Lucid extension or data connector. Use when moving a tested Lucid integration beyond local development. Trigger with "deploy Lucid integration".'
argument-hint: "[project-path] [target-environment]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, lucidchart, deployment, extensions, data-connectors]
model: inherit
effort: high
compatibility: Designed for Claude Code; upload, publication, OAuth registration, connector deployment, and rollback require explicit owner approval
---
# Governed Lucid Integration Deployment

## Overview

Move a Lucid extension and any companion data connector through reproducible build, canary, publication, and rollback gates using current official tooling.

## Prerequisites

- A clean reviewed revision with passing local build, type, manifest, fixture, and secret scans
- Environment owners, approved scopes, release notes, canary users, and rollback artifact
- Current `lucid-package` and project-specific connector deployment instructions

## Tool Discipline

Use `Read`, `Glob`, and `Grep` for repository and release evidence, `WebFetch` for current Lucid publication contracts, and `Write` or `Edit` only for local manifests, receipts, and release notes.

## Current Contract

Lucid editor extensions use the official package CLI and Extension SDK. A data connector is a separately operated server component with its own identity, hosting, secrets, observability, and rollback. Verify installed CLI syntax rather than relying on cached commands.

## Authentication

Separate developer, publisher, connector-runtime, and source-system identities. Keep credentials in approved secret stores; use least privilege and ensure rollback does not depend on an expired personal token.

## Instructions

1. Pin source revision, CLI/SDK versions, manifest, scopes, connector image, fixtures, and documentation.
2. Run the repository's secretless build, type, manifest, fixture, and compatibility gates.
3. Produce immutable extension and connector artifacts with checksums and provenance.
4. Compare requested scopes, OAuth redirects, data flows, and webhook behavior with the reviewed release.
5. Present artifact digests, target, canary cohort, expected mutations, monitoring, and rollback commands for approval.
6. After approval, upload or deploy only to the documented staging/developer target and run the canary.
7. Reconcile UI behavior, connector data, permissions, errors, and service health before production publication.
8. Require a second approval for production publication or traffic change; retain the prior artifact until the rollback window closes.

## Approval Boundaries

Never publish, change OAuth settings, expose a connector, rotate production secrets, or promote traffic implicitly.

## Output

Return source revision, artifact digests, version evidence, scopes, approvals, canary results, publication receipt, monitoring, and rollback status.

## Error Handling

| Condition | Response |
|---|---|
| Installed CLI differs from instructions | Use current `--help` and official docs; stop and update the plan. |
| Canary has auth or data drift | Halt promotion and roll back the canary artifact. |
| Previous artifact cannot be restored | Do not deploy until a tested rollback exists. |

## Example

```text
revision=abc123; extension-sha256=...; target=developer; canary=3/3; production=not-approved; rollback=verified
```

## Resources

- [Official documentation map](references/official-docs.md)

## Next Steps

Promote only with production-owner approval and evidence that the canary and rollback gates passed.
