---
name: canva-enterprise-rbac
description: 'Implement application-owned authorization from Canva scopes, user capabilities, resource ownership, and tenant policy. Use when gating Enterprise or privileged operations without inventing a Canva custom-role API. Trigger with: "Canva RBAC", "check Canva capability", "authorize Canva action".'
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[action-and-tenant-context]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - canva
  - authorization
  - operations
compatibility: 'Requires a documented application role model plus current Canva scope and capability evidence.'
---

# Canva Capability-Aware Authorization

## Overview

Use Canva scopes and capabilities as provider inputs to your own authorization decision. Do not equate OAuth consent with tenant role, resource ownership, feature entitlement, or approval to process content.

## Prerequisites

- Application roles, actions, tenants, and deny-by-default policy
- Current explicit Canva scopes and capability response contract
- Resource ownership and data-classification checks

## Instructions

### Step 1: Define the decision tuple

Name subject, tenant, application role, action, resource, environment, requested Canva operation, and data class.

### Step 2: Separate provider inputs

Treat granted scopes, capability fields, resource access, and preview availability as independent facts. Absence, unknown values, or stale evidence must deny.

### Step 3: Map application policy

Use Write or Edit to map each application action to minimum scopes, required capability evidence, ownership rule, approval, and audit class.

### Step 4: Enforce server-side

Resolve the policy after authenticated tenant identity and before dispatch. Keep the generic Canva client unaware of business roles.

### Step 5: Handle changes

Invalidate cached decisions after scope, membership, consent, capability, policy, or resource-owner changes; require reauthorization only when scopes changed.

### Step 6: Audit without content

Record policy version, opaque subject/resource references, decision inputs, allow/deny result, and reason code without tokens or design contents.

## Authentication

Canva Connect calls use Bearer access tokens obtained by a backend through OAuth 2.0 Authorization Code with SHA-256 PKCE. Request explicit least-privilege scopes, keep client secrets and tokens out of browser-visible state, and serialize refresh so the replacement single-use refresh token is stored atomically.

## Tool Discipline

Use Read and Grep for discovery and evidence. Use Write or Edit only for the approved artifact, code, configuration, test, or receipt described by this workflow; do not make an unapproved Canva-side change.

## Output

- Scoped decision or implementation artifact
- Redacted operation and validation receipt
- Failure, rollback, and follow-up ownership record

## Examples

An application editor requests brand-template autofill. The backend checks tenant role, explicit design and template scopes, current capability/availability, template ownership, and data approval before submitting one job.

## Error Handling

| Failure | Response |
| --- | --- |
| Capability field is unknown | Deny and update the pinned response contract |
| Scope exists but role denies | Deny; OAuth consent does not override application policy |
| Tenant cannot be resolved | Stop before any Canva request |
| Policy cache is stale | Invalidate and recompute from current evidence |

## Resources

- [First-party source notes](references/official-docs.md)
- [Capabilities](https://www.canva.dev/docs/connect/capabilities/)
- [OAuth scopes](https://www.canva.dev/docs/connect/appendix/scopes/)
