---
name: adobe-data-handling
description: >-
  Analyze and enforce classification, minimization, signed-URL custody, retention, deletion, content provenance, and privacy-request boundaries for Adobe workflows. Use when the task requires adobe data custody and privacy review. Trigger with "Adobe data handling", "PDF privacy", or "Firefly content policy".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<workflow> <data-classes> <jurisdictions>"
version: 1.8.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, adobe, data-governance]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Adobe actions require network access, appropriate entitlement and authentication, and explicit approval"
---
# Adobe Data Custody and Privacy Review

## Overview

Analyze and enforce classification, minimization, signed-URL custody, retention, deletion, content provenance, and privacy-request boundaries for Adobe workflows. This workflow produces a reviewable artifact and evidence before any live side effect.

## Prerequisites

- Current first-party Adobe documentation for every selected service, API version, auth flow, limit, and lifecycle.
- Named product, identity, security, data, budget, release, and operations owners appropriate to the scope.
- Synthetic or approved non-production fixtures with secret and content canaries.

## Current Contract

Adobe services have distinct custody contracts. PDF Services can use supported customer-storage signed URLs and can delete Adobe-hosted assets through the Assets endpoint. Firefly inputs/outputs and Content Credentials require product-specific review. Privacy Service is a separate Experience Platform API with its own authorization contract. Recheck the dated evidence map before relying on mutable product behavior.

## Authentication

Treat tokens and signed URLs as secrets and prompts, images, PDFs, extracted text, event bodies, and identifiers as classified content. Do not send data to a service merely because auth succeeds.

## Instructions

1. Map every input, derived field, prompt, artifact, event, log, storage hop, recipient, jurisdiction, purpose, and owner.
2. Minimize fields/content and select customer-managed storage or Adobe assets from current service/security evidence.
3. Set signed-URL scope/expiry, encryption, access, provenance, retention, deletion, and legal-hold controls.
4. Validate content-policy and Content Credentials behavior from live product outcomes without inventing regex screening guarantees.
5. Separate ordinary application deletion from regulated Privacy Service requests and identify responsible controllers/processors.
6. Test redaction, access, expiry, deletion, legal hold, provenance preservation, and incident escalation.

## Tool Discipline

Use Read, Glob, and Grep to inspect current documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Skill invocation alone does not authorize network access, credentials, Adobe content, consent, uploads, generation, spend, deployment, registration changes, replay, cancellation, or deletion.

## Approval Boundaries

Data, privacy, security, and product owners approve processing and destinations. Upload, external transfer, retention change, Privacy Service submission, or deletion requires explicit authority.

## Error Handling

- Do not publish universal 24-hour retention claims across Adobe products.
- Do not pre-screen prompts with unsupported claims that override Adobe's actual decision.
- Do not expose signed URLs in logs, tickets, or analytics.

## Output

Return the data-flow register, classifications, lawful purpose/owner, custody decisions, retention/deletion schedule, tests, and gaps. Mark assumptions, observed environment behavior, owners, evidence dates, and unresolved gaps explicitly.

## Examples

- Delete a synthetic PDF asset and verify access fails.
- Prove a signed URL is redacted from every telemetry sink.

## Validation

Exercise and record expected and observed results for:

- PII
- regulated document
- signed URL
- policy rejection
- legal hold
- deletion

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated Adobe sources before execution.
- Treat observed tenant or product behavior as environment-specific evidence, never a universal Adobe guarantee.
