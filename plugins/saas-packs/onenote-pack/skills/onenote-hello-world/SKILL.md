---
name: onenote-hello-world
description: >-
  Prove delegated OneNote access and the selected content boundary with one minimal read-only request. Use when onboarding or diagnosing initial connectivity. Trigger with "test OneNote connection", "OneNote hello world", or "verify OneNote access".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<user-alias> <location> <fixture-id>"
version: 1.7.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, onenote, onboarding]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live OneNote actions require network access, delegated authentication, and explicit approval"
---
# OneNote Read-Only Access Proof

## Overview

Prove delegated OneNote access and the selected content boundary with one minimal read-only request.. This workflow produces an auditable decision or artifact before any live action.

## Prerequisites

- Current first-party Microsoft Graph OneNote documentation and the selected integration's tested contract.
- Named identity, content, workload, security, and operations owners appropriate to the requested scope.
- Synthetic or approved non-production fixtures with secrets and real notebook content removed.

## Current Contract

The smallest safe proof uses Graph v1.0, a delegated Notes.Read scope, and one synthetic notebook or section at the approved user, group, or site root. A successful generic Graph call does not prove OneNote access. Recheck the dated evidence map before relying on mutable permissions, limits, SDK behavior, supported resources, or cloud availability.

## Authentication

Use an approved delegated session from the runtime secret store. Record app, tenant, and user aliases plus granted scope names; never print token values.

## Instructions

1. Confirm the environment, app registration, tenant, signed-in user, Notes.Read consent, and location type.
2. Select one synthetic notebook or section owned or shared within the approved boundary.
3. Request only its identifier and display name from the v1.0 OneNote root.
4. Follow a next link only if the bounded request returns one.
5. Exercise one expected denied or nonexistent synthetic target without broadening access.
6. Remove temporary sharing if created and preserve a content-free access receipt.

## Tool Discipline

Use Read, Glob, and Grep to inspect documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Invocation alone does not authorize network access, delegated credentials, tenant or notebook content, consent, file transfer, deployment, writes, spend, sharing changes, or deletion.

## Approval Boundaries

Require the signed-in user and content owner before authorization or temporary sharing. This workflow performs no writes.

## Error Handling

- Do not claim OneNote readiness from token acquisition alone.
- Stop if the target resolves under a different user, group, site, or tenant.
- Never paste a bearer token into shell history or logs.

## Output

Return the environment, delegated identity aliases, location, scope names, allow and deny results, request identifiers, and cleanup receipt. Identify assumptions, owners, expirations, and evidence gaps explicitly.

## Examples

- Read one synthetic section name with Notes.Read.
- Show that an unrelated location remains inaccessible.

## Validation

Exercise and record these paths with expected and observed results:

- valid delegated session
- expired session
- wrong location
- denied target
- next link
- secret leakage

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources before relying on mutable behavior.
- Treat observed tenant behavior as environment-specific evidence, never a universal OneNote guarantee.
