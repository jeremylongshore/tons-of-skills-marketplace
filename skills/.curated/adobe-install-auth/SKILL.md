---
name: adobe-install-auth
description: >-
  Select and prove the correct Adobe authentication model, entitlement, product profile, and secret lifecycle before integration work. Use when creating or repairing Adobe credentials. Trigger with "set up Adobe auth", "Adobe OAuth server-to-server", or "Adobe user authentication".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<product-api> <data-owner> <environment>"
version: 1.8.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, adobe, authentication]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Adobe actions require network access, appropriate entitlement and authentication, and explicit approval"
---
# Adobe Authentication and Entitlement Intake

## Overview

Select and prove the correct Adobe authentication model, entitlement, product profile, and secret lifecycle before integration work.. This workflow produces a reviewable artifact and evidence before any live side effect.

## Prerequisites

- Current first-party Adobe documentation for every selected service, API version, auth flow, limit, and lifecycle.
- Named product, identity, security, data, budget, release, and operations owners appropriate to the scope.
- Synthetic or approved non-production fixtures with secret and content canaries.

## Current Contract

OAuth Server-to-Server uses client credentials for application- or organization-owned data. User Authentication uses authorization code, explicit user consent, and optional offline access for user-owned data. Service Account JWT is deprecated and is never a valid new-work fallback. Recheck the dated evidence map before relying on mutable product behavior.

## Authentication

Keep client secrets and refresh tokens in an approved server-side secret store. Product profiles constrain organization data; scopes and a valid token do not prove entitlement by themselves.

## Instructions

1. Classify the API, data owner, organization, environment, and whether a user must consent.
2. Confirm the service is visible in the selected Developer Console organization and identify its license and admin owner.
3. Choose OAuth Server-to-Server or User Authentication from the ownership contract; reject JWT configuration.
4. Select only required scopes and product profiles and record requested versus granted authority.
5. Acquire a token through an established OAuth library and run one read-only, product-specific proof.
6. Document expiry, refresh, revocation, rotation, break-glass, and owner-transfer procedures.

## Tool Discipline

Use Read, Glob, and Grep to inspect current documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Skill invocation alone does not authorize network access, credentials, Adobe content, consent, uploads, generation, spend, deployment, registration changes, replay, cancellation, or deletion.

## Approval Boundaries

Require the organization or user owner for consent and product-profile assignment. Security approves production secret storage and rotation. Deleting a credential or old secret requires explicit approval after replacement evidence.

## Error Handling

- A token without product entitlement is not ready.
- Do not broaden scopes to cure a product-profile denial.
- Never print, decode, commit, or transmit a live token or secret.

## Output

Return the ownership decision, auth flow, scope/profile matrix, entitlement proof, redacted token test, lifecycle runbook, and unresolved gaps. Mark assumptions, observed environment behavior, owners, evidence dates, and unresolved gaps explicitly.

## Examples

- Prove an organization-owned read with a non-production S2S credential.
- Prove a user-owned request cannot proceed before explicit consent.

## Validation

Exercise and record expected and observed results for:

- wrong organization
- missing product
- insufficient profile
- expired token
- revoked consent
- rotation rollback

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated Adobe sources before execution.
- Treat observed tenant or product behavior as environment-specific evidence, never a universal Adobe guarantee.
