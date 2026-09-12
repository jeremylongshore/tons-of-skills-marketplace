---
name: notion-enterprise-rbac
description: >-
  Map Notion connection capabilities, content access, user context, and application roles into an auditable authorization model. Use when designing multi-workspace or enterprise controls. Trigger with "review Notion RBAC", "map Notion permissions", or "audit Notion tenant access".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<connection-model> <workspace-scope> <role-model>"
version: 1.40.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, notion, authorization]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Notion actions require network access and explicit approval"
---
# Notion Enterprise Authorization Boundary Review

## Overview

Map Notion connection capabilities, content access, user context, and application roles into an auditable authorization model.. This workflow produces an auditable decision or artifact before any live action.

## Prerequisites

- Current first-party Notion documentation and the selected integration's tested API-version contract.
- A named workspace owner, content or data owner, and operation owner.
- Synthetic or approved non-production fixtures with secrets and workspace content removed.

## Current Contract

Notion connection capabilities, page sharing, installer authority, personal-token user permissions, application roles, and enterprise admin APIs are distinct control planes. None should be presented as universal Notion RBAC. Recheck the dated evidence map before relying on mutable fields, endpoints, versions, limits, or delivery behavior.

## Authentication

Record internal connection, public OAuth connection, or personal access token explicitly. For public OAuth, bind encrypted tokens and refresh state to the correct workspace and installation.

## Instructions

1. Inventory actors, workspace and tenant boundaries, connection types, capabilities, shared roots, and application roles.
2. Build an operation matrix for read, insert, update, comments, user information, webhook, and administrative surfaces.
3. Calculate effective access as the intersection of token model, capabilities, content sharing, user authority, and application policy.
4. Design authorization checks at every job, cache, queue, and destination boundary.
5. Add joiner, mover, leaver, reauthorization, revocation, and workspace-removal workflows.
6. Review exceptions, separation of duties, audit evidence, and recertification cadence.

## Tool Discipline

Use Read, Glob, and Grep to inspect documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Invocation alone does not authorize network access, credentials, workspace content, user data, file transfer, deployment, capability or sharing changes, writes, spend, or deletion.

## Approval Boundaries

Require workspace admin, security, and data-owner approval for new capabilities, workspace-wide access, user-email access, administrative APIs, or cross-workspace processing.

## Error Handling

- Do not equate a successful token exchange with access to all workspace content.
- Do not use application roles to conceal an overprivileged Notion token.
- Fail closed when workspace binding is missing.

## Output

Return the actor-resource-operation matrix, effective-access rules, tenant-binding model, lifecycle workflows, exceptions, and recertification owner. Identify assumptions, owners, expirations, and evidence gaps explicitly.

## Examples

- Prove a read-only connection cannot update a page.
- Revoke one workspace installation without affecting another tenant.

## Validation

Exercise and record these paths with expected and observed results:

- capability denial
- unshared content
- tenant swap
- revoked grant
- role change
- recertification

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources before relying on mutable behavior.
- Treat observed tenant behavior as environment-specific evidence, never a universal Notion guarantee.
