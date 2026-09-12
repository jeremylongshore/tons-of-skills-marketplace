---
name: onenote-sdk-patterns
description: >-
  Build a testable Microsoft Graph OneNote client boundary with delegated auth, opaque pagination, HTML operations, errors, and throttling. Use when writing or reviewing integration code. Trigger with "design OneNote client", "review OneNote SDK", or "update OneNote patterns".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<language> <operations> <location-types>"
version: 1.7.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, onenote, sdk]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live OneNote actions require network access, delegated authentication, and explicit approval"
---
# OneNote Versioned Client Boundary

## Overview

Build a testable Microsoft Graph OneNote client boundary with delegated auth, opaque pagination, HTML operations, errors, and throttling.. This workflow produces an auditable decision or artifact before any live action.

## Prerequisites

- Current first-party Microsoft Graph OneNote documentation and the selected integration's tested contract.
- Named identity, content, workload, security, and operations owners appropriate to the requested scope.
- Synthetic or approved non-production fixtures with secrets and real notebook content removed.

## Current Contract

SDK versions change independently from Graph v1.0. Keep stable REST semantics behind typed operations, preserve opaque next links, retain Graph error and request identifiers, and treat generated snippets as starting evidence rather than a pinned package contract. Recheck the dated evidence map before relying on mutable permissions, limits, SDK behavior, supported resources, or cloud availability.

## Authentication

Inject a delegated credential provider bound to app, tenant, user, environment, and scopes. Application credentials and token logging are forbidden for OneNote operations.

## Instructions

1. Inventory runtime, installed SDK, target v1.0 operations, locations, and generated-code assumptions.
2. Define typed read hierarchy, page-content, create, update, and operation-result contracts.
3. Centralize delegated auth, request IDs, error classification, throttling, timeouts, and redaction.
4. Model opaque next links and semantic HTML normalization without leaking transport details to callers.
5. Add offline contract fixtures for additive fields, paging, errors, 429 without Retry-After, and ambiguous writes.
6. Canary the boundary against one approved synthetic root and record the compatibility matrix.

## Tool Discipline

Use Read, Glob, and Grep to inspect documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Invocation alone does not authorize network access, delegated credentials, tenant or notebook content, consent, file transfer, deployment, writes, spend, sharing changes, or deletion.

## Approval Boundaries

Require code-owner approval for implementation changes and the sandbox owner for live tests. Live writes need a separate content-owner approval.

## Error Handling

- Do not hardcode a remembered latest SDK version.
- Do not rebuild next links or silently retry ambiguous writes.
- Fail closed when delegated user or location binding is absent.

## Output

Return the client contract, dependency evidence, auth binding, operation types, fixtures, compatibility results, and migration notes. Identify assumptions, owners, expirations, and evidence gaps explicitly.

## Examples

- Paginate a synthetic section across multiple opaque links.
- Preserve a OneNote inner error and request identifier without returning page content.

## Validation

Exercise and record these paths with expected and observed results:

- additive field
- opaque link
- normalized HTML
- 429
- ambiguous write
- revoked session

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources before relying on mutable behavior.
- Treat observed tenant behavior as environment-specific evidence, never a universal OneNote guarantee.
