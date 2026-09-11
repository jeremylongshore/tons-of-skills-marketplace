---
name: cohere-prod-checklist
description: >-
  Issue an evidence-backed Cohere production go or no-go decision covering capacity, quality, security, operations, and rollback. Use when preparing to launch a Cohere workload. Trigger with "Cohere production checklist", "Cohere go live", or "Cohere launch review".
argument-hint: "[service] [environment]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- cohere
- production
model: inherit
effort: high
compatibility: Designed for Claude Code; live verification requires network access and an approved Cohere API key
---
# Cohere Production Readiness

## Overview

Convert a staged Cohere integration into a reversible production release with explicit owners, thresholds, and evidence.

## Prerequisites

- The target repository, runtime, environment, and accountable owner
- An approved Cohere team and key for any live verification
- Current quality, security, privacy, capacity, and change-control requirements

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect code, configuration, and evidence. Use `WebFetch` only for current Cohere primary documentation. Use `Write` or `Edit` only when the user requested implementation and the exact target files are known; never write credentials or customer content.

## Current Contract

- Public-facing workloads require the appropriate production key and acceptance of Cohere's current terms.
- Sensitive-use declarations can affect approval and capacity; verify the actual organization state.
- Models, limits, pricing, and deprecations must be checked at release time.
- Production readiness includes retrieval or task quality, not merely a successful API call.

## Authentication

Use an environment-specific key injected from an approved secret manager. Never print, persist, commit, or place `CO_API_KEY` in an example. Confirm access with the least costly bounded operation appropriate to the task, and treat key creation, rotation, revocation, role changes, and production-capacity requests as owner-approved actions.

## Instructions

1. Verify production key ownership, model availability, contractual data terms, and current capacity.
2. Attach offline and bounded live evaluations for quality, citations, safety, and failure handling.
3. Confirm secret isolation, tenant boundaries, redaction, timeouts, retries, and circuit breaking.
4. Set latency, error, throttle, cost, quality, and queue thresholds with named responders.
5. Run a staged canary with rollback criteria and no unapproved model fallback.
6. Record GO or NO-GO, approvers, evidence links, release window, and rollback command owner.

## Approval Boundaries

Do not expose or rotate keys, change Cohere Team roles, accept commercial terms, enable sensitive production data, increase spend or capacity, switch production models, send a support bundle, or execute model-proposed side effects without the accountable owner's approval. Keep diagnosis read-only unless implementation was requested.

## Output

Return the resolved API and model contract, files or settings inspected, evidence collected, validation result, remaining risk, owner, and rollback or next action. Redact keys, authorization headers, prompts, retrieved documents, embeddings, customer identifiers, and unrestricted environment output.

## Error Handling

| Condition | Response |
|---|---|
| Trial key | Do not launch a public production workload on evaluation capacity. |
| No quality gate | Block release until representative evaluation thresholds exist. |
| No rollback | Block release until traffic can be restored safely. |
| Model near retirement | Migrate or obtain an explicit time-bound exception. |

## Examples

Use this compact handoff shape to keep the selected scope, validation evidence, and operational result reviewable.

Input:

```text
service=support-rag; canary=5%; quality-threshold=approved; rollback=ready
```

Expected handoff:

```text
decision=GO; model=resolved; capacity=verified; evidence=linked
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Going live](https://docs.cohere.com/docs/going-live)
- [Deprecations](https://docs.cohere.com/docs/deprecations)
