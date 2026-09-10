---
name: stackblitz-security-basics
description: >-
  Threat-model a WebContainer or StackBlitz embed across host, runtime, user-code, filesystem, dependency, network, preview, secret, and persistence boundaries. Use when preparing to execute untrusted code, enable private packages, or ship an interactive browser IDE. Trigger with "StackBlitz security review", "secure WebContainers", or "WebContainer threat model".
argument-hint: "[project-path] [trust-boundary]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- stackblitz
- security
- threat-modeling
model: inherit
effort: high
compatibility: Designed for Claude Code
---
# WebContainer Security Review

## Overview

This skill produces a repo-grounded threat model and bounded hardening plan. Browser containment reduces host risk, but it does not make user code trustworthy, prevent all network activity, protect secrets mounted into the runtime, or replace host-page CSP and data-governance controls.

## Prerequisites

- A named application, data classification, and intended code/dependency sources
- Identified owners for the host page, runtime lifecycle, auth, preview, persistence, and deployment headers
- Permission to inspect security-sensitive configuration without reading secret values

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to trace input, filesystem, process, dependency, network, preview, auth, CSP, and persistence paths. Use `WebFetch` only for current official StackBlitz or WebContainers documentation. Use `Write` for an approved threat model and `Edit` only for narrow reviewed controls.

## Current Contract

- Treat mounted files, spawned commands, installed packages, terminal input, preview messages, and exported artifacts as untrusted flows.
- Never mount host secrets or ambient `.env` files into user-controlled projects; code running there may read them.
- Validate virtual paths component by component and reject traversal, absolute paths, ambiguous separators, duplicates, and dangerous overwrite targets.
- Pin dependencies and preserve install provenance; browser execution does not remove package supply-chain risk.
- Derive CSP and frame/connect allowances from observed official runtime behavior and the chosen embed mode; do not copy a universal permissive header.
- Match cross-origin isolation headers and iframe requirements without weakening unrelated host protections.
- Define retention and review for any saved or exported user project; the runtime filesystem alone is ephemeral.

## Authentication

Keep commercial API keys in existing runtime secret bindings and configure them before boot. Organization auth for private packages is a separate user-authorized flow. Do not log auth parameters, tokens, cookies, private registry settings, or package contents.

## Workflow

1. Map assets, actors, entrypoints, trust boundaries, data flows, and privileged operations.
2. Classify code, files, dependencies, terminal input, previews, exports, and auth material by trust level.
3. Identify abuse cases for path traversal, secret exposure, dependency compromise, runaway processes, network exfiltration, preview-to-host messaging, and persistence.
4. Map existing preventive, detective, and recovery controls to each abuse case.
5. Implement only the highest-value bounded control with tests for expected, hostile, and rollback paths.
6. Record residual risk, production approval, monitoring, incident response, and the exact deployment/header verification.

## Approval Boundaries

Require explicit approval before enabling arbitrary code, private packages, network-capable dependencies, host-preview messaging, project persistence/export, telemetry, or production CSP/header changes. Security review and commercial licensing are release gates, not inferred setup details.

## Output

Return the trust-boundary diagram or table, abuse cases, current controls, gaps by severity, changes made or proposed, verification, data handling, release decision, rollback, and residual risk owner.

## Error Handling

| Condition | Response |
|---|---|
| A secret is mounted into the runtime | Stop, remove the flow, rotate if exposure occurred, and use a mediated service boundary. |
| User paths are concatenated directly | Add component-safe normalization and hostile-path tests before writes. |
| CSP needs broad wildcards | Inventory actual origins and redesign the integration rather than disabling protection. |
| Preview messages are trusted blindly | Validate origin, schema, direction, and allowed actions at the host boundary. |

## Examples

Before launching an AI coding playground, map prompts-to-files, package installation, process/network behavior, preview messaging, exports, and auth; then block secret mounting and add tested path and message validation.

## Resources

- [Official StackBlitz and WebContainers references](references/official-docs.md)
- [WebContainers introduction](https://webcontainers.io/guides/introduction)
- [Configuring headers](https://webcontainers.io/guides/configuring-headers)
