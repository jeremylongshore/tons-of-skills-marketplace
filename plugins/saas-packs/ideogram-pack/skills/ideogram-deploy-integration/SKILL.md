---
name: ideogram-deploy-integration
description: >-
  Deploy an Ideogram server boundary with queues, storage, safety enforcement, observability, canaries, and rollback. Use when shipping a new runtime or changing production topology. Trigger with "deploy Ideogram", "ship an Ideogram worker", or "review Ideogram production architecture".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<platform> <release-sha> <environment>"
version: 1.11.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, ideogram, deployment]
model: inherit
effort: high
compatibility: "Designed for Claude Code; deployment and live generation require explicit approval"
---
# Ideogram Deployment Boundary

## Overview

Deploy Ideogram behind an application-owned server, queue, safety policy, and durable object store. Match runtime deadlines to sync or async behavior, keep paid authority out of clients, and preserve a reversible traffic path.

## Prerequisites

- Frozen release SHA, platform owner, environment, traffic slice, SLO, and rollback target.
- Secret manager, queue or concurrency control, object storage, monitoring, and incident response.
- Positive credit, billing owner, approved synthetic canary, and retention policy.

## Current Contract

Ideogram calls use `https://api.ideogram.ai`; default capacity is 10 in-flight requests. Async routes return `generation_id` and support webhook delivery with polling fallback. Image URLs expire, so deployment must download validated outputs into application storage before acknowledging durable completion.

## Authentication

Inject `IDEOGRAM_API_KEY` into the server or worker identity and send it only as `Api-Key`. A public browser receives application-scoped authorization, never the vendor credential or direct vendor URL.

## Instructions

1. Map request ingress, tenant auth, validation, queue, Ideogram route, webhook, polling, download, safety, storage, and publishing boundaries.
2. Choose sync only when platform and request deadlines safely cover generation plus download; otherwise persist async state.
3. Configure account-level concurrency below verified capacity, bounded queues, retry deadlines, and graceful drain.
4. Inject secrets by runtime reference, restrict egress to the approved host, and prevent request or response body logging.
5. Validate safety and media type before writing an opaque tenant-scoped object; discard temporary URLs.
6. Deploy a synthetic canary, compare status, latency, storage, safety, and cost signals, then increase traffic gradually.
7. Roll back traffic and reconcile in-flight generations and objects before terminating the prior version.

## Tool Discipline

Use Read, Glob, and Grep for manifests, infrastructure, adapters, and evidence. Use Write and Edit only for approved deployment changes. Invocation does not authorize a deploy, secret mutation, credit purchase, traffic shift, or destructive cleanup.

## Approval Boundaries

Require explicit approval for production secret access, new egress, live spend, policy changes, storage retention, traffic shifting, and rollback. Preserve the previous deployable artifact until in-flight work is reconciled.

## Error Handling

- Stop rollout on secret exposure, rising `429`, lost async state, unsafe-publication paths, or storage failure.
- Do not declare success while assets exist only at expiring vendor URLs.
- Drain or cancel local queue work before rollback; reconcile accepted vendor work idempotently.

## Output

Return release SHA, platform, topology, secret reference, concurrency and deadline settings, canary metrics, storage and safety results, traffic state, costs, and rollback receipt. Exclude credentials and content.

## Examples

- Deploy a queue-backed worker for async V4 and a verified webhook receiver with polling reconciliation.
- Keep the old worker at zero new traffic until all known generation IDs reach terminal state.

## Validation

Verify deployed digest, secret provenance, egress, queue bounds, signature checks, polling fallback, storage deletion, dashboards, and rollback. Confirm the canary object and temporary metadata are removed.

## Resources

- [Current first-party evidence map](references/official-docs.md)
