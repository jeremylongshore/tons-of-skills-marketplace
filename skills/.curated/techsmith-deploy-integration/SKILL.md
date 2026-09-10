---
name: techsmith-deploy-integration
description: >-
  Roll out Snagit or Camtasia with TechSmith deployment tooling, immutable packages, staged endpoint rings, and licensing controls. Use when preparing enterprise Windows or macOS deployment. Trigger with "deploy TechSmith", "Snagit MSI MST", or "Camtasia managed rollout".
argument-hint: "[product] [package-path] [deployment-ring]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- desktop-automation
- techsmith
- deployment
model: inherit
effort: medium
compatibility: Designed for Claude Code; TechSmith product execution requires an approved Windows or macOS desktop as documented
---
# TechSmith Managed Desktop Rollout

## Overview

This skill turns a vendor installer into a reviewed deployment artifact: on Windows, TechSmith's preparation tool consumes the MSI and produces an MST plus command assets for endpoint management. macOS uses the documented package and managed preferences for the selected release.

## Prerequisites

- A vendor-origin installer matching the purchased product/version and verified checksum
- Current TechSmith deployment guide and preparation tool for that version
- A business-license decision, approved key-handling channel, and connectivity policy
- Test, pilot, and production endpoint rings with rollback ownership

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect local scripts, manifests, logs, and tests. Use `WebFetch` only for current primary TechSmith documentation. Use `Write` or `Edit` only after confirming the target repository file and approval boundary.

## Current Contract

- The TechSmith deployment tool prepares MSI/MST assets; it is not itself the fleet deployment system.
- Business keys can be packaged or provisioned through approved controls; individual subscriptions require user sign-in.
- Subscription applications require activation connectivity and periodic license verification unless an approved business offline path applies.
- Feature, sharing, update, and cloud-experience restrictions must be deliberate and documented.

## Licensing and Authentication

TechSmith desktop activation is not API authentication. Resolve individual sign-in versus business-key or approved offline activation before execution. Redact all keys, account identifiers, activation artifacts, and sensitive endpoint details.

## Instructions

1. Verify installer origin, checksum, product/version, architecture, license model, and endpoint requirements.
2. Create the MST or macOS configuration from reviewed settings; never expose a key in a public command line or log.
3. Generate an immutable package manifest containing input hashes, tool version, selected controls, and output hashes.
4. Deploy to a disposable test endpoint, then a small pilot ring with product launch and activation checks.
5. Validate Snagit COM registration or Camtasia recorder discovery only on platforms where those surfaces apply.
6. Promote by ring with error thresholds, help-desk readiness, rollback package, and version inventory reconciliation.

## Approval Boundaries

Do not overwrite an existing activation, delete a Snagit library, remove prior versions, or disable security/connected features without an explicit policy decision and rollback.

## Output

Return package hashes, selected deployment settings, license-handling mode, ring results, activation/launch checks, rollback command, and promotion decision.

## Error Handling

| Condition | Response |
|---|---|
| Installer checksum differs | Stop and reacquire the package from TechSmith. |
| License model mismatched | Rebuild for business-key or individual-sign-in activation as authorized. |
| Pilot failure threshold exceeded | Halt promotion and preserve pilot diagnostics. |
| Rollback affects user data | Separate application removal from library/project retention and obtain approval. |

## Examples

The example below shows the minimum redacted evidence expected from a successful invocation of this operator workflow.

```text
product=Snagit; version=2026.x; package=msi+mst; ring=pilot; launch=pass; promotion=hold(activation-proxy)
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Deploying TechSmith products](https://support.techsmith.com/hc/en-us/articles/43771074923021-Deploying-TechSmith-Products)
- [Snagit MST guidance](https://support.techsmith.com/hc/en-us/articles/203730778-Customize-the-Snagit-installer-MSI-with-Transform-MST-for-Enterprise-Installation)
