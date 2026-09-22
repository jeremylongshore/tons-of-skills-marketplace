---
name: windsurf-enterprise-rbac
description: 'Analyze and design Devin Desktop (formerly Windsurf) enterprise SSO, SCIM, RBAC, and team controls. Use when defining least-privilege roles, identity lifecycle, model or terminal policy, MCP access, or organization-wide rollout governance. Trigger with "Windsurf SSO", "Devin Desktop RBAC", "enterprise rollout", or "team permissions".'
argument-hint: "[organization, identity provider, and access-policy requirements]"
allowed-tools: Read, Write, Edit
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- windsurf
- enterprise
- sso
- rbac
- admin
compatibility: Designed for Claude Code
---
# Devin Desktop Enterprise Access Control

## Overview

Build an evidence-backed enterprise access model for Devin Desktop, the current name for Windsurf. RBAC is an Enterprise feature; verify plan eligibility and current control labels in the admin console before promising a capability.

## Prerequisites

- An Enterprise organization and an authenticated administrator
- Named identity, security, billing, and developer-experience owners
- The organization's identity lifecycle, least-privilege, and break-glass requirements
- Current first-party documentation and contract terms for any mutable product claim

## Authentication

Perform administrative changes only from a protected enterprise-admin session. Treat SAML metadata, SCIM tokens, service keys, recovery codes, cookies, and exported member data as secrets; keep values in approved identity or secret systems and place only redacted references in deliverables.

## Tool Use

- Use `Read` to inspect only the repository policy and configuration files needed for the access design.
- Use `Write` only for a new access matrix or rollout artifact explicitly requested by the user.
- Use `Edit` for bounded changes to existing policy documents, preserving unrelated work and all credential boundaries.

## Instructions

### Step 1: Establish the administrative boundary

Record the organization, administrator group, identity provider, affected teams, repositories, and environments. Use the Devin Desktop admin console under the team settings surface; do not invent SAML endpoints or API scopes from examples.

### Step 2: Design roles from documented permissions

Devin Desktop provides default Admin and User roles and supports custom Enterprise roles. Start the User role with no administrative permissions, then grant only the documented actions required for the job.

Map needs against the current permission families:

- Attribution and analytics read access
- Team read, update, delete, and invite actions
- Index read, create, update, delete, and management actions
- SSO read and write actions
- Service-key read, create, update, and delete actions
- Billing read and write actions
- Role read, create, update, and delete actions

Never copy a role name from this skill without checking the live permissions list. The product can add, rename, or split permissions.

### Step 3: Connect SSO and SCIM lifecycle

Use SSO for authentication and SCIM for automated provisioning, deprovisioning, and group-to-team mapping where supported. Define:

1. The IdP group that grants base access.
2. The IdP groups that map to Devin Desktop teams.
3. The role each team receives.
4. The offboarding event and maximum revocation time.
5. A tested break-glass path with a named owner and audit requirement.

Enable enforcement only after a pilot administrator and a non-administrator complete sign-in, role, and recovery tests.

### Step 4: Configure team feature controls

Review each organization-level control in the current admin guide and record the chosen state, owner, and reason. Current control families include:

- Model access by specific model or provider, plus the initial Cascade default
- Maximum terminal auto-execution level: Disabled, Allowlist Only, Auto, or Turbo
- Team terminal allowlists and denylists, with deny taking precedence
- MCP availability and approved-server policy
- App Deploys, conversation sharing, PR-review integration, and knowledge-base access

Prefer the lowest terminal level that supports the workflow. Review MCP servers as external capabilities because they may create or mutate resources outside Devin Desktop.

### Step 5: Separate product controls from external enforcement

For every requirement, identify the authoritative enforcement point. Repository permissions, branch protection, identity-provider policy, secret management, deployment approval, and data-loss controls remain authoritative even when Devin Desktop provides a related toggle.

| Requirement | Devin Desktop control | External control | Owner | Evidence |
|---|---|---|---|---|
| Member lifecycle | SCIM team mapping | IdP group and termination workflow | Identity | Provision/deprovision test |
| Model access | Model/provider filter | Approved-model policy | Security | Admin export or screenshot |
| Terminal safety | Maximum level and lists | Repository permissions and CI | DevEx | Allowed/denied canary |
| MCP access | MCP toggle and allowlist | Vendor review and scoped credentials | Platform | Server inventory and test |
| Production deploy | App Deploys toggle | Protected deployment environment | SRE | Approval and rollback receipt |

### Step 6: Pilot and verify

Test at least one user in every proposed role. Verify allowed and denied admin pages, team membership, analytics visibility, indexing controls, SSO recovery, SCIM deprovisioning, terminal policy, MCP policy, and any enabled sharing or deployment feature.

Stop rollout on unexpected privilege, failed deprovisioning, missing audit evidence, or a control whose behavior cannot be confirmed from the current console and documentation.

### Step 7: Define recurring review

Set review owners and intervals for privileged roles, service keys, team membership, model/provider access, terminal lists, MCP allowlists, feature toggles, billing access, and break-glass accounts. Record changes as reviewable evidence rather than embedding secrets in the report.

## Output

Deliver an access-control matrix, IdP-to-team mapping, role definitions, feature-control decisions, pilot evidence, offboarding test, break-glass procedure, exceptions, and recurring review schedule. Label every item as a Devin Desktop control, an external enforcement control, or an unverified contract-dependent claim.

## Error Handling

| Issue | Safe response |
|---|---|
| A documented permission is absent | Stop and re-check the live Enterprise console and current first-party docs |
| SSO blocks all administrators | Use the pre-tested break-glass path, then repair IdP configuration before enforcement |
| SCIM leaves a terminated user active | Disable access directly, preserve evidence, and investigate the identity lifecycle |
| A role grants unexpected access | Remove the grant, compare the effective role, and rerun the denied-path test |
| An MCP or deploy control is ambiguous | Keep it disabled until ownership, credential scope, and rollback are approved |

## Examples

For an engineering lead who needs team analytics but no billing or identity access, create a custom role with the current analytics-read permission only, assign it through the appropriate team, and prove both the allowed analytics view and denied billing, SSO, service-key, and role-management paths.

For automated offboarding, map an IdP group to the target Devin Desktop team through SCIM, remove a synthetic pilot identity from the IdP group, and record the observed revocation time without exposing the SCIM credential.

## Resources

- [Role Based Access and Management](https://docs.devin.ai/desktop/accounts/rbac-role-management)
- [Devin Desktop Guide for Admins](https://docs.devin.ai/desktop/guide-for-admins)
- [SSO and SCIM](https://docs.devin.ai/desktop/accounts/sso-scim)

See [references/official-docs.md](references/official-docs.md) for the maintained first-party source list.

## Related Skills

Continue with `windsurf-migration-deep-dive` for staged adoption and `windsurf-policy-guardrails` for repository, terminal, MCP, and deployment enforcement.
