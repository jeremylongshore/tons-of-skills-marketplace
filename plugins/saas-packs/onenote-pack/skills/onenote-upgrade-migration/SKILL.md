---
name: onenote-upgrade-migration
description: >-
  Migrate a OneNote integration across auth, SDK, request, or unsupported-feature assumptions with canaries and rollback. Use when replacing app-only access, upgrading dependencies, or removing undocumented polling shortcuts. Trigger with "upgrade OneNote integration", "migrate OneNote auth", or "remove OneNote delta".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<current-contract> <target-contract> <migration-window>"
version: 1.7.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, onenote, migration]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live OneNote actions require network access, delegated authentication, and explicit approval"
---
# OneNote Contract Migration

## Overview

Migrate a OneNote integration across auth, SDK, request, or unsupported-feature assumptions with canaries and rollback.. This workflow produces an auditable decision or artifact before any live action.

## Prerequisites

- Current first-party Microsoft Graph OneNote documentation and the selected integration's tested contract.
- Named identity, content, workload, security, and operations owners appropriate to the requested scope.
- Synthetic or approved non-production fixtures with secrets and real notebook content removed.

## Current Contract

A safe migration distinguishes Graph v1.0 from SDK version, delegated auth from obsolete app-only paths, supported hierarchy paging from undocumented search or delta, and scheduled reconciliation from unsupported OneNote change notifications. Recheck the dated evidence map before relying on mutable permissions, limits, SDK behavior, supported resources, or cloud availability.

## Authentication

Replace application credentials with an approved delegated lifecycle. Preserve tenant, user, scopes, redirect, consent, encrypted cache, revocation, and reauthentication evidence throughout rollout.

## Instructions

1. Inventory every OneNote auth flow, SDK call, REST route, location, paging loop, HTML operation, event assumption, and fixture.
2. Trace each behavior to current first-party documentation and classify supported, contradicted, undocumented, or environment-observed.
3. Define the target client boundary and compatibility fixtures without changing live state.
4. Migrate app-only, reconstructed paging, search, delta, webhook, fixed-limit, and Retry-After assumptions.
5. Canary one delegated user and synthetic root with rollback and dual-read comparison where safe.
6. Reconcile results, remove obsolete credentials and dead paths, and publish the final compatibility receipt.

## Tool Discipline

Use Read, Glob, and Grep to inspect documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Invocation alone does not authorize network access, delegated credentials, tenant or notebook content, consent, file transfer, deployment, writes, spend, sharing changes, or deletion.

## Approval Boundaries

Require identity and security approval for auth migration, content-owner approval for live reads or writes, and release approval for cutover and old-secret removal.

## Error Handling

- Do not keep client credentials as an emergency OneNote fallback.
- Do not replace unsupported delta with an unbounded all-pages scan.
- Roll back on count, content, location, or user-binding drift.

## Output

Return the inventory, evidence classification, target contract, code and fixture changes, canary comparison, cutover decision, cleanup, and rollback. Identify assumptions, owners, expirations, and evidence gaps explicitly.

## Examples

- Replace a client-credential job with delegated session ownership.
- Replace an undocumented pages-delta loop with section-scoped polling and reconciliation.

## Validation

Exercise and record these paths with expected and observed results:

- auth migration
- SDK change
- paging
- HTML
- unsupported event
- rollback

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources before relying on mutable behavior.
- Treat observed tenant behavior as environment-specific evidence, never a universal OneNote guarantee.
