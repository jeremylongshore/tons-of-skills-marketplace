---
name: ideogram-local-dev-loop
description: >-
  Build a fixture-first local loop for Ideogram multipart requests, async states, safety outcomes, and expiring assets. Use when developing or testing without uncontrolled API spend. Trigger with "mock Ideogram locally", "test Ideogram fixtures", or "debug an Ideogram adapter".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<adapter-path> <test-command> [live-smoke-flag]"
version: 1.11.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, ideogram, testing]
model: inherit
effort: high
compatibility: "Designed for Claude Code; deterministic local tests require no vendor credentials"
---
# Ideogram Fixture-First Development Loop

## Overview

Develop the Ideogram boundary against owned request and response contracts before spending credit. Model multipart fields, asynchronous lifecycle states, unsafe outputs, transient errors, and expiring URLs as fixtures so the fast loop remains deterministic and privacy-safe.

## Prerequisites

- The repository's adapter seam, test runner, fixture policy, and data classification.
- Sanitized synthetic examples for success, unsafe output, validation failure, throttling, and terminal failure.
- An opt-in live-smoke flag that is disabled by default and on untrusted forks.

## Current Contract

Current generation surfaces include V4 synchronous and asynchronous routes, transparent variants, P-Image, and V3 compatibility routes. Async work returns a `generation_id`; status is reconciled by appending that returned value to `GET /v1/generations/` or by receiving a webhook. Returned asset URLs are temporary.

## Authentication

Fixtures must not contain credentials. When a separately approved live lane runs, inject `IDEOGRAM_API_KEY` server-side and send it only in the `Api-Key` header to the configured first-party host.

## Instructions

1. Read the adapter and enumerate request fields, response variants, error classes, and storage side effects.
2. Create sanitized fixtures for sync success, async submission, in-progress polling, safe and unsafe completion, `400`, `401`, `422`, `429`, and `503`.
3. Test multipart construction by field name and file metadata without snapshotting secrets or customer content.
4. Verify idempotent status reconciliation, duplicate webhook handling, bounded polling, URL download, and durable object persistence.
5. Keep the paid live smoke behind an explicit environment flag, trusted context, credit ceiling, and synthetic prompt.
6. Compare live response shape to fixtures, update only reviewed schema drift, and record cleanup.

## Tool Discipline

Use Read, Glob, and Grep to locate adapters, fixtures, and test commands. Use Write and Edit for approved test and adapter changes. Do not infer permission to call Ideogram, upload an image, spend credit, or retain generated media.

## Approval Boundaries

Offline fixture work is safe by default. Require approval before any live request, use of production credentials, customer-derived input, shared bucket write, fixture refresh from real responses, or deployment.

## Error Handling

- Reject fixtures containing key-like values, raw customer prompts, image bytes, or live URLs.
- Keep retry tests deterministic by injecting clocks and jitter rather than sleeping.
- Treat unrecognized response fields as explicit drift evidence; do not silently discard safety or billing signals.

## Output

Return adapter path, fixture inventory, assertion counts, deterministic command and result, live-lane status, detected contract drift, sensitive-data scan result, and cleanup state. Exclude prompts, images, credentials, and expiring URLs.

## Examples

- Test that `is_image_safe=false` produces no download attempt and a reviewable policy result.
- Test async transitions `submitted -> processing -> terminal` with duplicate delivery and polling fallback.

## Validation

Run the narrowest test command twice, confirm identical results, scan fixtures for secrets and URLs, and ensure the live lane remains disabled on forks. Verify temporary files and objects are removed after the test.

## Resources

- [Current first-party evidence map](references/official-docs.md) — use the dated endpoint, webhook, billing, team, and training links as the contract index for this workflow.
- Recheck the endpoint-specific page and current OpenAPI description before relying on an enum, limit, beta feature, or lifecycle claim.
- Record live observations as environment-specific evidence, not as universal vendor guarantees.
