---
name: bamboohr-deploy-integration
description: >-
  Deploy a BambooHR connector with tenant-isolated secrets, OAuth callback
  controls, durable token refresh, health probes, and staged rollback. Use when
  promoting an integration across environments. Trigger with "deploy BambooHR",
  "BambooHR production deployment", or "BambooHR environment promotion".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<environment> <deployment-target>"
version: 1.5.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, hr, bamboohr, deployment, operations]
model: inherit
effort: high
compatibility: Designed for Claude Code
---
# BambooHR Controlled Deployment

## Overview

Promote an already-tested BambooHR connector without baking one cloud vendor's
CLI into the skill. Separate application deployment, secret mutation, OAuth
registration, webhook replacement, data migration, and traffic cutover because
they have different approvals and rollback behavior.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The tenant, identity, and data scope only when approved live work is in scope.
- The current evidence register plus customer-specific permissions and agreements.

## Current Contract

The application must use the tenant-local BambooHR host. OAuth redirects are
exact HTTPS locations and refreshed tokens require application persistence.
Webhook destinations require HTTPS and creation yields a one-time verification
key. Health checks must not expose employee data or require broad HR permissions.

## Authentication

Create distinct identities/secrets per environment and tenant. Bind token records
to subject and tenant. Deployment health may verify local configuration and
dependencies; a live BambooHR readiness check must be separately approved,
read-only, low sensitivity, body-discarding, and rate bounded.

## Instructions

1. Record immutable artifact digest, source commit, configuration schema, target
   environment, tenant set, deployment owner, data migration, and rollback owner.
2. Diff configuration names and secret references without reading secret values.
   Verify no production credential appears in build args, images, logs, or previews.
3. Validate exact OAuth redirect URIs, trusted tenant mapping, encrypted token
   persistence, rotation callback, egress policy, TLS, and log redaction.
4. Run offline tests, schema checks, migration dry run, and synthetic webhook
   verification before deploying the immutable artifact.
5. Deploy dark or to a canary. Run local liveness/readiness first; then, if
   approved, one body-discarding company-information check with a request ID.
6. Drain or pause schedulers and queues during cutover so two versions do not
   race. Preserve idempotency and checkpoints across rollback.
7. Observe authentication failures, refresh failures, request errors, queue age,
   reconciliation, webhook verification, and cross-tenant alarms.
8. Promote or roll back against explicit thresholds. Revoke superseded secrets
   or webhook keys only after the new path is verified and separately approved.

## Tool Discipline

Use Read, Glob, and Grep to inspect deployment files and secret references. Use
Write/Edit only for approved manifests, configuration, and tests. This skill does
not run provider CLIs, authenticate, provision, deploy, rotate, or cut traffic.

## Approval Boundaries

Require separate approval for deployment, database migration, secret write,
OAuth redirect change, live readiness call, webhook replacement, traffic shift,
rollback, and revocation.

## Output

Return artifact digest, target/environment/tenant scope, config and secret diff,
preflight results, canary plan, health evidence, queue/checkpoint state, observed
metrics, approval receipts, and promote/rollback decision.

## Error Handling

- Token persistence unavailable: do not cut over an OAuth integration.
- Health probe leaks data: remove it and deploy a minimal local probe.
- Ambiguous active version or queue owner: stop schedulers before proceeding.
- Failed canary: roll back artifact/config together and preserve evidence.

## Examples

- "Deploy to Cloud Run" produces provider-neutral gates plus target-specific manifests.
- "Reuse staging keys in prod" is rejected in favor of environment isolation.

## Resources

Read [official evidence](references/official-docs.md) before production promotion.
