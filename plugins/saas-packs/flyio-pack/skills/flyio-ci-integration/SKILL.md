---
name: flyio-ci-integration
description: >-
  Design a least-privilege Fly.io CI lane with deterministic validation, deployment, and rollback evidence. Use when wiring or auditing automated deployments. Trigger with: "add Fly.io CI", "harden Fly deploy workflow", "rotate Fly CI token".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[app-environment-and-workflow]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - flyio
  - ci-cd
  - deploy-token
  - change-control
compatibility: 'Requires a Fly.io app, an approved CI system, an app-scoped or organization-scoped token, and a protected deployment environment.'
---

# Fly.io CI Deployment Control

## Overview

Build CI as a controlled release system rather than a single deploy command. Separate pull-request validation from authenticated deployment, bind production to an immutable revision, and retain enough evidence to identify and reverse the release.

## Prerequisites

- Named app, organization, environment, release owner, and rollback owner
- Protected CI environment with an approved secret manager
- Health endpoint or other deployment check and a tested prior release

## Instructions

### Step 1: Separate validation from deployment

Run secret-free configuration, container, and contract checks on pull requests. Permit authenticated Fly.io access only in a protected post-merge or manually approved environment.

### Step 2: Issue the narrowest token

Use an app-scoped deploy token for one app, an organization token only for approved multi-app workflows, or a read-only token for observation. Set an explicit expiry and store only the secret reference.

### Step 3: Pin the release inputs

Bind source commit, image digest, flyctl setup action or binary version, target app, configuration hash, and deployment strategy before execution.

### Step 4: Validate the candidate

Check the rendered app configuration, image startup contract, health checks, release command, volume constraints, and rollback target without changing production.

### Step 5: Deploy through one serialized lane

Use environment concurrency so two production releases cannot race. Capture the release identifier and wait for health checks rather than treating command exit alone as success.

### Step 6: Verify and close

Probe the approved endpoint, inspect aggregate health and Machine state, reconcile the running image, and either record success or invoke the tested rollback.

## Authentication

Expose the token to the deployment step as `FLY_API_TOKEN` or `FLY_ACCESS_TOKEN` only. The provider recommends scoped tokens created with `fly tokens create`; do not use the deprecated hidden `fly auth token` output in CI. Mask the value and revoke it after suspected exposure.

## Tool Discipline

Use Read and Grep to inspect application configuration, deployment evidence, provider documentation, fixtures, logs, schemas, and existing tests before proposing a change. Use Write or Edit only for an approved plan, configuration, implementation, test, or redacted receipt. Do not create, deploy, scale, restart, stop, suspend, destroy, rotate, revoke, expose, or migrate live Fly.io resources without explicit operator approval.

## Output

- CI trust-boundary and approval map
- Pinned workflow with validation, deploy, health, and rollback stages
- Release receipt containing revision, image, app, strategy, checks, and token reference

Return the target organization, app, environment, region set, Machine or database identifiers, source-contract fingerprint, evidence, unresolved risks, rollback state, and final decision without exposing tokens, secrets, connection strings, or customer data.

## Examples

A production workflow validates `fly.toml` without credentials on every pull request. After merge, a protected environment supplies an expiring app deploy token, serializes `fly deploy --strategy rolling`, verifies health, and retains the previous image as the rollback target.

## Error Handling

| Failure | Response |
| --- | --- |
| Token sees no app | Confirm token scope and app name; scoped tokens can filter listings instead of returning an explicit authorization error. |
| Health checks fail | Stop promotion, preserve logs and Machine state, and roll back to the recorded healthy release. |
| Concurrent release detected | Cancel the newer lane or wait for the active release; never interleave two production updates. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Machines API setup](https://fly.io/docs/machines/api/working-with-machines-api/)
- [Automation and tokens](https://fly.io/docs/flyctl/integrating/)
- [App configuration](https://fly.io/docs/reference/configuration/)
- [Deploy an app](https://fly.io/docs/launch/deploy/)
- [Health checks](https://fly.io/docs/reference/health-checks/)
