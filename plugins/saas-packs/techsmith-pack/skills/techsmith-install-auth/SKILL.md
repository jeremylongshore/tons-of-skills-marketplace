---
name: techsmith-install-auth
description: >-
  Select and verify the supported Snagit or Camtasia install, license, activation, connectivity, and Snagit COM-registration path. Use when provisioning a workstation or resolving activation ambiguity. Trigger with "install TechSmith", "activate Snagit", or "configure Camtasia license".
argument-hint: "[product] [operating-system] [license-model]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- desktop-automation
- techsmith
- setup
model: inherit
effort: medium
compatibility: Designed for Claude Code; TechSmith product execution requires an approved Windows or macOS desktop as documented
---
# TechSmith Installation and Activation Decision

## Overview

This skill treats activation as a product and entitlement decision, not API authentication. Individual subscriptions activate by account sign-in, while business licenses use a software key and support managed deployment and, where documented, offline activation.

## Prerequisites

- Product, operating system, target version, architecture, and system requirements
- Authoritative entitlement owner and license model: individual, business, or legacy
- Approved installer source and endpoint-management channel
- Connectivity, proxy, offline-use, update, and connected-feature policy

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect local scripts, manifests, logs, and tests. Use `WebFetch` only for current primary TechSmith documentation. Use `Write` or `Edit` only after confirming the target repository file and approval boundary.

## Current Contract

- Individual subscriptions require the purchasing account to sign in and do not use a software key.
- Business subscriptions use software keys; approved offline activation is a business-license path.
- Subscription software normally needs initial activation connectivity and periodic verification within the vendor's current interval.
- Snagit COM should register during Windows installation; `SnagitCapture.exe /register` is an elevated recovery, not a default step.

## Licensing and Authentication

TechSmith desktop activation is not API authentication. Resolve individual sign-in versus business-key or approved offline activation before execution. Redact all keys, account identifiers, activation artifacts, and sensitive endpoint details.

## Instructions

1. Resolve product/version and confirm the entitlement before downloading or installing anything.
2. Choose standard interactive installation, managed Windows MSI/MST, documented macOS deployment, or approved offline activation.
3. Verify installer origin and checksum, then install through the approved endpoint channel.
4. Activate by individual sign-in, managed business key, or the documented offline exchange without logging secret material.
5. Confirm product launch, displayed version/license state, and required connectivity.
6. For Windows Snagit automation, create the COM object; use vendor registration recovery only if creation fails and approval is recorded.

## Approval Boundaries

Never paste a license key into chat, source control, a public CI variable, or diagnostic output. Do not convert an individual subscription into an unattended shared-worker credential.

## Output

Return product/version, installer hash, deployment mode, redacted license model, activation result, connectivity disposition, COM probe result where applicable, and owner.

## Error Handling

| Condition | Response |
|---|---|
| Entitlement cannot be confirmed | Stop before installation and contact the license owner. |
| Individual sign-in unavailable | Do not substitute a shared account; resolve assignment or use an authorized business license. |
| Offline activation requested for individual plan | Reject the path and explain the documented business-license requirement. |
| COM registration recovery fails | Capture redacted install/version evidence and escalate to TechSmith support. |

## Examples

The example below shows the minimum redacted evidence expected from a successful invocation of this operator workflow.

```text
product=Snagit; platform=Windows; license=business-key(redacted); install=managed; com_probe=pass
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Activation overview](https://support.techsmith.com/hc/en-us/articles/45353457739149-How-to-Activate-Snagit-or-Camtasia)
- [Deployment overview](https://support.techsmith.com/hc/en-us/articles/43771074923021-Deploying-TechSmith-Products)
