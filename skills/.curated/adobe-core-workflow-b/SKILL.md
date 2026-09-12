---
name: adobe-core-workflow-b
description: >-
  Execute an Adobe PDF Services operation through explicit asset custody, asynchronous status, output verification, and cleanup. Use for approved document conversion, extraction, or generation. Use when this Adobe operator workflow is needed. Trigger with "process PDF with Adobe", "PDF Services job", or "Adobe document automation".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<operation> <input-classification> <output-destination>"
version: 1.8.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, adobe, pdf]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Adobe actions require network access, appropriate entitlement and authentication, and explicit approval"
---
# PDF Services Controlled Document Job

## Overview

Execute an Adobe PDF Services operation through explicit asset custody, asynchronous status, output verification, and cleanup.. This workflow produces a reviewable artifact and evidence before any live side effect.

## Prerequisites

- Current first-party Adobe documentation for every selected service, API version, auth flow, limit, and lifecycle.
- Named product, identity, security, data, budget, release, and operations owners appropriate to the scope.
- Synthetic or approved non-production fixtures with secret and content canaries.

## Current Contract

The REST lifecycle is authenticate, supply a supported signed URL or create an asset and upload to its pre-signed URI, create an async job, follow the Location/status contract, retrieve output, and delete Adobe-hosted assets when no longer needed. Limits vary by operation. Recheck the dated evidence map before relying on mutable product behavior.

## Authentication

Use server-side service credentials and bind assets to the same credential or approved signed URL. Signed URLs are bearer capabilities and must be redacted, narrowly scoped, and short-lived.

## Instructions

1. Classify the input, operation, page/file constraints, output, retention, transaction budget, and owners.
2. Choose customer-managed signed URLs or Adobe-hosted assets and document the custody boundary.
3. Validate media type, size, protection state, operation contract, and current limits before upload.
4. Create the job once, retain the returned status location, and poll within an attempt and elapsed-time budget.
5. Download or receive output into approved storage, verify type/hash/expected structure, and acknowledge downstream custody.
6. Delete approved Adobe-hosted assets promptly and reconcile transaction, failure, retention, and deletion evidence.

## Tool Discipline

Use Read, Glob, and Grep to inspect current documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Skill invocation alone does not authorize network access, credentials, Adobe content, consent, uploads, generation, spend, deployment, registration changes, replay, cancellation, or deletion.

## Approval Boundaries

Require data-owner and budget approval before upload or job creation. Decryption, external transfer, output retention, and asset deletion require explicit authorized owners.

## Error Handling

- Do not retry a disqualified or malformed document unchanged.
- Do not log input/output content, credentials, or signed URLs.
- Treat an ambiguous job result as reconciliation work, not permission to duplicate a transaction.

## Output

Return classification, storage decision, asset/job ledger, status evidence, verified output, transaction class, deletion receipt, and residual retention. Mark assumptions, observed environment behavior, owners, evidence dates, and unresolved gaps explicitly.

## Examples

- Process a synthetic PDF and delete its Adobe-hosted assets.
- Reject an unsupported or protected fixture before upload.

## Validation

Exercise and record expected and observed results for:

- valid output
- unsupported input
- expired URL
- 429
- ambiguous job
- deletion verification

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated Adobe sources before execution.
- Treat observed tenant or product behavior as environment-specific evidence, never a universal Adobe guarantee.
