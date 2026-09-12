---
name: adobe-multi-env-setup
description: >-
  Separate Adobe development, stage, and production organizations/projects/workspaces, credentials, profiles, storage, events, budgets, and evidence. Use when the task requires adobe multi-environment isolation. Trigger with "Adobe environments", "separate Adobe staging", or "Adobe workspace setup".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<environments> <services> <promotion-model>"
version: 1.8.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, adobe, environments]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Adobe actions require network access, appropriate entitlement and authentication, and explicit approval"
---
# Adobe Multi-Environment Isolation

## Overview

Separate Adobe development, stage, and production organizations/projects/workspaces, credentials, profiles, storage, events, budgets, and evidence. This workflow produces a reviewable artifact and evidence before any live side effect.

## Prerequisites

- Current first-party Adobe documentation for every selected service, API version, auth flow, limit, and lifecycle.
- Named product, identity, security, data, budget, release, and operations owners appropriate to the scope.
- Synthetic or approved non-production fixtures with secret and content canaries.

## Current Contract

App Builder provides isolated workspaces such as Stage and Production within a project, while some risk boundaries require separate projects or credentials. Environment equivalence must be proven from configuration and entitlement, not assumed from names. Recheck the dated evidence map before relying on mutable product behavior.

## Authentication

Each credential is bound to one declared environment and secret store. Product profiles, redirect URIs, event registrations, storage buckets, and consenting users are independently mapped.

## Instructions

1. Inventory organizations, projects, workspaces, credentials, services, profiles, users, URLs, storage, events, and billing owners.
2. Define isolation requirements and choose workspace, project, or organization separation for each threat and operational boundary.
3. Create a typed environment manifest with aliases and secret references but no values.
4. Add fail-closed assertions for organization/project/workspace, endpoint hosts, storage, event recipient, and production fixture bans.
5. Compare environment capabilities and run synthetic parity tests without copying production data.
6. Document promotion, drift detection, emergency disablement, rotation, teardown, and ownership.

## Tool Discipline

Use Read, Glob, and Grep to inspect current documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Skill invocation alone does not authorize network access, credentials, Adobe content, consent, uploads, generation, spend, deployment, registration changes, replay, cancellation, or deletion.

## Approval Boundaries

Security and organization admins approve environment/credential/profile creation; data and budget owners approve storage and live workloads; teardown and deletion require separate approval.

## Error Handling

- Never infer environment from a branch name alone.
- Do not reuse production credentials or data in development.
- Treat entitlement differences as explicit drift, not a test inconvenience.

## Output

Return the environment matrix, isolation rationale, typed manifest, parity results, promotion gate, drift controls, and owners. Mark assumptions, observed environment behavior, owners, evidence dates, and unresolved gaps explicitly.

## Examples

- Prove a Stage build cannot address Production storage.
- Detect a workspace/profile mismatch before deploy.

## Validation

Exercise and record expected and observed results for:

- wrong workspace
- shared credential
- profile drift
- storage crossover
- event crossover
- teardown

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated Adobe sources before execution.
- Treat observed tenant or product behavior as environment-specific evidence, never a universal Adobe guarantee.
