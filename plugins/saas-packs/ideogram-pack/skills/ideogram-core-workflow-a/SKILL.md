---
name: ideogram-core-workflow-a
description: >-
  Select and operate the current Ideogram generation route across V4 sync, V4 async, transparency, and P-Image. Use when designing a text-to-image workflow with explicit latency and output contracts. Trigger with "generate with Ideogram V4", "choose an Ideogram model route", or "build transparent Ideogram images".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<use-case> <latency-class> <output-contract>"
version: 1.11.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, ideogram, generation]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live image generation consumes prepaid credit"
---
# Ideogram Generation Route Selection

## Overview

Choose the smallest current generation surface that satisfies latency, transparency, prompt, and model requirements. Make route choice explicit so applications do not inherit stale legacy endpoints or accidentally treat synchronous and asynchronous lifecycles as equivalent.

## Prerequisites

- An approved use case, prompt and input classification, latency target, output count, and cost ceiling.
- A server-side key, positive credit, durable storage, and content-review policy.
- Current endpoint-specific documentation; generic examples do not override route contracts.

## Current Contract

Ideogram documents V4 synchronous `/v1/ideogram-v4/generate`, V4 asynchronous `/v1/ideogram-v4/async/generate`, transparent variants, and P-Image sync/async routes. V4 accepts either text or structured JSON prompting; JSON prompting disables magic prompt. V4 `FLASH` currently returns `400`.

## Authentication

Send the server-side `IDEOGRAM_API_KEY` only through the `Api-Key` header to `https://api.ideogram.ai`. Never expose the key or direct paid-generation authority to a browser or untrusted tenant.

## Instructions

1. Classify whether the workload requires V4, transparency, P-Image, structured prompting, or compatibility with an existing V3 flow.
2. Choose synchronous handling only when the request deadline safely includes generation and immediate download; otherwise choose async.
3. Build the exact endpoint-specific multipart payload and reject mutually exclusive or unsupported fields before sending.
4. Bound output count, input size, rendering option, in-flight concurrency, and total operation deadline.
5. Validate safety on every returned image and persist approved assets immediately because vendor URLs expire.
6. For async work, persist `generation_id`, reconcile webhook and polling results idempotently, and close only on a recognized terminal state.
7. Record route, policy, spend, safety, storage, and cleanup evidence without retaining content.

## Tool Discipline

Use Read, Glob, and Grep to inspect product requirements, adapters, and fixtures. Use Write and Edit for approved implementation or documentation changes. Do not perform live generation, upload customer content, or alter production traffic by invocation alone.

## Approval Boundaries

Require approval for paid calls, sensitive prompts or images, external publication, model or rendering changes, copyright-detection policy changes, and production rollout. A route migration needs a canary and reversible traffic control.

## Error Handling

- Reject V4 `FLASH` until endpoint documentation states support.
- Treat `400`, `401`, `422`, and `429` by class; do not retry validation or authentication failures.
- Treat `is_image_safe=false` and an empty URL as a completed policy outcome, not transport failure.

## Output

Return selected route, sync or async mode, prompt form, bounds, status counts, safe and unsafe counts, opaque generation IDs, persistence result, latency, spend owner, and rollback state. Exclude credentials, prompts, images, and temporary URLs.

## Examples

- Route an interactive opaque-image request to V4 sync and a batch campaign to V4 async.
- Route a background-free catalog asset to the transparent endpoint only after storage and moderation are ready.

## Validation

Compare route and multipart fields with current first-party docs, run fixture coverage for every terminal outcome, verify URL persistence and removal, and confirm concurrency plus deadline limits. Test the traffic rollback before enabling the canary.

## Resources

- [Current first-party evidence map](references/official-docs.md) — use the dated endpoint, webhook, billing, team, and training links as the contract index for this workflow.
- Recheck the endpoint-specific page and current OpenAPI description before relying on an enum, limit, beta feature, or lifecycle claim.
- Record live observations as environment-specific evidence, not as universal vendor guarantees.
