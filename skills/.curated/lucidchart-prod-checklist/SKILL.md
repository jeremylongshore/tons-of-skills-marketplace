---
name: lucidchart-prod-checklist
description: 'Run a fail-closed production-readiness review for a Lucid REST, Standard Import, extension, or data connector integration. Use when preparing a production launch or material change. Trigger with "Lucid production checklist".'
argument-hint: "[project-path] [release-id]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, lucidchart, production-readiness, governance, release]
model: inherit
effort: high
compatibility: Designed for Claude Code; production launch, publication, credentials, and rollback execution require accountable owner approval
---
# Lucid Production Readiness Gate

## Overview
Prove a Lucid integration is supportable, secure, reversible, and contract-grounded before authorizing production use.

## Prerequisites
- Immutable release revision and artifacts with provenance
- Named service, data, security, and rollback owners
- Current architecture, data classification, scope matrix, runbook, and service objectives

## Tool Discipline
Use `Read`, `Glob`, and `Grep` to verify repository evidence, `WebFetch` for current Lucid contracts and status, and `Write` or `Edit` only for the local gate receipt and approved documentation fixes.

## Current Contract
Readiness must match the actual surface: REST credential and version headers, Standard Import constraints, Extension API scopes and bundle behavior, and connector hosting/OAuth/webhook responsibilities. A generic green checklist is insufficient.

## Authentication
Verify principal type, least scopes, secret-store location, owner, rotation, revocation, redirect URIs, and break-glass procedure without exposing values.

## Instructions
1. Pin revision, artifacts, dependencies, SDK/CLI versions, manifests, fixtures, and target environment.
2. Re-fetch exact official pages for authentication, scopes, headers, limits, and the chosen integration surface.
3. Verify build, type, manifest, schema, secret, dependency, fixture, migration, and rollback gates from clean state.
4. Exercise happy path, invalid input, insufficient scope, throttling, partial failure, ambiguous response, upstream outage, and rollback.
5. Reconcile data lineage, retention, deletion, ownership, document destinations, and connector/webhook behavior.
6. Verify logs are redacted; alerts, dashboards, status dependency, on-call, escalation bundle, and runbook are usable.
7. Record every control as PASS, FAIL, or NOT APPLICABLE with evidence; unresolved critical controls fail closed.
8. Present blast radius, canary, monitoring, publication/deployment actions, and rollback for explicit production approval.

## Approval Boundaries
This skill reports readiness; it never treats a checklist completion as authorization to publish, deploy, rotate credentials, or mutate production.

## Output
Return release identity, gate matrix, official evidence date, test receipts, risks, owners, approval state, canary plan, and rollback evidence.

## Error Handling
| Condition | Response |
|---|---|
| Critical evidence is missing or stale | Mark FAIL and stop release recommendation. |
| Rollback is documented but untested | Mark FAIL until restored in a representative environment. |
| Ownership is ambiguous | Block the affected capability from production. |

## Example
```text
release=1.8.0; pass=27; fail=1; na=3; blocker=connector-rollback; production-approved=no
```

## Resources
- [Official documentation map](references/official-docs.md)

## Next Steps
Resolve all release blockers, rerun from the immutable revision, and obtain recorded production approval.
