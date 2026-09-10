---
name: algolia-security-basics
description: >-
  Audit and harden Algolia credentials, record exposure, index restrictions, and tenant search controls. Use when reviewing frontend keys, backend ACLs, key rotation, or data visibility. Trigger with "secure Algolia", "Algolia key audit", or "Algolia security review".
argument-hint: "[repository-path] [application-id]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.7.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- algolia
- security
model: inherit
effort: medium
compatibility: Designed for Claude Code
---
# Algolia Security Baseline

## Overview

This skill reviews the actual security boundary of an Algolia integration. A browser search-only key is intentionally visible, so record contents, index restrictions, secured-key design, and abuse controls remain essential.

## Prerequisites

- A named repository, environment, and Algolia application or index in scope
- The local lockfile and installed client types as implementation authority
- A safe read-only query or explicitly disposable test target
- Current first-party documentation for any provider behavior that affects the change

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect local code, configuration names, tests, and dependency versions. Use `WebFetch` only for current official Algolia documentation. Use `Write` or `Edit` only after identifying the target files, constraints, and verification plan.

## Current Contract

- Never index data that must remain secret merely because an attribute is not displayed.
- Use custom main keys with minimum ACLs and restrictions; rotate long-lived keys under an owned policy.
- Generate secured keys on a trusted backend and require restrictions appropriate to the user or tenant.
- Treat referer restrictions, rate limits, filters, and ACLs as layers whose current behavior must be verified.

## Authentication

Inspect key metadata without exporting secret values. Admin credentials stay out of application defaults, browser bundles, logs, support artifacts, and developer examples.

## Instructions

1. Inventory every application ID, environment variable, client constructor, key owner, ACL, restriction, and exposed index.
2. Scan source, built assets, history, logs, and documentation for write-capable key exposure.
3. Review record fields and index settings for data a search-only client could retrieve or scrape.
4. Map backend operations to custom key ACLs and tenant search to secured-key restrictions.
5. Test allowed and denied paths, including cross-index and cross-tenant attempts.
6. Document rotation, revocation, incident response, ownership, exceptions, and retest dates.

## Approval Boundaries

Do not rotate or revoke production keys, alter index restrictions, or remove access until dependencies and recovery paths are verified.

## Output

Return the key and actor inventory, exposure findings, data-visibility review, allowed/denied tests, remediation plan, rotation procedure, and residual risks.

## Error Handling

| Condition | Response |
|---|---|
| Write key found in browser | Contain and rotate through the incident process. |
| Search key exposes sensitive records | Remove the data and review index design. |
| Tenant restriction bypassed | Disable affected path and correct server-generated restrictions. |
| Key owner unknown | Treat it as orphaned and investigate before revocation. |

## Examples

Use this compact input and expected handoff to calibrate scope and evidence quality.

Input:

```text
app=APP…9X; actors=browser,indexer,ops; indices=products_*
```

Expected handoff:

```text
browser=search-only; indexer=custom-minimum; tenant-denial=pass; exposed-write-key=none
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [API keys](https://www.algolia.com/doc/guides/security/api-keys)
- [Secured API keys](https://www.algolia.com/doc/guides/building-search-ui/going-further/api-keys-security/react)
- [Security best practices](https://www.algolia.com/doc/guides/security/security-best-practices)
