---
name: adobe-known-pitfalls
description: >-
  Detect current high-risk Adobe integration traps before they become production incidents. Use when the task requires adobe integration pitfall review. Trigger with "Adobe pitfalls", "review Adobe integration", or "find obsolete Adobe code".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<repository> <services> <environment>"
version: 1.8.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, adobe, review]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Adobe actions require network access, appropriate entitlement and authentication, and explicit approval"
---
# Adobe Integration Pitfall Review

## Overview

Detect current high-risk Adobe integration traps before they become production incidents. This workflow produces a reviewable artifact and evidence before any live side effect.

## Prerequisites

- Current first-party Adobe documentation for every selected service, API version, auth flow, limit, and lifecycle.
- Named product, identity, security, data, budget, release, and operations owners appropriate to the scope.
- Synthetic or approved non-production fixtures with secret and content canaries.

## Current Contract

High-risk traps include Service Account JWT, confusing S2S with user auth, missing entitlements/profiles, secrets in clients, retired Photoshop v1 and Lightroom Firefly Services, reconstructed async URLs, leaked signed URLs, fixed limits, unverified events, and wrong App Builder workspace. Recheck the dated evidence map before relying on mutable product behavior.

## Authentication

Review effective authority and secret flow before code style. A valid token, installed SDK, or successful deploy does not prove product entitlement or correct data ownership.

## Instructions

1. Read manifests, locks, config, adapters, routes, workflows, logs, dashboards, tests, and runbooks.
2. Glob and Grep for JWT, /sensei/cutout, Lightroom Firefly Services, client-side secrets, fixed quotas, and hardcoded job routes.
3. Trace auth ownership, product profiles, versions, signed URLs, async states, retries, events, workspaces, and cleanup.
4. Classify each finding as obsolete, unsafe, brittle, undocumented, environment-specific, or stale evidence.
5. Propose the smallest compatible correction with tests, canary, rollback, and named owner.
6. Edit only approved repository artifacts, rerun gates, and record unresolved external dependencies.

## Tool Discipline

Use Read, Glob, and Grep to inspect current documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Skill invocation alone does not authorize network access, credentials, Adobe content, consent, uploads, generation, spend, deployment, registration changes, replay, cancellation, or deletion.

## Approval Boundaries

Read-only review needs no mutation authority. Credential/profile changes, production calls, deploys, replays, registration changes, and deletion require separate explicit approval.

## Error Handling

- Do not replace one remembered constant with another.
- Do not infer a product from a similarly named Adobe API.
- Do not auto-fix secrets without coordinated rotation and revocation.

## Output

Return findings with file/line evidence, current sources, severity, correction, test, owner, and unresolved risks. Mark assumptions, observed environment behavior, owners, evidence dates, and unresolved gaps explicitly.

## Examples

- Find a retired endpoint in code and documentation.
- Find a status URL reconstructed from jobId instead of response evidence.

## Validation

Exercise and record expected and observed results for:

- JWT
- Photoshop v1
- Lightroom EOL
- client secret
- fixed limit
- forged event

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated Adobe sources before execution.
- Treat observed tenant or product behavior as environment-specific evidence, never a universal Adobe guarantee.
