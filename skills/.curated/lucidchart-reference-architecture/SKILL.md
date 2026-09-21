---
name: lucidchart-reference-architecture
description: 'Design a contract-grounded Lucid integration architecture across REST, Standard Import, editor extensions, and optional data connectors. Use when making system and boundary decisions. Trigger with "design Lucid architecture".'
argument-hint: "[requirements-path] [architecture-scope]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, lucidchart, architecture, extensions, data-connectors]
model: inherit
effort: high
compatibility: Designed for Claude Code; architecture decisions involving data movement, OAuth, hosting, or production mutation require accountable owner approval
---
# Lucid Integration Reference Architecture

## Overview

Select the smallest supported Lucid surface for the requirement and document trust, data, failure, and ownership boundaries before implementation.

## Prerequisites

- Functional requirements, data classification, users, service objectives, and failure tolerance
- Known Lucid product, ownership model, and plan/account constraints
- Current official contracts for candidate surfaces

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect the system and constraints, `WebFetch` for current Lucid contracts, and `Write` or `Edit` only for architecture records and diagrams in the approved project.

## Current Contract

- Use REST operations for documented server-side document/account workflows.
- Use Standard Import for deterministic file-driven document creation.
- Use an editor extension for in-editor UI, document content, and document data behavior.
- Add a data connector only when server-side source authentication, scheduled refresh, or documented connector webhook behavior is required.

## Authentication

Map each boundary to a principal: human/API key, OAuth user, OAuth account, extension, connector runtime, and upstream source. Define scopes, secret storage, rotation, revocation, consent, and audit evidence.

## Instructions

1. Capture actors, use cases, latency, volume, data classes, residency, ownership, and recovery objectives.
2. Re-fetch the candidate surface documentation; reject capabilities supported only by memory or third-party examples.
3. Draw component, trust-boundary, data-flow, and failure/recovery views.
4. For every edge, specify schema, identity, authorization, validation, retry/idempotency, retention, and observability.
5. Compare at least two viable options on complexity, supportability, least privilege, failure isolation, and reversibility.
6. Explicitly exclude unsupported generic document webhooks, document locking, universal quotas, and unverified cost assumptions.
7. Define canary, reconciliation, disaster recovery, ownership, and decommissioning.
8. Record the decision, evidence date, alternatives, assumptions, approval boundaries, and review trigger.

## Approval Boundaries

Do not register applications, provision hosting, move data, publish extensions, or commit to commercial terms during architecture design.

## Output

Return chosen surfaces, diagrams, principal/scope matrix, data contracts, failure model, options, decision, assumptions, owners, and approval gates.

## Error Handling

| Condition | Response |
|---|---|
| Required capability lacks official support | Mark the gap and redesign; do not invent an API. |
| Data ownership is unresolved | Stop the affected data flow at the trust boundary. |
| Connector adds no necessary server responsibility | Prefer the simpler editor-extension or import design. |

## Example

```text
decision=editor-extension+connector; reason=source-oauth-and-scheduled-sync; generic-document-webhooks=excluded; review=2026-Q4
```

## Resources

- [Official documentation map](references/official-docs.md)

## Next Steps

Convert the approved decision into threat model, contract tests, deployment gates, and an operations runbook.
