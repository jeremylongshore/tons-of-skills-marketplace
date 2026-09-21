---
name: notion-install-auth
description: >-
  Establish a least-privilege Notion connection and tested API contract without leaking credentials. Use when onboarding an internal connection, public OAuth connection, or personal access token. Trigger with "set up Notion auth", "create Notion connection", or "review Notion credentials".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<connection-type> <workspace> <environment>"
version: 1.40.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, notion, access]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Notion actions require network access and explicit approval"
---
# Notion Connection and Authentication Intake

## Overview

Establish a least-privilege Notion connection and tested API contract without leaking credentials.. This workflow produces an auditable decision or artifact before any live action.

## Prerequisites

- Current first-party Notion documentation and the selected integration's tested API-version contract.
- A named workspace owner, content or data owner, and operation owner.
- Synthetic or approved non-production fixtures with secrets and workspace content removed.

## Current Contract

Notion supports internal connections, public OAuth connections, and personal access tokens with different ownership and access behavior. REST calls require bearer authentication and an explicit tested Notion-Version contract. Recheck the dated evidence map before relying on mutable fields, endpoints, versions, limits, or delivery behavior.

## Authentication

Record credential issuer, connection or user owner, workspace binding, capabilities, shared roots, expiry or refresh behavior, storage, rotation, and revocation without storing the secret value.

## Instructions

1. Choose the connection type from distribution, tenant, and user-context requirements.
2. Define the minimum content, comment, and user capabilities plus exact shared fixture roots.
3. Select and test an SDK and API-version combination against current upgrade guidance.
4. Provision the credential through the approved secret manager and record a fingerprint.
5. Run bot identity plus one explicitly shared read-only fixture check.
6. Document rotation, OAuth refresh if applicable, revocation, reauthorization, and production promotion.

## Tool Discipline

Use Read, Glob, and Grep to inspect documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Invocation alone does not authorize network access, credentials, workspace content, user data, file transfer, deployment, capability or sharing changes, writes, spend, or deletion.

## Approval Boundaries

Require the workspace owner for connection creation and sharing; require security review for public OAuth, user information, external distribution, or production secrets.

## Error Handling

- Never infer OAuth scopes or redirect behavior from an internal token example.
- A connection capability does not grant access until content is shared where required.
- Do not commit env files or access tokens.

## Output

Return the connection model, workspace binding, capability matrix, shared roots, secret reference, validation evidence, lifecycle owners, and gaps. Identify assumptions, owners, expirations, and evidence gaps explicitly.

## Examples

- Onboard a read-only internal connection to a synthetic data source.
- Document a public OAuth installation without persisting tokens in browser state.

## Validation

Exercise and record these paths with expected and observed results:

- least privilege
- workspace binding
- shared content
- secret storage
- revocation
- negative access

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources before relying on mutable behavior.
- Treat observed tenant behavior as environment-specific evidence, never a universal Notion guarantee.
