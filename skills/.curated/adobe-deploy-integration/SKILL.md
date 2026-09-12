---
name: adobe-deploy-integration
description: >-
  Deploy an Adobe-backed service or App Builder application with isolated environments, immutable artifacts, canaries, observability, and rollback. Use when the task requires adobe integration deployment. Trigger with "deploy Adobe integration", "aio app deploy", or "promote Adobe app".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<artifact> <target-environment> <rollout-scope>"
version: 1.8.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, adobe, deployment]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Adobe actions require network access, appropriate entitlement and authentication, and explicit approval"
---
# Adobe Integration Deployment

## Overview

Deploy an Adobe-backed service or App Builder application with isolated environments, immutable artifacts, canaries, observability, and rollback. This workflow produces a reviewable artifact and evidence before any live side effect.

## Prerequisites

- Current first-party Adobe documentation for every selected service, API version, auth flow, limit, and lifecycle.
- Named product, identity, security, data, budget, release, and operations owners appropriate to the scope.
- Synthetic or approved non-production fixtures with secret and content canaries.

## Current Contract

AIO CLI v11 and later require Adobe IMS authentication for App Builder deploys: interactive aio login locally or OAuth Server-to-Server in CI. Runtime namespace auth is not a current deploy mechanism. Stage and Production workspaces are isolated. Recheck the dated evidence map before relying on mutable product behavior.

## Authentication

Bind deploy credentials and product credentials to the target environment. app.config.yaml is reviewed source; .env and .aio are local state and must not be committed.

## Instructions

1. Verify the artifact digest, dependency locks, configuration schema, tests, migration, and rollback artifact.
2. Resolve organization, project, workspace, service credentials, product profiles, storage, and event registrations.
3. Confirm the AIO CLI/auth path or external platform identity and fail closed on environment mismatch.
4. Deploy dark, verify configuration and logs, then run one approved read-only or synthetic smoke path.
5. Canary bounded traffic while watching auth, 429, jobs, queue age, spend, activations, and content-safe errors.
6. Promote or roll back from declared thresholds and preserve deployment, activity-log, cleanup, and owner receipts.

## Tool Discipline

Use Read, Glob, and Grep to inspect current documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Skill invocation alone does not authorize network access, credentials, Adobe content, consent, uploads, generation, spend, deployment, registration changes, replay, cancellation, or deletion.

## Approval Boundaries

Release owner approves production deployment; security approves credentials; data/budget owners approve live product calls; webhook or asset deletion needs separate approval.

## Error Handling

- Stop if the selected workspace differs from the review target.
- Do not commit .env or .aio.
- Rollback if artifact, auth, entitlement, storage, or observability evidence is missing.

## Output

Return artifact and environment identity, auth path, preflight, smoke/canary metrics, decision, rollback, cleanup, and owners. Mark assumptions, observed environment behavior, owners, evidence dates, and unresolved gaps explicitly.

## Examples

- Deploy to Stage and prove Production is unchanged.
- Exercise rollback after a synthetic entitlement failure.

## Validation

Exercise and record expected and observed results for:

- artifact mismatch
- workspace mismatch
- missing entitlement
- 429
- rollback
- cleanup

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated Adobe sources before execution.
- Treat observed tenant or product behavior as environment-specific evidence, never a universal Adobe guarantee.
