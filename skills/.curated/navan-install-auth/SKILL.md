---
name: navan-install-auth
description: >-
  Establish a Navan integration access contract without guessing endpoints, grants, or scopes. Use when onboarding a Booking API, Expense API, SFTP, SCIM, SSO, or direct integration. Trigger with "set up Navan access", "authenticate Navan", or "review Navan credentials".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<tenant> <integration-surface> <environment>"
version: 1.9.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, navan, access]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live or external Navan actions require network access and explicit approval"
---
# Navan Integration Access Intake

## Overview

Establish a Navan integration access contract without guessing endpoints, grants, or scopes. This workflow produces an auditable decision or artifact before any live action.

## Prerequisites

- Access to the selected tenant's current Navan Help Center and contracted integration documentation.
- A named business owner and data owner for the travel or expense workflow.
- A non-production evidence set with secrets and traveler data removed.

## Current Contract

Navan publicly confirms Booking API, Expense API, SFTP, direct integrations, SCIM, SAML, and OpenID Connect surfaces. Exact hosts, credentials, scopes, schemas, and enablement are tenant- and contract-specific; copy them from the current in-account source.

## Authentication

Record the credential type, issuer, audience or destination, scopes or permissions, expiry, rotation owner, and storage location from the tenant contract. Never infer OAuth client credentials or reuse interactive session cookies.

## Instructions

1. Choose one integration surface and its business owner.
2. Capture the current tenant documentation URL, revision date, and access prerequisites.
3. Request least-privilege non-production credentials through the approved secret channel.
4. Create a redacted connection profile with no credential values.
5. Plan one read-only or metadata-only validation allowed by the contract.
6. Record rotation, revocation, escalation, and production-promotion gates.

## Tool Discipline

Use Read, Glob, and Grep to inspect documentation, schemas, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Invocation alone does not authorize network access, credentials, traveler or expense data, bookings, payments, policy or identity changes, file transfers, deployments, or deletion.

## Approval Boundaries

Require the Navan admin and data owner before credential issuance, scope expansion, production access, SSO/SCIM changes, or any traveler-data read.

## Error Handling

- A public product page is not an endpoint contract.
- A login redirect is not proof that an API route exists.
- Missing scope or tenant enablement must fail closed and go to the Navan administrator.

## Output

Return an access matrix, evidence links, credential owner, allowed environments, read-only validation, rotation plan, and unresolved tenant questions. Identify assumptions, owners, expirations, and evidence gaps explicitly.

## Examples

- Prepare Expense API access without placing a secret in the repository.
- Document an Okta SCIM handoff while leaving provisioning disabled.

## Validation

Verify the evidence date, tenant, credential provenance, least privilege, secret storage, revocation owner, and absence of live values in artifacts. Record expected and observed results, including fail-closed behavior.

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources and the selected tenant's in-account contract before relying on mutable endpoints, fields, entitlements, limits, or delivery behavior.
- Record tenant observations as environment-specific evidence, never universal Navan guarantees.
