---
name: firecrawl-enterprise-rbac
description: >-
  Design and audit Firecrawl team roles, API-key ownership, endpoint and format restrictions, IP restrictions, SSO, and separation of duties. Use when governing enterprise access. Trigger with "Firecrawl RBAC", "restrict a Firecrawl key", or "Firecrawl enterprise controls".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<team-or-environment> <access-change>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, firecrawl, access-control, enterprise]
model: inherit
effort: high
compatibility: "Designed for Claude Code; Firecrawl Cloud work requires network access"
---
# Firecrawl Enterprise Access Governance

## Overview

Translate Firecrawl's actual team and key controls into a least-privilege operating model. Do not invent fine-grained roles that the dashboard does not provide.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The source authorization, data classification, and environment policy.
- Current Firecrawl documentation, credentials only when needed, and an owner for approvals.

## Current Contract

The dashboard documents two team roles, Admin and Member, with administrative actions reserved for Admins. Enterprise key restrictions can enforce per-key endpoint and output-format allowlists; team-scoped IP restrictions can restrict authenticated origins; SSO is an enterprise capability. Empty restriction lists mean unrestricted, and changes can take time to propagate.

## Authentication

For authenticated Cloud operations, inject FIRECRAWL_API_KEY from an approved
secret manager. REST requests use Authorization: Bearer with the key. Never print,
commit, transmit, or place a key in a URL. Keyless access is suitable only where
the current documentation explicitly allows it and the workload accepts its
limits; production workflows should make identity and team ownership explicit.

## Instructions

1. Inventory teams, Admins, Members, API keys, service owners, environments, permitted endpoints/formats, source networks, spend limits, SSO state, and break-glass access.
2. Remove shared human keys from services. Assign each workload an owned key and secret-manager path with a documented purpose and rotation/revocation procedure.
3. Use the smallest team role. Keep invitations, member removal, role changes, key administration, billing, and enterprise-control changes behind Admin review.
4. For eligible enterprise keys, configure non-empty endpoint and format allowlists; remember that an empty list does not restrict that dimension.
5. Apply team-scoped IP restrictions only after inventorying every legitimate egress address and testing a break-glass path from an approved network.
6. Align SSO, offboarding, key rotation, SIEM evidence, spend limits, and quarterly access review with the organization's identity controls.
7. Test allow, deny, propagation, revoked-key, removed-user, unexpected-IP, and disaster-recovery cases and retain only redacted evidence.

## Tool Discipline

Use Read, Glob, and Grep to inspect code, configuration, tests, and evidence. Use
Write/Edit only for approved implementation or documentation changes. Do not call
Firecrawl, rotate keys, change account settings, scrape a target, or deploy merely
because this skill was invoked.

## Approval Boundaries

Require two-person approval for Admin grants, SSO or IP changes, break-glass use, restriction removal, new unrestricted keys, and access to sensitive targets.

## Output

Return an access matrix, Admin/Member rationale, key-to-workload inventory, restriction and IP policy, SSO/offboarding design, test evidence, exceptions, owners, and review date.

## Error Handling

- Required granularity is unsupported: enforce it at the gateway and key boundary rather than inventing a Firecrawl role.
- An IP allowlist may lock out production: stage it with verified egress and tested break-glass recovery.
- Restriction update is not visible yet: wait for documented propagation and verify deny cases before rollout.

## Examples

- "Give the crawler read-only access" maps to an endpoint/format-restricted service key, not a fictional ReadOnly role.
- "Let every developer use the production key" is replaced with named membership and environment-specific service identity.

## Resources

Read [official Firecrawl evidence](references/official-docs.md) before relying on
an endpoint, SDK method, plan limit, price, retention option, or self-hosted release.
