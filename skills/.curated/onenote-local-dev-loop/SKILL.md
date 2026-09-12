---
name: onenote-local-dev-loop
description: >-
  Create a repeatable local OneNote development loop using synthetic fixtures, mocks, and an explicitly approved delegated sandbox. Use when implementing or debugging without touching real notebooks. Trigger with "develop OneNote locally", "mock OneNote API", or "set up OneNote sandbox".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<repository> <feature> <sandbox-user>"
version: 1.7.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, onenote, development]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live OneNote actions require network access, delegated authentication, and explicit approval"
---
# OneNote Isolated Development Loop

## Overview

Create a repeatable local OneNote development loop using synthetic fixtures, mocks, and an explicitly approved delegated sandbox.. This workflow produces an auditable decision or artifact before any live action.

## Prerequisites

- Current first-party Microsoft Graph OneNote documentation and the selected integration's tested contract.
- Named identity, content, workload, security, and operations owners appropriate to the requested scope.
- Synthetic or approved non-production fixtures with secrets and real notebook content removed.

## Current Contract

Offline fixtures should model v1.0 roots, opaque next links, constrained input HTML, normalized output HTML, generated update IDs, Graph error envelopes, and OneNote 429 responses without Retry-After. Recheck the dated evidence map before relying on mutable permissions, limits, SDK behavior, supported resources, or cloud availability.

## Authentication

Use a dedicated sandbox user and encrypted delegated cache. Production tokens, tenant IDs, notebook IDs, titles, bodies, and binary resources never become fixtures.

## Instructions

1. Pin runtime and Graph SDK dependencies and place OneNote calls behind a narrow client boundary.
2. Create synthetic hierarchy, paging, HTML, update-target, error, and throttling fixtures with secret canaries.
3. Implement offline unit and contract tests before any network call.
4. Add a production-target guard based on explicit environment, tenant alias, user alias, and fixture IDs.
5. Run one approved read and optionally one reversible write in the delegated sandbox.
6. Reset the fixture, scan for production identifiers, and preserve the test and cleanup receipt.

## Tool Discipline

Use Read, Glob, and Grep to inspect documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Invocation alone does not authorize network access, delegated credentials, tenant or notebook content, consent, file transfer, deployment, writes, spend, sharing changes, or deletion.

## Approval Boundaries

Require the sandbox user before live access and explicit content-owner approval for writes, uploads, copies, sharing, or deletion.

## Error Handling

- Fail closed if environment or user binding is absent.
- Do not snapshot live page bodies into source control.
- Do not make tests depend on undocumented search, delta, or webhook behavior.

## Output

Return the dependency contract, fixture manifest, test commands, sandbox binding, live receipt, cleanup, and residual risks. Identify assumptions, owners, expirations, and evidence gaps explicitly.

## Examples

- Test three pages across two opaque response pages.
- Update one synthetic target and verify normalized output before restoring it.

## Validation

Exercise and record these paths with expected and observed results:

- production guard
- secret canary
- opaque paging
- HTML normalization
- 429
- sandbox cleanup

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources before relying on mutable behavior.
- Treat observed tenant behavior as environment-specific evidence, never a universal OneNote guarantee.
