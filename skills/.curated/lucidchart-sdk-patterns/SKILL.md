---
name: lucidchart-sdk-patterns
description: 'Apply supported patterns with Lucid lucid-package and lucid-extension-sdk while treating installed types as authoritative. Use when implementing or reviewing editor extensions. Trigger with "Lucid SDK pattern".'
argument-hint: "[project-path] [feature]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, lucidchart, sdk, extensions, typescript]
model: inherit
effort: medium
compatibility: Designed for Claude Code; dependency changes, developer installation, new scopes, and publication require explicit project-owner approval
---
# Lucid SDK Implementation Patterns

## Overview

Implement an editor-extension feature from the installed SDK, project manifest, and official guidance—never from guessed type names or stale snippets.

## Prerequisites

- Existing extension project with lockfile, manifest, scripts, and pinned versions
- Defined user behavior, document/data boundary, scopes, and test fixture
- Current official Extension API and package CLI references

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect source, installed declarations, manifests, and tests; use `WebFetch` for current official docs; use `Write` or `Edit` only for bounded local changes and evidence.

## Current Contract

`lucid-package` supplies project tooling and `lucid-extension-sdk` supplies supported APIs and types. Official Lucid AI guidance says to consult documentation and types, avoid guessing APIs, use correct pnpm mode syntax, and request least extension scopes.

## Authentication

Editor bundles must not contain server secrets. Put source OAuth and confidential credentials behind an approved connector/server boundary. Review manifest scopes before any developer install.

## Instructions

1. Read repository instructions, package manifest, Lucid manifest, lockfile, scripts, and relevant tests.
2. Inspect installed SDK declaration/source files for the exact API, callback, return, error, and availability contract.
3. Re-fetch the corresponding official topic and note version/documentation drift.
4. Design a thin typed boundary that validates external data and converts errors into explicit user-safe states.
5. Implement the smallest feature using existing project patterns; avoid global mutable state and undocumented object shapes.
6. Add tests for success, invalid input, unavailable context, insufficient scope, cancellation, and partial failure.
7. Run project type/build/manifest/test commands using installed `--help` and correct package-manager argument passing.
8. Present dependency, scope, or developer-install changes for approval and record exact receipts.

## Approval Boundaries

Do not upgrade dependencies, broaden scopes, install developer packages, connect production data, or publish without approval.

## Output

Return SDK/CLI versions, inspected types/docs, chosen pattern, changed files, scopes, gate receipts, drift, and approval state.

## Error Handling

| Condition | Response |
|---|---|
| Documented example fails type checking | Follow the installed type and report version drift. |
| Needed API is absent | Stop and redesign with supported primitives; do not cast around it. |
| Feature requires a secret in the bundle | Introduce an approved server/connector boundary. |

## Example

```text
feature=data-refresh; sdk=pinned-lockfile; installed-types=inspected; typecheck=pass; manifest-scopes=unchanged
```

## Resources

- [Official documentation map](references/official-docs.md)

## Next Steps

Preserve the type-level and fixture regression tests before moving to developer-mode verification.
