---
name: ideogram-data-handling
description: >-
  Govern Ideogram prompts, uploads, structured descriptions, generated assets, temporary URLs, metadata, and training datasets through deletion. Use when designing privacy or retention controls. Trigger with "map Ideogram data", "set Ideogram retention", or "audit Ideogram image storage".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<data-class> <use-case> <retention-policy>"
version: 1.11.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, ideogram, data-governance]
model: inherit
effort: high
compatibility: "Designed for Claude Code; customer-derived media requires explicit authority"
---
# Ideogram Data Lifecycle

## Overview

Map and enforce the lifecycle of every datum that crosses an Ideogram workflow. Distinguish prompts, JSON descriptions, source media, masks, generated outputs, temporary links, safety decisions, metadata, logs, and custom-training assets because each has different ownership and retention needs.

## Prerequisites

- Use case, data owner, tenant, classification, rights basis, region, retention, and deletion SLO.
- Architecture for upload, API, async state, webhook, polling, download, storage, review, publication, backup, and telemetry.
- Vendor terms and privacy review appropriate to the workload.

## Current Contract

V4 describe can transform an uploaded image into a structured `json_prompt`; its bounding boxes use normalized `[0,1000]` coordinates in `[y_min,x_min,y_max,x_max]` order. Output URLs expire. Custom training supports datasets of 10–100 images, optional captions or ZIP upload, model training, and model-status retrieval.

## Authentication

Keep `IDEOGRAM_API_KEY` outside data stores and send it only as `Api-Key` from a trusted server. Application authorization must bind every input, generated object, dataset, and trained-model reference to its tenant and purpose.

## Instructions

1. Inventory each data class, source, purpose, rights basis, vendor transmission, destination, readers, retention, and deletion path.
2. Minimize prompts and metadata, validate image type and size, strip unnecessary metadata, and isolate temporary files.
3. Store async identifiers and safety decisions without copying content into queues, logs, traces, or incident evidence.
4. Download approved output promptly, validate it, store under an opaque tenant-scoped key, and discard the vendor URL.
5. Apply separate governance to describe output, captions, datasets, ZIPs, custom model references, backups, and derived assets.
6. Enforce access, encryption, publication review, lifecycle deletion, legal holds, and tenant export.
7. Test deletion across primary storage, metadata, queue, cache, backup policy, and custom-training records.

## Tool Discipline

Use Read, Glob, and Grep to inspect schemas, stores, policies, and fixtures. Use Write and Edit for approved lifecycle controls or documentation. Do not open, copy, upload, publish, or delete customer media without authority.

## Approval Boundaries

Require data-owner approval for sensitive inputs, training, new purposes, longer retention, external publication, cross-region movement, backup exceptions, and destructive deletion. Rights uncertainty is a stop condition.

## Error Handling

- Never treat an expiring URL as durable storage or an authorization token.
- Quarantine tenant-mismatched, malformed, oversized, or unexpectedly content-bearing records.
- Preserve legal holds while reporting why normal deletion could not complete.

## Output

Return the data map, classifications, rights and purpose decisions, stores, access paths, retention and deletion controls, tests, gaps, owners, and rollback. Exclude actual prompts, images, URLs, or credentials.

## Examples

- Retain an opaque generation ID and safety result for audit while deleting the source upload and vendor URL metadata.
- Govern a training dataset, captions, trained-model reference, and derived outputs as linked but separately deletable records.

## Validation

Trace one synthetic record through every system, verify least privilege and content-free telemetry, execute deletion, and confirm all governed locations. Reconcile any retained backup or legal-hold exception.

## Resources

- [Current first-party evidence map](references/official-docs.md) — use the dated endpoint, webhook, billing, team, and training links as the contract index for this workflow.
- Recheck the endpoint-specific page and current OpenAPI description before relying on an enum, limit, beta feature, or lifecycle claim.
- Record live observations as environment-specific evidence, not as universal vendor guarantees.
