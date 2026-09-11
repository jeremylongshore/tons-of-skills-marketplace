---
name: linktree-ci-integration
description: 'Gate repository-managed Linktree campaign specifications with deterministic static and synthetic checks. Use when adding CI around profile content or an approved partner adapter. Trigger with "add Linktree CI".'
argument-hint: "[spec-path] [ci-provider]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- linktree
- ci
- content-validation
- supply-chain
model: inherit
effort: medium
compatibility: Designed for Claude Code; live work requires an authorized Linktree account and approval from the profile, Workspace, data, or partner-integration owner
---
# Linktree Content Change CI Gate

## Overview

Turn profile and campaign policy into a fail-closed repository gate without logging in to Linktree or requiring production secrets in pull-request jobs.

## Prerequisites

- An authorized Linktree account or a clearly bounded design-only task
- The profile, Workspace, destination, campaign, data, or integration owner appropriate to the requested change
- Current account evidence for plan-dependent features and user-supplied approved partner documentation for every private interface

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect repository specifications, sanitized fixtures, policies, tests, and prior receipts.

Use `WebFetch` only for current official Linktree documentation or explicitly approved partner documentation.

Use `Write` or `Edit` only after confirming scope, target, owners, data classification, and approval state. These tools do not confer Linktree access, account authority, or permission to process visitor data. Return exact operator steps or an approval-gated handoff when a live action is not authorized.

## Current Contract

- Public Admin documentation can ground link-type, order, schedule, and visible-content expectations.
- A CI job cannot prove a live profile state unless an approved, documented partner interface explicitly provides that evidence.
- Fork and pull-request workflows must remain secretless and synthetic.

## Authentication

For Admin work, use only the operator's individually provisioned Linktree account, documented Workspace role, and enabled MFA. Never request passwords, one-time codes, browser cookies, recovery codes, or session material. For partner automation, use only the authentication method, environment, scope, storage, rotation, and revocation process in the user-supplied approved partner contract. Public help pages do not establish a general API credential.

## Instructions

1. Define the protected specification format, owners, required reviews, destination policy, schedule format, and evidence retained by CI.
2. Use Read, Glob, and Grep to inspect workflow files, campaign fixtures, ownership rules, and existing tests.
3. Add static checks for schema, HTTPS destinations, host policy, duplicate identifiers, title limits defined by local policy, timezone presence, and rollback metadata.
4. Add synthetic rendering or adapter contract tests that do not contact Linktree and cannot consume production session material.
5. Make the gate fail closed on validation errors and report concise, redacted diagnostics suitable for untrusted pull requests.
6. Use Write or Edit to modify the workflow and tests after confirming branch-protection expectations and generated-file ownership.
7. Use WebFetch only to verify public behavior or approved partner documentation; never fetch and execute remote code in CI.

## Approval Boundaries

Do not expose secrets to fork jobs, mutate a live profile from pull-request CI, or label a synthetic check as end-to-end production proof.

## Output

Return protected paths, checks, fixtures, secret exposure count, failure behavior, required context, evidence retention, and remaining live verification.

## Error Handling

| Condition | Response |
|---|---|
| Fork job requests a credential | Remove the live dependency and replace it with a synthetic contract fixture. |
| Generated output drifts | Regenerate through the canonical producer and fail the gate on subsequent drift. |
| Check can pass without reading the specification | Fix the test denominator so the intended files are always evaluated. |

## Example

The example is a synthetic, redacted operator receipt, not proof of Linktree access or a live account change.

```text
spec=campaigns/*.yaml; checks=7; fixtures=synthetic; fork-secrets=0; mutation=none; required-context=linktree-content; result=pass
```

## Resources

- [Official documentation map](references/official-docs.md) — dated evidence and limits for this workflow.

Read the map before acting. Recheck current account and partner-specific evidence for plan-dependent or private behavior.

## Next Steps

Revalidate source dates, owner approval, target profile, and rollback readiness before repeating the workflow in another account, Workspace, campaign, region, plan, or integration.
