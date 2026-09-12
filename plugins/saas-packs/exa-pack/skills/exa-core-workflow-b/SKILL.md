---
name: exa-core-workflow-b
description: >-
  Run asynchronous Exa Agent research with a bounded schema, effort, terminal-state policy, citations, and cleanup decision. Use when operating or reviewing this Exa boundary. Trigger with "Exa core workflow b", "review Exa core workflow b", or "fix Exa core workflow b".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<research-task> <effort> <output-schema>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, exa]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Exa work requires network access"
---
# Exa Agent Run Lifecycle

## Overview

Run asynchronous Exa Agent research with a bounded schema, effort, terminal-state policy, citations, and cleanup decision. Treat credentials, queries, retrieved content, generated output, spend, and destructive state as separately governed boundaries.

## Prerequisites

- The target repository, environment, Exa team, product surface, and accountable owner.
- The workload's data classification, latency and freshness promise, cost ceiling, and retention policy.
- Current first-party documentation plus credentials only for a narrowly approved live check.

## Current Contract

Agent runs are asynchronous unless streamed. A created run returns an ID that must be polled, streamed, stopped, cancelled, or deleted through the Agent lifecycle. Fixed effort provides a predictable price; auto and beta max are usage-metered. Structured output and grounding require separate validation.

## Authentication

For normal REST work, inject `EXA_API_KEY` from an approved server-side secret manager and send it only as `Authorization: Bearer` to the configured first-party Exa API host. Team Management service keys, hosted MCP OAuth or enterprise managed authorization, and payment-protocol calls are separate trust models. Never print, commit, place in a URL, or expose a credential to an untrusted client.

## Instructions

1. Translate the approved research question into a narrow query and optional system prompt.
2. Choose fixed effort or an explicit metered cap and define the output schema.
3. Create one run and persist its content-free run ID.
4. Poll or consume server-sent events with a deadline and terminal-state handling.
5. Validate structured fields, grounding, citations, and cost independently.
6. Stop, cancel, retain, or delete the run according to the approved evidence policy.

## Tool Discipline

Use Read, Glob, and Grep to inspect repository code, configuration, fixtures, and evidence. Use Write and Edit only for approved implementation or documentation changes. Do not call Exa, run paid research, create or alter a Monitor, Webset, Agent run, Batch, team, member, API key, budget, webhook, or deployment merely because this skill was invoked.

## Approval Boundaries

Require an accountable owner before live queries involving sensitive intent, production credentials, spend or rate-limit changes, forced live crawling, generated summaries, external delivery, deployment, member or key changes, schedule creation, or destructive cancellation, stopping, deletion, or revocation. Read-only repository inspection and synthetic offline validation do not authorize live vendor actions.

## Failure Modes

- Run creation is not completion.
- A schema-valid result can still be weakly grounded or out of scope.
- Cancel, stop, and delete have different operational intent and must not be conflated.

## Output

Return the operation scope, environment, team and product surface, authorization class, contract and policy decisions, deterministic validation results, content-free identifiers, status and cost counts, risks, cleanup or rollback state, and a concise pass or fail receipt. Exclude credentials, raw queries, prompts, presigned URLs, retrieved content, generated output, and customer-derived data unless separately approved.

## Example

- Create a low-effort company-verification run with a closed JSON schema, poll to completion, and retain only IDs, verdict, citations, and cost.
- Finish with request or resource IDs, assertion counts, cost and terminal state, rollback or deletion status, and the decision owner; never reproduce secrets or retrieved content.

## Validation

Rerun the smallest relevant deterministic test, compare actual behavior with the requested outcome and current first-party contract, verify sensitive fields are absent from evidence, and confirm deadlines, terminal state, downstream retention, and rollback before reporting success.

## References

Review the dated first-party evidence map before relying on any endpoint, parameter, search type, price, limit, beta, compliance, identity, retry, or lifecycle claim.

- [Current first-party evidence map](references/official-docs.md)
