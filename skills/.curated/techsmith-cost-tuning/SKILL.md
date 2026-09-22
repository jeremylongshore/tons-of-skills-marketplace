---
name: techsmith-cost-tuning
description: >-
  Optimize TechSmith desktop automation cost through license assignment, workstation utilization, retention, and measured export capacity. Use when sizing Snagit or Camtasia operations without inventing API usage pricing. Trigger with "TechSmith cost tuning", "Camtasia capacity cost", or "Snagit license optimization".
argument-hint: "[inventory-path] [planning-window]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- desktop-automation
- techsmith
- cost
model: inherit
effort: medium
compatibility: Designed for Claude Code; TechSmith product execution requires an approved Windows or macOS desktop as documented
---
# TechSmith License and Workstation Cost Control

## Overview

This skill treats cost as a desktop fleet and media-lifecycle problem. TechSmith's supported Snagit/Camtasia automation is not a metered public API, so optimization focuses on approved license models, active seats, workstation time, local scratch, retained artifacts, and support burden.

## Prerequisites

- A redacted inventory of product, version, license model, assigned user, and workstation
- Measured queue duration, failure/rework rate, storage growth, and retention
- Current commercial terms from TechSmith or the organization's agreement
- Business owners for license reassignment, archive policy, and service levels

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect local scripts, manifests, logs, and tests. Use `WebFetch` only for current primary TechSmith documentation. Use `Write` or `Edit` only after confirming the target repository file and approval boundary.

## Current Contract

- Do not invent per-request pricing or API quotas for desktop COM and recorder workflows.
- Individual subscriptions activate by user sign-in; business licenses use managed keys and can support offline activation.
- Commercial prices and discounts are contract facts to recheck, not constants to embed in code.
- Camtasia project/export work remains workstation-bound; concurrency adds hardware and license implications.

## Licensing and Authentication

TechSmith desktop activation is not API authentication. Resolve individual sign-in versus business-key or approved offline activation before execution. Redact all keys, account identifiers, activation artifacts, and sensitive endpoint details.

## Instructions

1. Reconcile installed products and versions with assigned entitlements without collecting raw keys.
2. Measure successful workstation-minutes per output, queue delay, retries, storage churn, and operator intervention.
3. Separate mandatory production capacity from burst, development, and disaster-recovery capacity.
4. Reduce rework through version pinning, standalone projects, local scratch, approved presets, and canary exports.
5. Apply retention tiers to source projects, intermediate files, and validated deliverables; archive only after applications close.
6. Model license or hardware changes with current vendor quotes and document the assumptions and rollback.

## Approval Boundaries

Do not share a single-user credential across workers, deactivate users automatically, or treat an observed install as proof of entitlement.

## Output

Return entitlement counts, measured utilization, unit-cost assumptions, capacity risks, retention savings, recommended action, owner, and review date.

## Error Handling

| Condition | Response |
|---|---|
| Entitlement data incomplete | Report a range and request the authoritative contract inventory. |
| Costs are stale | Recheck the vendor quote or agreement before recommending purchase. |
| Queue savings reduce reliability | Restore headroom and prioritize deterministic canaries over utilization. |
| License reassignment disputed | Stop and route to the contract or procurement owner. |

## Examples

The example below shows the minimum redacted evidence expected from a successful invocation of this operator workflow.

```text
licensed_workers=4; peak_required=3; export_rework=12%; recommendation=fix-version-drift-before-adding-seat
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Deploying TechSmith products](https://support.techsmith.com/hc/en-us/articles/43771074923021-Deploying-TechSmith-Products)
- [Activation models](https://support.techsmith.com/hc/en-us/articles/31352249532941-How-Do-I-Activate-My-Snagit-or-Camtasia-Subscription)
