---
name: onenote-install-auth
description: >-
  Establish a least-privilege delegated Microsoft Graph connection for OneNote with tested consent and lifecycle controls. Use when registering or repairing OneNote authentication. Trigger with "set up OneNote auth", "register OneNote app", or "review Notes permissions".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<account-type> <tenant> <environment>"
version: 1.7.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, onenote, authentication]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live OneNote actions require network access, delegated authentication, and explicit approval"
---
# OneNote Delegated Authentication Intake

## Overview

Establish a least-privilege delegated Microsoft Graph connection for OneNote with tested consent and lifecycle controls.. This workflow produces an auditable decision or artifact before any live action.

## Prerequisites

- Current first-party Microsoft Graph OneNote documentation and the selected integration's tested contract.
- Named identity, content, workload, security, and operations owners appropriate to the requested scope.
- Synthetic or approved non-production fixtures with secrets and real notebook content removed.

## Current Contract

The OneNote service-specific overview says app-only authentication is unsupported. Use a delegated authorization flow and choose Notes.Create, Notes.Read, or Notes.ReadWrite according to the operation; treat conflicting generic application-permission tables as documentation drift, not authorization to deploy client credentials. Recheck the dated evidence map before relying on mutable permissions, limits, SDK behavior, supported resources, or cloud availability.

## Authentication

Record app registration, account type, tenant, redirect URI, signed-in user, requested and granted delegated scopes, token-cache location, expiry, revocation, and reauthentication without storing secret values.

## Instructions

1. Classify the account as personal Microsoft or work or school and resolve the approved tenant boundary.
2. Register the application and exact redirect URI through the approved identity workflow.
3. Choose the minimum delegated Notes scope from the required read, create, or update operations.
4. Implement authorization-code or device flow appropriate to the client and protect token-cache material.
5. Run one synthetic read-only OneNote request and compare requested with granted scopes.
6. Document consent withdrawal, token-cache deletion, reauthentication, owner transfer, and production promotion.

## Tool Discipline

Use Read, Glob, and Grep to inspect documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Invocation alone does not authorize network access, delegated credentials, tenant or notebook content, consent, file transfer, deployment, writes, spend, sharing changes, or deletion.

## Approval Boundaries

Require the signed-in user for delegated consent and the tenant administrator when policy requires it. Require security approval for multitenant distribution, public clients, redirect changes, or production token storage.

## Error Handling

- Do not use client credentials or the default application scope for OneNote calls.
- Stop when generic permission metadata conflicts with the service-specific support statement.
- Never commit client secrets, tokens, or serialized caches.

## Output

Return the account and tenant model, app and redirect aliases, delegated scope matrix, consent evidence, synthetic check, lifecycle owners, and gaps. Identify assumptions, owners, expirations, and evidence gaps explicitly.

## Examples

- Onboard read-only access with Notes.Read and prove a write is unavailable.
- Revoke consent and verify the client enters a recoverable reauthentication state.

## Validation

Exercise and record these paths with expected and observed results:

- personal account
- tenant account
- consent denied
- wrong redirect
- revocation
- app-only rejection

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources before relying on mutable behavior.
- Treat observed tenant behavior as environment-specific evidence, never a universal OneNote guarantee.
