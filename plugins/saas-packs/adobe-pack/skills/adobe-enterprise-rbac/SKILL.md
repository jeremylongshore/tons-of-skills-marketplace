---
name: adobe-enterprise-rbac
description: >-
  Govern Adobe Developer Console roles, product profiles, technical accounts, User Management API automation, and periodic access review. Use when this Adobe operator workflow is needed. Trigger with "Adobe RBAC", "Adobe product profiles", or "Adobe user provisioning".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<organization> <products> <access-change>"
version: 1.8.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, adobe, rbac]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Adobe actions require network access, appropriate entitlement and authentication, and explicit approval"
---
# Adobe Enterprise Access Governance

## Overview

Govern Adobe Developer Console roles, product profiles, technical accounts, User Management API automation, and periodic access review.. This workflow produces a reviewable artifact and evidence before any live side effect.

## Prerequisites

- Current first-party Adobe documentation for every selected service, API version, auth flow, limit, and lifecycle.
- Named product, identity, security, data, budget, release, and operations owners appropriate to the scope.
- Synthetic or approved non-production fixtures with secret and content canaries.

## Current Contract

Developer Console project access, API scopes, product entitlement, product-profile assignment, and resource ownership are distinct. User Management API manages enterprise users/groups/entitlements under its own authorization; it is not a generic fix for application API access. Recheck the dated evidence map before relying on mutable product behavior.

## Authentication

Use named admin/automation identities with least privilege, environment binding, approver separation, rotation, and review dates. Technical-account access is constrained by assigned product profiles.

## Instructions

1. Inventory organizations, directories, admins, developers, projects, credentials, users/groups, products, profiles, and automation.
2. Build a role-to-operation matrix and calculate effective access across Console roles, scopes, profiles, and resources.
3. Identify orphaned credentials, broad profiles, stale users, shared admins, and cross-environment grants.
4. Design joiner/mover/leaver and service-account changes with approval, idempotency, reconciliation, and rollback.
5. Canary UMAPI changes on a synthetic group where authorized and compare intended versus effective access.
6. Schedule recertification, exception expiry, secret rotation, audit export, and emergency revocation.

## Tool Discipline

Use Read, Glob, and Grep to inspect current documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Skill invocation alone does not authorize network access, credentials, Adobe content, consent, uploads, generation, spend, deployment, registration changes, replay, cancellation, or deletion.

## Approval Boundaries

Organization, product, identity, and security owners approve grants and revocations. Bulk membership/profile changes and credential deletion require explicit execution approval.

## Error Handling

- Do not equate an OAuth scope with product entitlement.
- Do not use UMAPI against an unverified organization.
- Quarantine drift rather than auto-removing critical access without an approved rollback.

## Output

Return organization/access inventory, effective-access matrix, findings, approved change plan, reconciliation, exceptions, and recertification schedule. Mark assumptions, observed environment behavior, owners, evidence dates, and unresolved gaps explicitly.

## Examples

- Prove a technical account is limited by its product profile.
- Remove a synthetic group assignment and verify intended loss of access.

## Validation

Exercise and record expected and observed results for:

- orphaned account
- overbroad profile
- wrong organization
- stale admin
- bulk partial failure
- rollback

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated Adobe sources before execution.
- Treat observed tenant or product behavior as environment-specific evidence, never a universal Adobe guarantee.
