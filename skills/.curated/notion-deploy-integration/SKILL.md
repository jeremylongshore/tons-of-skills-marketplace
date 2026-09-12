---
name: notion-deploy-integration
description: >-
  Prepare and verify a Notion integration deployment with environment isolation, secret provenance, staged rollout, and rollback. Use when promoting an integration runtime. Trigger with "deploy Notion integration", "promote Notion worker", or "review Notion release".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<artifact> <target-environment> <release-id>"
version: 1.40.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, notion, deployment]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Notion actions require network access and explicit approval"
---
# Notion Integration Deployment Control

## Overview

Prepare and verify a Notion integration deployment with environment isolation, secret provenance, staged rollout, and rollback.. This workflow produces an auditable decision or artifact before any live action.

## Prerequisites

- Current first-party Notion documentation and the selected integration's tested API-version contract.
- A named workspace owner, content or data owner, and operation owner.
- Synthetic or approved non-production fixtures with secrets and workspace content removed.

## Current Contract

Deployment readiness depends on the tested SDK and API contract, connection configuration, shared fixture content, worker or queue topology, and rollback compatibility; a successful build is not a production acceptance test. Recheck the dated evidence map before relying on mutable fields, endpoints, versions, limits, or delivery behavior.

## Authentication

Bind each environment to distinct secret references and Notion connections. Never copy development tokens into production or expose secrets to preview builds.

## Instructions

1. Pin the artifact digest, dependency lock, selected API version, schema assumptions, and migration order.
2. Verify environment-specific connection, content access, webhook destination, queue, and observability bindings.
3. Run offline contract tests and a non-production read-only smoke test.
4. Produce a rollout plan with canary scope, concurrency, retry, write, and reconciliation guards.
5. Deploy only through the approved platform workflow and observe defined health signals.
6. Reconcile output and either promote or execute the tested rollback.

## Tool Discipline

Use Read, Glob, and Grep to inspect documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Invocation alone does not authorize network access, credentials, workspace content, user data, file transfer, deployment, capability or sharing changes, writes, spend, or deletion.

## Approval Boundaries

Require release-owner approval for production deployment and separate content-owner approval before enabling writes, subscriptions, or backfills.

## Error Handling

- Do not accept a health endpoint that never touches the configured dependency contract.
- Do not rotate a token and deploy code in one unreviewable step.
- Rollback if object-shape or reconciliation checks diverge.

## Output

Return the artifact and configuration receipts, gate matrix, rollout observations, reconciliation result, and rollback outcome. Identify assumptions, owners, expirations, and evidence gaps explicitly.

## Examples

- Canary a read-only query before enabling a write worker.
- Roll back a version migration when fixture and live shape differ.

## Validation

Exercise and record these paths with expected and observed results:

- artifact identity
- secret isolation
- preview isolation
- canary
- reconciliation
- rollback

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources before relying on mutable behavior.
- Treat observed tenant behavior as environment-specific evidence, never a universal Notion guarantee.
