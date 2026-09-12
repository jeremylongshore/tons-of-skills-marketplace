---
name: mistral-security-basics
description: >-
  Threat-model Mistral credentials, untrusted content, model output, tools, files, and tenant access. Use when securing or reviewing an integration. Trigger with "secure Mistral", "audit Mistral prompts", or "threat model a Mistral app".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<system-boundary> <data-class> <tool-surface>"
version: 1.14.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, mistral, security]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live or external Mistral actions require network access and explicit approval"
---
# Mistral Security Boundary

## Overview

Apply controls at the application boundary because model instructions do not enforce identity, tenancy, authorization, or side-effect safety. Treat user content, retrieval, files, and output as untrusted.

## Prerequisites

- A data-flow diagram covering browser, app, Mistral, stores, and tools.
- Credential, retention, tenant, moderation, and incident policies.
- An inventory of stateful APIs, files, retrieval stores, and actions.

## Current Contract

Bearer credentials authorize provider calls but not application users. Classifiers can support policy but do not replace controls. ZDR eligibility differs between stateless and stateful products.

## Authentication

Keep keys server-side and environment-scoped; rotate on exposure. Enforce user and tenant authorization before retrieval, provider calls, files, and tools.

## Instructions

1. Map trust boundaries and classify prompts, outputs, embeddings, files, logs, and IDs.
2. Remove credentials and privileged instructions from browser/untrusted contexts.
3. Separate trusted policy from untrusted content and delimit retrieved text as data.
4. Validate output structure and safety before render, storage, or tool use.
5. Authorize tools via closed registry, schemas, least privilege, deadlines, and idempotency.
6. Test injection, cross-tenant access, unsafe output, exfiltration, duplicates, and rotation.

## Tool Discipline

Use Read, Glob, and Grep to inspect code, locks, configuration, tests, and evidence. Use Write and Edit only for approved repository changes. Invocation alone does not authorize network calls, paid usage, uploads, stateful resources, admin mutations, deployments, or deletion.

## Approval Boundaries

Require approval for sensitive data, uploads, stateful APIs, tools, policy changes, retention, or live attack testing. Model output never grants authority.

## Error Handling

- Prompt wording cannot enforce access control.
- Moderation success does not prove correctness or tool safety.
- Assuming ZDR for Files, Batch, Agents, Conversations, or other stateful products is unsafe.

## Output

Return assets, threats, controls, residual risks, data/API boundary, tests, owners, and rollback. Exclude live secrets and customer data.

## Examples

- Reject retrieved text asking for a system secret.
- Require fresh app authorization before a proposed refund tool.

## Validation

Run synthetic abuse cases across input, retrieval, output, rendering, and tools; confirm tenant filters and rotation independently.

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources before relying on mutable endpoints, models, limits, prices, preview status, or retention.
- Record live account observations as environment-specific evidence, not universal Mistral guarantees.
