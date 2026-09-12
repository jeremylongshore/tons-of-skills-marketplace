---
name: ideogram-reference-architecture
description: >-
  Design an Ideogram service boundary with policy gateway, queue, async state, verified webhooks, polling, moderation, storage, and audit. Use when creating or reviewing a production architecture. Trigger with "architect Ideogram", "design an Ideogram service", or "review an Ideogram system diagram".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<workload> <tenant-model> <slo>"
version: 1.11.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, ideogram, architecture]
model: inherit
effort: high
compatibility: "Designed for Claude Code; architecture work is evidence-led and deployment-neutral"
---
# Ideogram Reference Architecture

## Overview

Define ownership and data flow for a production Ideogram integration. Keep user authorization, paid vendor authority, request validation, async state, event verification, content review, durable media, and audit evidence as explicit components.

## Prerequisites

- Workload, tenant and identity model, data class, SLO, budget, region, and retention policy.
- Expected endpoint mix, input sizes, concurrency, publication destinations, and failure modes.
- Owners for billing, security, moderation, storage, operations, and vendor escalation.

## Current Contract

The API uses server-side `Api-Key`, endpoint-specific multipart requests, sync and async generation, item-level safety, signed async webhooks, polling, and temporary asset URLs. Default capacity is 10 in-flight requests. These contracts require stateful application orchestration even when the product experience is synchronous.

## Authentication

Place `IDEOGRAM_API_KEY` only in a private vendor adapter. The policy gateway authenticates application identities and authorizes tenant, use case, spend, input, output, and destination separately.

## Instructions

1. Define ingress and policy gateway boundaries for identity, tenant, rights, media validation, safety, copyright settings, budget, and admission.
2. Route accepted work to a durable queue and an account-level concurrency controller.
3. Use a vendor adapter that owns endpoint schemas, multipart, deadlines, typed errors, and content-free telemetry.
4. Persist request and `generation_id` state before async delivery, then reconcile verified webhooks with polling.
5. Pass safe outputs through a downloader that validates media and stores opaque tenant-scoped objects immediately.
6. Publish only from the application object store after required review; never authorize from a vendor URL.
7. Add outbox, audit, deletion, incident, canary, and rollback paths with explicit owners.

## Tool Discipline

Use Read, Glob, and Grep to ground the design in the actual repository and infrastructure. Use Write and Edit for approved architecture records or implementation. Do not provision services, create keys, or deploy from a design invocation.

## Approval Boundaries

Require accountable review for trust-boundary changes, public ingress, data residency, sensitive media, external publication, retention, spend, and production topology. Record unresolved assumptions as blockers.

## Error Handling

- Keep queue acceptance distinct from vendor acceptance and durable asset completion.
- Reconcile duplicate or missing events without duplicate paid submissions.
- Quarantine unsafe, malformed, oversized, or tenant-mismatched media before publication.

## Output

Return components, flows, trust boundaries, state model, endpoint choices, SLO and capacity model, data lifecycle, controls, owners, failure paths, open decisions, and rollback architecture. Exclude secret or content examples.

## Examples

- Flow: application client -> policy gateway -> queue -> vendor adapter -> state store -> verified webhook or poller -> safe downloader -> object store -> reviewer -> publisher.
- Keep audit records content-free while placing regulated media in its approved retention boundary.

## Validation

Walk happy, unsafe, throttled, duplicate, missing-webhook, expired-URL, storage-failure, and rollback scenarios. Verify every state and retained datum has one owner and deletion path.

## Resources

- [Current first-party evidence map](references/official-docs.md) — use the dated endpoint, webhook, billing, team, and training links as the contract index for this workflow.
- Recheck the endpoint-specific page and current OpenAPI description before relying on an enum, limit, beta feature, or lifecycle claim.
- Record live observations as environment-specific evidence, not as universal vendor guarantees.
