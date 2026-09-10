---
name: techsmith-prod-checklist
description: >-
  Validate a Snagit or Camtasia automation release across licensing, versioning, desktop session, storage, privacy, rollback, and support readiness. Use when preparing a production rollout or scheduled media run. Trigger with "TechSmith production checklist", "Camtasia go live", or "Snagit automation readiness".
argument-hint: "[release-manifest] [environment]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- desktop-automation
- techsmith
- operations
model: inherit
effort: medium
compatibility: Designed for Claude Code; TechSmith product execution requires an approved Windows or macOS desktop as documented
---
# TechSmith Production Go-No-Go

## Overview

This skill produces a fail-closed production decision with evidence owners. It covers desktop constraints that ordinary web-service checklists miss: interactive sessions, licensed endpoints, installed type libraries, project version compatibility, local scratch, capture privacy, and artifact promotion.

## Prerequisites

- Release manifest with scripts, packages, product versions, configurations, and hashes
- Approved endpoints, license assignments, service owner, privacy classification, and retention policy
- Representative canary capture/export plus expected validation results
- Rollback package, incident contacts, and maintenance window

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect local scripts, manifests, logs, and tests. Use `WebFetch` only for current primary TechSmith documentation. Use `Write` or `Edit` only after confirming the target repository file and approval boundary.

## Current Contract

- Every production worker maps to an approved endpoint, user/license model, product version, and data boundary.
- Snagit COM jobs declare capture scope and interactive-session behavior.
- Camtasia jobs use local active storage and the modern exporter supported by the pinned release.
- Promotion requires validated output, cleanup, monitoring, and tested rollback—not merely process exit zero.

## Licensing and Authentication

TechSmith desktop activation is not API authentication. Resolve individual sign-in versus business-key or approved offline activation before execution. Redact all keys, account identifiers, activation artifacts, and sensitive endpoint details.

## Instructions

1. Verify immutable release inputs, vendor-origin installers, checksums, code review, and test evidence.
2. Reconcile endpoint versions, entitlement ownership, activation health, connectivity, and update policy.
3. Test COM registration or recorder discovery and confirm interactive-session scheduling where required.
4. Run a canary with synthetic content; validate file properties, path boundary, and cleanup.
5. Exercise rollback without deleting libraries, projects, or user data; confirm support escalation artifacts.
6. Issue GO only when every blocking control has evidence; otherwise name the blocker, owner, and next check.

## Approval Boundaries

No checklist item may be waived silently. Capture privacy, entitlement, destructive uninstall, data migration, and rollback failures are hard blockers.

## Output

Return GO/NO-GO, release and product versions, evidence per control, blockers, owners, canary result, rollback result, and review timestamp.

## Error Handling

| Condition | Response |
|---|---|
| Version inventory drifts | Stop rollout and reconcile workers to the pinned release. |
| Canary captures real user data | Delete or quarantine it under policy and replace the canary with synthetic content. |
| Rollback deletes data | Reject the rollback plan and separate application removal from data retention. |
| License health unknown | Block scheduling until the entitlement owner verifies it. |

## Examples

The example below shows the minimum redacted evidence expected from a successful invocation of this operator workflow.

```text
decision=NO-GO; blocker=worker-03-version-drift; owner=desktop-eng; canary=pass; rollback=pass
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Deployment overview](https://support.techsmith.com/hc/en-us/articles/43771074923021-Deploying-TechSmith-Products)
- [Current update guidance](https://support.techsmith.com/hc/en-us/articles/360038603471-How-do-I-upgrade-update-Snagit-or-Camtasia-Editor)
