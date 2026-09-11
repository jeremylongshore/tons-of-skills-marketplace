---
name: linktree-local-dev-loop
description: 'Rehearse Linktree-related changes locally with synthetic profile fixtures and destination checks before touching an account. Use when developing campaign tooling or a partner adapter. Trigger with "rehearse Linktree change".'
argument-hint: "[fixture-set] [change-id]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- linktree
- local-development
- fixtures
- rehearsal
model: inherit
effort: medium
compatibility: Designed for Claude Code; live work requires an authorized Linktree account and approval from the profile, Workspace, data, or partner-integration owner
---
# Linktree Synthetic Integration Rehearsal

## Overview

Provide a fast local loop for content and integration work using sanitized fixtures, deterministic validations, and no assumption of a public Linktree sandbox.

## Prerequisites

- An authorized Linktree account or a clearly bounded design-only task
- The profile, Workspace, destination, campaign, data, or integration owner appropriate to the requested change
- Current account evidence for plan-dependent features and user-supplied approved partner documentation for every private interface

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect repository specifications, sanitized fixtures, policies, tests, and prior receipts.

Use `WebFetch` only for current official Linktree documentation or explicitly approved partner documentation.

Use `Write` or `Edit` only after confirming scope, target, owners, data classification, and approval state. These tools do not confer Linktree access, account authority, or permission to process visitor data. Return exact operator steps or an approval-gated handoff when a live action is not authorized.

## Current Contract

- Public Linktree help defines the visible link and profile behaviors that synthetic fixtures may model.
- The public developer page does not promise a sandbox or publish a general automation contract.
- Partner-specific behavior must be derived from the approved contract and kept separate from public UI expectations.

## Authentication

For Admin work, use only the operator's individually provisioned Linktree account, documented Workspace role, and enabled MFA. Never request passwords, one-time codes, browser cookies, recovery codes, or session material. For partner automation, use only the authentication method, environment, scope, storage, rotation, and revocation process in the user-supplied approved partner contract. Public help pages do not establish a general API credential.

## Instructions

1. Choose one change and define acceptance checks for titles, destination hosts, order, schedule metadata, mobile rendering assumptions, and rollback.
2. Use Read, Glob, and Grep to locate sanitized profile fixtures, the destination allowlist, adapter boundary, and current tests.
3. Create or update synthetic fixtures with fake identifiers and non-sensitive example destinations; label every modeled field with its authority source.
4. Run deterministic checks for malformed URLs, disallowed hosts, duplicate campaign IDs, inaccessible labels, expired schedules, and missing owners.
5. Exercise success, validation failure, authorization failure at the adapter seam, and rollback without connecting to a Linktree account.
6. Use Write or Edit to update fixtures, tests, or the rehearsal receipt after the local scope is confirmed.
7. Use WebFetch only to verify current public Linktree behavior or approved partner documentation relevant to the model.

## Approval Boundaries

Do not import a production profile export, session data, subscriber data, or live credential into the local loop. Local success does not authorize deployment.

## Output

Return change ID, fixture provenance, validation checks, success and failure results, modeled assumptions, contract gaps, rollback result, and deployment readiness.

## Error Handling

| Condition | Response |
|---|---|
| Fixture contains real personal data | Quarantine it, notify the data owner, and replace it with synthetic values. |
| Test depends on an undocumented field | Remove the assumption or cite the approved partner contract. |
| Local result is nondeterministic | Stabilize time, ordering, and external dependencies before promotion. |

## Example

The example is a synthetic, redacted operator receipt, not proof of Linktree access or a live account change.

```text
change=campaign-42; fixtures=synthetic-v3; url-checks=pass; failure-cases=3-pass; partner-fields=none; rollback=pass; deploy-ready=no-approval
```

## Resources

- [Official documentation map](references/official-docs.md) — dated evidence and limits for this workflow.

Read the map before acting. Recheck current account and partner-specific evidence for plan-dependent or private behavior.

## Next Steps

Revalidate source dates, owner approval, target profile, and rollback readiness before repeating the workflow in another account, Workspace, campaign, region, plan, or integration.
