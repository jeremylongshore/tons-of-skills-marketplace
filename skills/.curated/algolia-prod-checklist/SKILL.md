---
name: algolia-prod-checklist
description: >-
  Run a fail-closed production readiness review for an Algolia-backed search release. Use when promoting new indices, settings, credentials, UI behavior, or event tracking. Trigger with "Algolia production checklist", "search go-live", or "Algolia launch review".
argument-hint: "[repository-path] [release-sha]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.7.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- algolia
- production
model: inherit
effort: medium
compatibility: Designed for Claude Code
---
# Algolia Production Readiness Review

## Overview

This skill consolidates the release evidence needed to decide whether an Algolia search surface is ready. It uses organization-owned SLOs and policies rather than hard-coded latency or response targets.

## Prerequisites

- A named repository, environment, and Algolia application or index in scope
- The local lockfile and installed client types as implementation authority
- A safe read-only query or explicitly disposable test target
- Current first-party documentation for any provider behavior that affects the change

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect local code, configuration names, tests, and dependency versions. Use `WebFetch` only for current official Algolia documentation. Use `Write` or `Edit` only after identifying the target files, constraints, and verification plan.

## Current Contract

- Bind all evidence to a release SHA, target application, index state, and source snapshot.
- Verify least-privilege browser, server, indexing, monitoring, and event credentials separately.
- Exercise representative relevance, filter, facet, empty-state, error, and accessibility paths.
- Require tested rollback for both application code and index or settings state.

## Authentication

Confirm secret-store ownership, key ACLs, index restrictions, rotation, and exposure scans. Never include credential values in the readiness packet.

## Instructions

1. Freeze the candidate SHA and inventory code, records, settings, synonyms, rules, keys, and event surfaces.
2. Run schema, unit, integration, security, accessibility, and representative query gates.
3. Verify indexing tasks, counts, sentinel records, environment mapping, and rollback target.
4. Review observability against owned SLOs and exercise alert or incident routing.
5. Validate event consent, stable user tokens, query IDs, and provider event validation where applicable.
6. Record pass, fail, waiver owner, evidence link, expiration, and final go/no-go decision.

## Approval Boundaries

Do not waive a failed security, rollback, data-integrity, or required branch-protection gate without the named authority and durable evidence.

## Output

Return a release-bound checklist, evidence links, failed and waived gates, credential matrix, rollback rehearsal, approvers, and explicit go/no-go outcome.

## Error Handling

| Condition | Response |
|---|---|
| Evidence belongs to another SHA | Rerun or reject it. |
| Rollback not rehearsed | Hold production promotion. |
| Threshold has no owner | Treat it as observation, not a gate. |
| Required gate pending | Outcome remains no-go. |

## Examples

Use this compact input and expected handoff to calibrate scope and evidence quality.

Input:

```text
release=abc123; app=production; index=products_20260910; source=snap-184
```

Expected handoff:

```text
required=31/31-pass; waivers=0; rollback=rehearsed; decision=go
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [API keys](https://www.algolia.com/doc/guides/security/api-keys)
- [Sending and managing data](https://www.algolia.com/doc/guides/sending-and-managing-data)
- [Sending events](https://www.algolia.com/doc/guides/sending-events)
