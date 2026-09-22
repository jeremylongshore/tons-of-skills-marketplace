---
name: exa-security-basics
description: >-
  Threat-model Exa credentials, query intent, retrieved web content, generated output, and retained operational evidence as separate trust boundaries. Use when operating or reviewing this Exa boundary. Trigger with "Exa security basics", "review Exa security basics", or "fix Exa security basics".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<data-class> <product-surface> <retention-mode>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, exa]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Exa work requires network access"
---
# Exa Security and Data Boundary

## Overview

Threat-model Exa credentials, query intent, retrieved web content, generated output, and retained operational evidence as separate trust boundaries. Treat credentials, queries, retrieved content, generated output, spend, and destructive state as separately governed boundaries.

## Prerequisites

- The target repository, environment, Exa team, product surface, and accountable owner.
- The workload's data classification, latency and freshness promise, cost ceiling, and retention policy.
- Current first-party documentation plus credentials only for a narrowly approved live check.

## Current Contract

Exa is SOC 2 Type II certified and offers enterprise controls such as Zero Data Retention and HIPAA enablement. HIPAA mode is request-scoped, supports only eligible Search and Contents cache-only retrieval, and rejects summaries or live freshness. Regional access restrictions can yield Cloudflare block pages rather than Exa JSON.

## Authentication

For normal REST work, inject `EXA_API_KEY` from an approved server-side secret manager and send it only as `Authorization: Bearer` to the configured first-party Exa API host. Team Management service keys, hosted MCP OAuth or enterprise managed authorization, and payment-protocol calls are separate trust models. Never print, commit, place in a URL, or expose a credential to an untrusted client.

## Instructions

1. Classify queries, URLs, retrieved content, outputs, identifiers, and credentials separately.
2. Confirm team plan and enterprise controls before asserting compliance.
3. Keep API and service keys server-side with narrow ownership and rotation.
4. Apply moderation, domain policy, output validation, and prompt-injection defenses.
5. Store only approved evidence and propagate deletion or retention decisions downstream.
6. Test credential revocation, policy denial, regional blocks, and incident escalation.

## Tool Discipline

Use Read, Glob, and Grep to inspect repository code, configuration, fixtures, and evidence. Use Write and Edit only for approved implementation or documentation changes. Do not call Exa, run paid research, create or alter a Monitor, Webset, Agent run, Batch, team, member, API key, budget, webhook, or deployment merely because this skill was invoked.

## Approval Boundaries

Require an accountable owner before live queries involving sensitive intent, production credentials, spend or rate-limit changes, forced live crawling, generated summaries, external delivery, deployment, member or key changes, schedule creation, or destructive cancellation, stopping, deletion, or revocation. Read-only repository inspection and synthetic offline validation do not authorize live vendor actions.

## Failure Modes

- SOC 2 certification does not automatically authorize a workload.
- HIPAA mode is not a global account toggle and does not support Agent, Answer, or livecrawl.
- Retrieved public text can still be malicious, copyrighted, personal, or policy-restricted.

## Output

Return the operation scope, environment, team and product surface, authorization class, contract and policy decisions, deterministic validation results, content-free identifiers, status and cost counts, risks, cleanup or rollback state, and a concise pass or fail receipt. Exclude credentials, raw queries, prompts, presigned URLs, retrieved content, generated output, and customer-derived data unless separately approved.

## Example

- An eligible HIPAA request uses instant or fast Search, cache-only text or highlights, and no summary or livecrawl.
- Finish with request or resource IDs, assertion counts, cost and terminal state, rollback or deletion status, and the decision owner; never reproduce secrets or retrieved content.

## Validation

Rerun the smallest relevant deterministic test, compare actual behavior with the requested outcome and current first-party contract, verify sensitive fields are absent from evidence, and confirm deadlines, terminal state, downstream retention, and rollback before reporting success.

## References

Review the dated first-party evidence map before relying on any endpoint, parameter, search type, price, limit, beta, compliance, identity, retry, or lifecycle claim.

- [Current first-party evidence map](references/official-docs.md)
