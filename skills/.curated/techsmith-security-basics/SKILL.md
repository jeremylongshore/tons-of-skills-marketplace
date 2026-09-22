---
name: techsmith-security-basics
description: >-
  Harden Snagit and Camtasia automation around capture consent, license secrecy, local storage, share destinations, least privilege, and artifact review. Use when threat-modeling or approving a TechSmith workflow. Trigger with "TechSmith security", "secure Snagit automation", or "Camtasia data controls".
argument-hint: "[workflow-path] [data-classification]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- desktop-automation
- techsmith
- security
model: inherit
effort: medium
compatibility: Designed for Claude Code; TechSmith product execution requires an approved Windows or macOS desktop as documented
---
# TechSmith Desktop Automation Security Boundary

## Overview

Desktop capture and media production cross sensitive screen, microphone, camera, filesystem, cloud-sharing, and licensing boundaries. This skill makes those boundaries explicit and keeps automation narrower than an interactive user's full capabilities.

## Prerequisites

- Workflow, users, endpoints, product versions, and data classification
- Approved capture subjects, devices, destinations, retention, and sharing policy
- License model and secret owner
- Deployment controls, endpoint protection, audit logging, and incident response

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect local scripts, manifests, logs, and tests. Use `WebFetch` only for current primary TechSmith documentation. Use `Write` or `Edit` only after confirming the target repository file and approval boundary.

## Current Contract

- Software keys and offline activation artifacts are secrets; keep them out of code, chat, logs, and unrestricted process arguments.
- Require explicit scope and consent for screen, microphone, camera, and clipboard operations.
- Use allowlisted local input/output roots and promote only validated artifacts.
- Use TechSmith deployment controls to disable unapproved share destinations or connected features rather than relying on operator memory.

## Licensing and Authentication

TechSmith desktop activation is not API authentication. Resolve individual sign-in versus business-key or approved offline activation before execution. Redact all keys, account identifiers, activation artifacts, and sensitive endpoint details.

## Instructions

1. Map actors, endpoint privileges, capture devices, project/media paths, share outputs, activation flow, and downstream publishers.
2. Classify threats: unintended capture, secret leakage, path traversal, malicious project/media, unauthorized upload, and persistence.
3. Constrain worker identity, session access, COM/recorder operations, input/output roots, and network destinations.
4. Configure approved deployment restrictions for sharing, updates, analytics, assets, or cloud features according to policy.
5. Add redacted audit events for authorization, job identity, product/version, output hash, validation, promotion, and deletion.
6. Exercise denial, cancellation, wrong-path, secret-scan, and incident-containment scenarios before approval.

## Approval Boundaries

Do not disable endpoint security, broaden share outputs, record hidden devices, retain clipboard data, or upload artifacts merely to prove connectivity.

## Output

Return assets, threats, controls, residual risks, data-flow boundaries, deployment restrictions, audit events, test evidence, and accountable owners.

## Error Handling

| Condition | Response |
|---|---|
| Capture scope ambiguous | Deny the job until subject, window/region, devices, and purpose are explicit. |
| Key appears in artifact | Quarantine, rotate, and purge the affected history or bundle. |
| Output destination unapproved | Block promotion and correct the allowlist. |
| Required control unsupported | Change the architecture or product workflow rather than accepting silent exposure. |

## Examples

The example below shows the minimum redacted evidence expected from a successful invocation of this operator workflow.

```text
capture=approved-window; audio=disabled; output=local-allowlist; sharing=restricted; retention=7d; audit=pass
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Snagit deployment controls](https://assets.techsmith.com/Docs/Snagit-2025-Deployment-Tool-Guide.pdf)
- [Camtasia deployment controls](https://assets.techsmith.com/docs/Camtasia_2025_Deployment_Tool_Guide.pdf)
