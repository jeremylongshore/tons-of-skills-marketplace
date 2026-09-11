---
name: linktree-sdk-patterns
description: 'Design a testable adapter around an approved Linktree partner contract without claiming a public SDK or endpoint schema. Use when implementing authorized partner automation. Trigger with "design Linktree adapter".'
argument-hint: "[contract-path] [integration-name]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- linktree
- partner-integration
- adapter
- contract-testing
model: inherit
effort: medium
compatibility: Designed for Claude Code; live work requires an authorized Linktree account and approval from the profile, Workspace, data, or partner-integration owner
---
# Linktree Partner-Contract Adapter Boundary

## Overview

Translate user-supplied partner documentation into a narrow internal port, redacted fixtures, and contract tests while keeping undocumented behavior outside the implementation.

## Prerequisites

- An authorized Linktree account or a clearly bounded design-only task
- The profile, Workspace, destination, campaign, data, or integration owner appropriate to the requested change
- Current account evidence for plan-dependent features and user-supplied approved partner documentation for every private interface

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect repository specifications, sanitized fixtures, policies, tests, and prior receipts.

Use `WebFetch` only for current official Linktree documentation or explicitly approved partner documentation.

Use `Write` or `Edit` only after confirming scope, target, owners, data classification, and approval state. These tools do not confer Linktree access, account authority, or permission to process visitor data. Return exact operator steps or an approval-gated handoff when a live action is not authorized.

## Current Contract

- Linktree publicly invites developers to register interest for APIs and SDKs and sends existing partners to its Marketplace.
- That page does not establish package names, hosts, authentication, schemas, event types, quotas, or service guarantees.
- The signed partner contract and current partner portal evidence are authoritative for private automation.

## Authentication

For Admin work, use only the operator's individually provisioned Linktree account, documented Workspace role, and enabled MFA. Never request passwords, one-time codes, browser cookies, recovery codes, or session material. For partner automation, use only the authentication method, environment, scope, storage, rotation, and revocation process in the user-supplied approved partner contract. Public help pages do not establish a general API credential.

## Instructions

1. Verify the approved partner relationship, contract revision, environment, integration owner, data classification, and permitted use cases.
2. Use Read, Glob, and Grep to inspect only the supplied contract, existing adapter, redacted fixtures, and tests; do not read credential values.
3. Create a contract table for each authorized operation: input, output, authentication method, scope, idempotency, pagination, error model, and evidence citation.
4. Define a vendor-neutral internal port that exposes only required operations and keeps transport objects behind the adapter.
5. Build synthetic contract fixtures for success, authorization failure, validation failure, throttling behavior if documented, and unknown responses.
6. Use Write or Edit for the design or implementation only after every field has contract evidence; leave unknowns as blocking questions.
7. Use WebFetch only for the public developer boundary or an explicitly approved, authenticated partner-documentation URL.

## Approval Boundaries

Never substitute a community package, guessed host, generic OAuth flow, or remembered payload for the approved private contract. Live calls require separate change authority.

## Output

Return contract revision, evidence matrix, internal port, adapter responsibilities, authentication owner, synthetic tests, unknowns, live-call boundary, and approval state.

## Error Handling

| Condition | Response |
|---|---|
| No approved contract is supplied | Stop at an interface-neutral design and request partner documentation. |
| Implementation exposes transport types | Move those types behind the adapter and preserve a stable internal port. |
| A required behavior is undocumented | Mark it unknown and obtain vendor confirmation before coding. |

## Example

The example is a synthetic, redacted operator receipt, not proof of Linktree access or a live account change.

```text
contract=partner-rev-redacted; operations=2-approved; port=ProfilePublishing; fixtures=5-synthetic; unknowns=1-blocking; live-calls=not-authorized
```

## Resources

- [Official documentation map](references/official-docs.md) — dated evidence and limits for this workflow.

Read the map before acting. Recheck current account and partner-specific evidence for plan-dependent or private behavior.

## Next Steps

Revalidate source dates, owner approval, target profile, and rollback readiness before repeating the workflow in another account, Workspace, campaign, region, plan, or integration.
