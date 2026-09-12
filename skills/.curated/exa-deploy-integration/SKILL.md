---
name: exa-deploy-integration
description: >-
  Deploy an Exa integration with server-side credentials, bounded concurrency, canary controls, and explicit rollback of scheduled work. Use when operating or reviewing this Exa boundary. Trigger with "Exa deploy integration", "review Exa deploy integration", or "fix Exa deploy integration".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<service> <platform> <environment>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, exa]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Exa work requires network access"
---
# Exa Reversible Deployment Workflow

## Overview

Deploy an Exa integration with server-side credentials, bounded concurrency, canary controls, and explicit rollback of scheduled work. Treat credentials, queries, retrieved content, generated output, spend, and destructive state as separately governed boundaries.

## Prerequisites

- The target repository, environment, Exa team, product surface, and accountable owner.
- The workload's data classification, latency and freshness promise, cost ceiling, and retention policy.
- Current first-party documentation plus credentials only for a narrowly approved live check.

## Current Contract

Production workers should call Exa from trusted server runtimes. Search and Contents can be synchronous, while Agent, Monitors, Websets, and Batch require durable IDs and terminal-state reconciliation. Deployments must account for queues and scheduled resources that outlive a process release.

## Authentication

For normal REST work, inject `EXA_API_KEY` from an approved server-side secret manager and send it only as `Authorization: Bearer` to the configured first-party Exa API host. Team Management service keys, hosted MCP OAuth or enterprise managed authorization, and payment-protocol calls are separate trust models. Never print, commit, place in a URL, or expose a credential to an untrusted client.

## Instructions

1. Identify every runtime, queue, webhook, schedule, key, and Exa product in the release.
2. Inject environment-specific secrets and deny them to browser or preview builds.
3. Configure timeouts, endpoint budgets, queue bounds, and content-size limits.
4. Deploy dark, validate configuration, then enable a small synthetic canary.
5. Observe request IDs, error classes, latency, cost, and asynchronous backlog.
6. Rollback code and separately pause or reconcile monitors, batches, and runs.

## Tool Discipline

Use Read, Glob, and Grep to inspect repository code, configuration, fixtures, and evidence. Use Write and Edit only for approved implementation or documentation changes. Do not call Exa, run paid research, create or alter a Monitor, Webset, Agent run, Batch, team, member, API key, budget, webhook, or deployment merely because this skill was invoked.

## Approval Boundaries

Require an accountable owner before live queries involving sensitive intent, production credentials, spend or rate-limit changes, forced live crawling, generated summaries, external delivery, deployment, member or key changes, schedule creation, or destructive cancellation, stopping, deletion, or revocation. Read-only repository inspection and synthetic offline validation do not authorize live vendor actions.

## Failure Modes

- Rolling back code does not cancel vendor-side asynchronous work.
- Preview environments can leak production keys or create paid schedules.
- Autoscaling workers without a shared limiter can exceed team limits.

## Output

Return the operation scope, environment, team and product surface, authorization class, contract and policy decisions, deterministic validation results, content-free identifiers, status and cost counts, risks, cleanup or rollback state, and a concise pass or fail receipt. Exclude credentials, raw queries, prompts, presigned URLs, retrieved content, generated output, and customer-derived data unless separately approved.

## Example

- Deploy a disabled worker, validate secrets and egress, enable one-percent traffic, and pause Monitors before rollback.
- Finish with request or resource IDs, assertion counts, cost and terminal state, rollback or deletion status, and the decision owner; never reproduce secrets or retrieved content.

## Validation

Rerun the smallest relevant deterministic test, compare actual behavior with the requested outcome and current first-party contract, verify sensitive fields are absent from evidence, and confirm deadlines, terminal state, downstream retention, and rollback before reporting success.

## References

Review the dated first-party evidence map before relying on any endpoint, parameter, search type, price, limit, beta, compliance, identity, retry, or lifecycle claim.

- [Current first-party evidence map](references/official-docs.md)
