---
name: mistral-data-handling
description: >-
  Govern Mistral prompts, outputs, embeddings, files, OCR, audio, batch, stateful resources, and deletion evidence. Use when sensitive or retained data is involved. Trigger with "Mistral data retention", "upload a file to Mistral", or "review Mistral privacy".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<workload> <data-class> <retention-policy>"
version: 1.14.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, mistral, data-governance]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live or external Mistral actions require network access and explicit approval"
---
# Mistral Data Lifecycle Governance

## Overview

Map every data class through provider transit, app storage, derived artifacts, state, retention, and deletion. Never infer privacy from one endpoint or account feature.

## Prerequisites

- A data inventory, lawful purpose, tenant boundary, retention requirements, and privacy owner.
- Current endpoint/account evidence including ZDR applicability.
- Deletion, subject-request, incident, and derived-data policies.

## Current Contract

ZDR covers supported stateless paid-plan calls but excludes stateful products/APIs including Agents, Batch processing files, Conversations, Libraries, and `/v1/files`. Each workload needs review.

## Authentication

Authorize data independently of the provider key. Never put credentials or customer content in logs, receipts, or diagnostics.

## Instructions

1. Classify prompts, outputs, embeddings, files, transcripts, OCR, batch artifacts, state IDs, and derived records.
2. Map endpoint, account controls, transit, provider state, app stores, logs, backups, and subprocessors.
3. Verify ZDR for the exact stateless operation; mark excluded/unknown stateful surfaces.
4. Minimize/redact, isolate tenants, bound purpose/retention, and authorize before transmission.
5. Track resource IDs and derived artifacts for cross-system deletion reconciliation.
6. Test access, expiry, deletion, restore/backups, subject requests, and incident evidence.

## Tool Discipline

Use Read, Glob, and Grep to inspect code, locks, configuration, tests, and evidence. Use Write and Edit only for approved repository changes. Invocation alone does not authorize network calls, paid usage, uploads, stateful resources, admin mutations, deployments, or deletion.

## Approval Boundaries

Sensitive data, uploads, batch/stateful use, retention, region changes, training/fine-tuning, and deletion require privacy/security approval. Deprecated fine-tuning docs do not establish a current supported workflow.

## Error Handling

- App deletion does not prove provider or index deletion.
- Embeddings, OCR, and transcripts remain sensitive derived data.
- Assuming ZDR for stateful APIs contradicts current exclusions.

## Output

Return the data and endpoint map, purpose, ZDR evidence, stores and retention, deletion ledger, owners, risks, and receipts. Label exclusions and unknown provider state.

## Examples

- Track document upload through OCR, index, backup, and deletion.
- Reject fine-tuning upload until a current supported contract and approval exist.

## Validation

Trace records end to end, test tenant denial, retention, deletion, and restore behavior, and verify every ZDR assertion. Fail the review when any derived artifact lacks an owner.

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources before relying on mutable endpoints, models, limits, prices, preview status, or retention.
- Record live account observations as environment-specific evidence, not universal Mistral guarantees.
