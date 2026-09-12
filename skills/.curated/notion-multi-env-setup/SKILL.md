---
name: notion-multi-env-setup
description: >-
  Define isolated development, staging, and production Notion connections, secrets, content roots, and promotion rules. Use when an integration spans multiple environments. Trigger with "separate Notion environments", "configure Notion staging", or "audit Notion env isolation".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<environments> <connection-model> <promotion-policy>"
version: 1.40.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, notion, environments]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Notion actions require network access and explicit approval"
---
# Notion Multi-Environment Isolation

## Overview

Define isolated development, staging, and production Notion connections, secrets, content roots, and promotion rules.. This workflow produces an auditable decision or artifact before any live action.

## Prerequisites

- Current first-party Notion documentation and the selected integration's tested API-version contract.
- A named workspace owner, content or data owner, and operation owner.
- Synthetic or approved non-production fixtures with secrets and workspace content removed.

## Current Contract

Notion has no universal environment abstraction for integrations. Isolation comes from distinct connections or tokens, workspace/content boundaries, secrets, destinations, queues, webhooks, and application guards. Recheck the dated evidence map before relying on mutable fields, endpoints, versions, limits, or delivery behavior.

## Authentication

Provision unique secret references and fingerprints per environment. Never fall back from a missing non-production secret to production.

## Instructions

1. Inventory each environment's workspace, connection, owner, capabilities, shared roots, webhook, queue, and destination.
2. Define immutable environment identifiers and fail-closed startup assertions.
3. Separate secrets, object IDs, callback URLs, encryption keys, and telemetry labels.
4. Use synthetic fixtures outside production and prevent configuration fallbacks.
5. Promote code artifacts independently from credentials and content configuration.
6. Run cross-environment leak tests and record rotation, teardown, and break-glass owners.

## Tool Discipline

Use Read, Glob, and Grep to inspect documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Invocation alone does not authorize network access, credentials, workspace content, user data, file transfer, deployment, capability or sharing changes, writes, spend, or deletion.

## Approval Boundaries

Require each workspace owner before sharing content; require release approval for production binding and security approval for break-glass access.

## Error Handling

- Abort if two environments share a credential fingerprint.
- Do not infer environment from a page title or hostname alone.
- Never copy production exports into lower environments without governance.

## Output

Return the environment matrix, fingerprints, shared-root map, promotion gates, leak-test results, lifecycle owners, and exceptions. Identify assumptions, owners, expirations, and evidence gaps explicitly.

## Examples

- Prove staging cannot retrieve a production fixture.
- Promote one artifact while retaining distinct environment credentials.

## Validation

Exercise and record these paths with expected and observed results:

- missing config
- fallback blocked
- fingerprint collision
- wrong workspace
- webhook isolation
- teardown

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources before relying on mutable behavior.
- Treat observed tenant behavior as environment-specific evidence, never a universal Notion guarantee.
