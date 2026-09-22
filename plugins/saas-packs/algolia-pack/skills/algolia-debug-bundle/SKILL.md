---
name: algolia-debug-bundle
description: >-
  Collect a bounded, secret-safe Algolia diagnostic bundle for an incident or support escalation. Use when a reproducible search or indexing failure needs portable evidence. Trigger with "Algolia debug bundle", "collect Algolia diagnostics", or "Algolia support evidence".
argument-hint: "[repository-path] [incident-id]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- algolia
- diagnostics
model: inherit
effort: medium
compatibility: Designed for Claude Code
---
# Algolia Redacted Debug Bundle

## Overview

This skill assembles code, configuration shape, client versions, redacted request evidence, task IDs, and reproduction steps without copying API keys, full records, or unrestricted account data.

## Prerequisites

- A named repository, environment, and Algolia application or index in scope
- The local lockfile and installed client types as implementation authority
- A safe read-only query or explicitly disposable test target
- Current first-party documentation for any provider behavior that affects the change

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect local code, configuration names, tests, and dependency versions. Use `WebFetch` only for current official Algolia documentation. Use `Write` or `Edit` only after identifying the target files, constraints, and verification plan.

## Current Contract

- Prefer local configuration names and hashes over live secret or key inspection.
- Collect the smallest failing request and response; redact credentials, personal data, and unrelated record fields.
- Include timestamps, regions or hosts, request IDs, task IDs, and client versions when available.
- Create a manifest before sharing so reviewers can see every included file and redaction rule.

## Authentication

Do not fetch, print, validate, or transmit secret values. If a support workflow needs account evidence, use a separately approved read-only credential and preserve only redacted results.

## Instructions

1. Define the incident, recipient, allowed data classes, time window, and maximum bundle size.
2. Inspect local dependencies, wrapper code, environment variable names, index configuration, and recent relevant logs.
3. Reproduce one safe read or disposable-index operation and capture redacted request metadata.
4. Scan every artifact for keys, tokens, emails, user tokens, record payloads, and unrelated secrets.
5. Build a plain-text manifest with collection source, hash, redaction action, and omission reason.
6. Review the manifest and bundle contents before any external transfer.

## Approval Boundaries

Do not use an Admin key for diagnosis, archive an entire environment, collect production records wholesale, or send the bundle automatically.

## Output

Return the reproduction, dependency versions, redacted evidence, artifact manifest, secret-scan result, omitted evidence, and a human-approved handoff path.

## Error Handling

| Condition | Response |
|---|---|
| Potential secret found | Remove the artifact or redact it, then rescan. |
| Reproduction mutates production | Stop and move to a disposable target. |
| Bundle exceeds limit | Narrow the time window and fields. |
| Required evidence is sensitive | Describe the gap and request an approved channel. |

## Examples

Use this compact input and expected handoff to calibrate scope and evidence quality.

Input:

```text
incident=ALG-42; window=10m; target=products_readonly; bundle-limit=5MB
```

Expected handoff:

```text
artifacts=7; secret-scan=pass; production-records=0; transfer=pending-review
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [API keys](https://www.algolia.com/doc/guides/security/api-keys)
- [Security best practices](https://www.algolia.com/doc/guides/security/security-best-practices)
- [Algolia status](https://status.algolia.com/)
