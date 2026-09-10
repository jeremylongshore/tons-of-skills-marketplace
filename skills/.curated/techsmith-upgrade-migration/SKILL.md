---
name: techsmith-upgrade-migration
description: >-
  Upgrade Snagit or Camtasia with entitlement checks, immutable backups, canaries, project-format boundaries, and reversible endpoint rollout. Use when changing product versions or retiring legacy media. Trigger with "upgrade TechSmith", "migrate Camtasia project", or "convert Snagit library".
argument-hint: "[product] [source-version] [target-version]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- desktop-automation
- techsmith
- migration
model: inherit
effort: medium
compatibility: Designed for Claude Code; TechSmith product execution requires an approved Windows or macOS desktop as documented
---
# TechSmith Versioned Upgrade and Media Migration

## Overview

This skill treats application upgrade and content conversion as separate transactions. It preserves original libraries/projects, pins the tools needed for legacy formats, validates copies on a canary, and never assumes backward compatibility.

## Prerequisites

- Source and target product/version, platform, license eligibility, and installer hashes
- Immutable backup of Snagit library or standalone/zipped Camtasia projects plus checksums
- Representative canary assets and acceptance criteria
- Rollback endpoint/package and owners for content conversion

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect local scripts, manifests, logs, and tests. Use `WebFetch` only for current primary TechSmith documentation. Use `Write` or `Edit` only after confirming the target repository file and approval boundary.

## Current Contract

- Camtasia projects are not backward-compatible; collaborators must align on the same version.
- Camtasia 2020+ does not open CAMPROJ or CAMREC directly; CAMPROJ requires an intermediate 9/2018/2019 save to TSCPROJ, while CAMREC must be produced in an older version.
- Snagit 2022 introduced SNAGX; export to standard formats while a usable Snagit entitlement is available when long-term portability is required.
- Never overwrite originals during canary conversion or uninstall user data as part of application rollback.

## Licensing and Authentication

TechSmith desktop activation is not API authentication. Resolve individual sign-in versus business-key or approved offline activation before execution. Redact all keys, account identifiers, activation artifacts, and sensitive endpoint details.

## Instructions

1. Inventory endpoints, entitlements, integrations, COM clients, project/library formats, share outputs, and collaborators.
2. Back up original content immutably, record hashes, and verify restore before installing the target version.
3. Read target release and deployment guidance; identify removed exporter, executable, codec, project, and policy changes.
4. Upgrade one canary endpoint and test launch, activation, COM creation, recorder discovery, representative open/edit/export, and rollback.
5. Convert copies through the documented intermediate versions or batch-export path; retain original-to-result mapping and validation.
6. Promote by endpoint ring, monitor failures, and retire legacy tooling only after recovery and audit windows expire.

## Approval Boundaries

Do not bulk-convert the only copy, open a project in a newer version before preserving a rollback copy, or assume a subscription unlocks every historical version.

## Output

Return source/target matrix, entitlement result, backup and restore evidence, canary tests, conversion ledger, rollback result, promotion decision, and retained originals.

## Error Handling

| Condition | Response |
|---|---|
| Historical version unavailable | Pause that content cohort and obtain an authorized conversion workstation or support path. |
| Project fails in target | Restore the canary copy and classify version, media, font, or codec cause. |
| Output validation differs | Reject the conversion and keep the original authoritative. |
| Rollback loses library/project data | Stop rollout and redesign data preservation separately from app removal. |

## Examples

The example below shows the minimum redacted evidence expected from a successful invocation of this operator workflow.

```text
product=Camtasia; source=2019-camproj; bridge=2019-tscproj; target=2026; originals=retained; canary=pass
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Legacy Camtasia file migration](https://support.techsmith.com/hc/en-us/articles/360048452272-Opening-Camproj-and-Camrec-Files-in-Camtasia-2020-and-Later)
- [Export a Snagit library](https://support.techsmith.com/hc/en-us/articles/27142747345805-How-Do-I-Export-My-Snagit-Library-if-I-No-Longer-Plan-to-Use-Snagit)
