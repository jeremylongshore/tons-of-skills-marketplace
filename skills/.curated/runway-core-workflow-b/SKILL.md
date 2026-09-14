---
name: runway-core-workflow-b
description: >-
  Prepare, submit, and preserve Runway image-to-video or video-to-video work with validated media provenance. Use when a generation begins from an asset. Trigger with: "Runway image to video", "Runway video transformation", "upload media to Runway".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[input-asset-and-intent]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - runway
  - image-to-video
  - video-to-video
  - media
compatibility: 'Requires server-side Runway Dev access, current first-party documentation, an approved credit budget, and controlled media storage.'
---

# Runway Input-Media Transformation Workflow

## Overview

Input media is part of the generation contract and the security boundary. Choose public HTTPS, data URI, or an ephemeral upload deliberately; verify rights, content, size, format, crop, expiry, and model compatibility before spending credits.

## Prerequisites

- An approved source asset with provenance and usage rights
- Current input constraints and exact model variant schema
- Temporary-upload and final-output retention policies

## Instructions

### Step 1: Classify the transformation

Choose image-to-video, video-to-video, upscale, or another documented endpoint from the desired input and output—not from a copied sample. Record the expected preservation and allowed creative change.

### Step 2: Validate the asset

Check MIME type, extension, byte size, dimensions, duration, codec, orientation, and moderation policy. Review auto-crop consequences when the source aspect ratio differs from the requested output.

### Step 3: Choose transport

Use a reachable HTTPS URL for already hosted media, a data URI only for small inputs, or an ephemeral upload for local files. Never embed large video as base64 merely because a sample does.

### Step 4: Create an ephemeral upload safely

For local media, use the SDK helper or the documented two-step upload. A `runway://` URI lasts 24 hours, supports reuse within that period, and must not be treated as permanent storage.

### Step 5: Submit and track

Validate the chosen model's input fields, persist the request fingerprint and task ID, then use bounded polling. Do not retry a failed upload URL; start a new upload as documented.

### Step 6: Validate transformed output

Copy successful output to owned storage and compare duration, dimensions, codec, visible crop, continuity, brand constraints, and safety. Preserve both source and output checksums in the receipt.

## Authentication

The Runway API secret remains server-side for uploads, generation, and task reads. Source URLs and temporary Runway/output URLs may grant access to media and must be redacted and expired according to policy.

## Tool Discipline

Use Read and Grep to inspect application configuration, provider documentation, lockfiles, fixtures, schemas, tests, and redacted operational evidence before proposing a change. Use Write or Edit only for an approved implementation, configuration, test, runbook, or redacted receipt. Do not create, cancel, delete, retry, deploy, rotate, revoke, publish, or otherwise mutate production Runway resources without explicit operator approval.

## Output

- Input provenance, validation, crop, and transport decision
- Upload and generation identifiers with state evidence
- Owned output with media, safety, and transformation review

Return the environment, organization alias, operation and task identifiers, API and SDK versions, model or router policy, source-contract fingerprint, task-state evidence, credit boundary, output disposition, unresolved risk, rollback state, and final decision without exposing API secrets, prompt or media contents, or temporary signed URLs.

## Examples

A private product still is 12 MB and would crop poorly to the target ratio. The worker records rights, pads the composition before upload, creates a 24-hour `runway://` URI, submits one compatible image-to-video task, and stores the result under the source checksum.

## Error Handling

| Failure | Response |
| --- | --- |
| Input is outside the selected model contract | Transform the asset through an approved preprocessing step or choose a compatible documented model; do not force the request. |
| Ephemeral upload fails | Start a fresh upload request rather than retrying the failed upload target. |
| Output crop removes required content | Reject the output and revise the approved composition or ratio before another billable attempt. |

## Validation

Test public URL, small data URI, and ephemeral-upload adapters with synthetic media; assert exact model constraints, expiry handling, and output copying. Include a visual review for crop and transformation requirements.

## Resources

- [First-party source notes](references/official-docs.md)
- [Runway agent context](https://docs.dev.runwayml.com/ai-context.md)
- [API reference](https://docs.dev.runwayml.com/api.md)
- [Models](https://docs.dev.runwayml.com/guides/models.md)
- [Usage tiers](https://docs.dev.runwayml.com/usage/tiers.md)
- [Pricing](https://docs.dev.runwayml.com/guides/pricing.md)
- [Production checklist](https://docs.dev.runwayml.com/guides/go-live.md)
