---
name: linktree-hello-world
description: 'Run the smallest documented Linktree publish-and-verify workflow without inventing an API. Use when launching a profile or proving a new Linktree setup. Trigger with "smoke test Linktree".'
argument-hint: "[profile-url] [test-destination]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- linktree
- smoke-test
- publishing
- link-qa
model: inherit
effort: medium
compatibility: Designed for Claude Code; live work requires an authorized Linktree account and approval from the profile, Workspace, data, or partner-integration owner
---
# Linktree First-Publish Smoke Test

## Overview

Prove one bounded path from an approved destination to a visible classic link, then verify the visitor experience on mobile and desktop before broader promotion.

## Prerequisites

- An authorized Linktree account or a clearly bounded design-only task
- The profile, Workspace, destination, campaign, data, or integration owner appropriate to the requested change
- Current account evidence for plan-dependent features and user-supplied approved partner documentation for every private interface

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect repository specifications, sanitized fixtures, policies, tests, and prior receipts.

Use `WebFetch` only for current official Linktree documentation or explicitly approved partner documentation.

Use `Write` or `Edit` only after confirming scope, target, owners, data classification, and approval state. These tools do not confer Linktree access, account authority, or permission to process visitor data. Return exact operator steps or an approval-gated handoff when a live action is not authorized.

## Current Contract

- Linktree documents classic links and Link Apps as separate experiences created from the Links area.
- A classic link sends a visitor to the configured destination; an app can embed an experience on the profile.
- The public developer page invites registration for broader API and SDK access; it is not a public automation specification.

## Authentication

For Admin work, use only the operator's individually provisioned Linktree account, documented Workspace role, and enabled MFA. Never request passwords, one-time codes, browser cookies, recovery codes, or session material. For partner automation, use only the authentication method, environment, scope, storage, rotation, and revocation process in the user-supplied approved partner contract. Public help pages do not establish a general API credential.

## Instructions

1. Confirm the authorized account, profile URL, approved destination, owner, rollback action, and test window.
2. Inspect local campaign copy, destination inventory, and acceptance notes with Read, Glob, and Grep; do not search credential files.
3. In Linktree Admin, add one classic link with an unambiguous title and the approved destination, leaving unrelated links unchanged.
4. Open the public profile in a signed-out mobile viewport and desktop viewport; confirm title, placement, destination, HTTPS, and expected redirect chain.
5. Exercise one safe failure path with a deliberately unpublished draft or a nonproduction destination, then confirm visitors cannot reach it.
6. Use Write or Edit to record a redacted receipt containing timestamps, expected and actual destination hosts, and rollback status.
7. Use WebFetch only to recheck the current official Linktree guidance when UI labels or feature availability differ.

## Approval Boundaries

Do not publish a campaign, collect visitor data, or change an established destination without the profile owner and campaign owner approving the exact change.

## Output

Return profile, link title, destination host, viewport checks, redirect result, failure-path result, rollback state, evidence location, and go/no-go. Separate observed facts from assumptions.

## Error Handling

| Condition | Response |
|---|---|
| Destination redirects unexpectedly | Pause publication and have the destination owner approve the complete redirect chain. |
| Link is visible before approval | Disable it immediately and record the exposure window. |
| Admin labels differ from the guide | Stop guessing and recheck current official help. |

## Example

The example is a synthetic, redacted operator receipt, not proof of Linktree access or a live account change.

```text
profile=/launch; item=Spring catalog; mobile=pass; desktop=pass; redirect=approved-host; failure-path=pass; rollback=ready; result=go
```

## Resources

- [Official documentation map](references/official-docs.md) — dated evidence and limits for this workflow.

Read the map before acting. Recheck current account and partner-specific evidence for plan-dependent or private behavior.

## Next Steps

Revalidate source dates, owner approval, target profile, and rollback readiness before repeating the workflow in another account, Workspace, campaign, region, plan, or integration.
