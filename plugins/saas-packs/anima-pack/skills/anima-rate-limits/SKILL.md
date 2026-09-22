---
name: anima-rate-limits
description: 'Implement rate limiting for Anima API code generation requests.

  Use when batching component generation, handling rate limit errors,

  or optimizing API throughput for large design systems.

  Trigger with: "anima rate limit", "anima throttling", "anima batch generation".

  '
allowed-tools: Read, Write, Edit, Bash(npm:*)
version: 2.0.0
argument-hint: "[figma-workload]"
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- design
- figma
- anima
- rate-limiting
compatibility: Requires Node.js 20+, approved Anima API access, current Anima SDK documentation, and authorized Figma or website source access
---
# Anima Rate Limits

## Overview

Handle Figma rate limits from the current SDK's structured callback and treat any
Anima generation quota as account-specific until the provider or agreement says
otherwise. Never encode an invented requests-per-minute or concurrency allowance.

## Documented Signals

| Surface | Signal | Required action |
|---------|--------|-----------------|
| `FigmaRestApi.onRateLimited` | `retryAfter`, `figmaPlanTier`, `figmaRateLimitType` | Retry only inside a bounded elapsed-time budget |
| `figmaRateLimitMaxWait` | 1–180 seconds; default 60 | Set explicitly for the request's latency budget |
| Anima generation | Returned error/progress state and account contract | Stop or queue; do not infer a numeric quota |

## Prerequisites

- Confirm the account's current generation and concurrency contract before choosing worker concurrency; absence of a published number means fail closed, not guess.
- Store `ANIMA_TOKEN`, `FIGMA_TOKEN`, and `FIGMA_FILE_KEY` in the runtime secret manager or injected environment, and verify that the token has only the scopes required for the selected file. Never put tokens in source, fixtures, logs, generated receipts, or retry payloads.
- Define an explicit allowlist of Figma files and node IDs, a bounded batch size, a maximum retry budget, and an approved output directory. Use synthetic or sandbox designs for load tests and confirm that generated output contains no customer data before persisting it.
- Install the pinned SDK and decide whether a generation is safe to repeat. Persist a redacted request fingerprint and resume only failed node IDs.

## Instructions

### Step 1: Configure Structured Figma Rate Handling

```typescript
// src/anima/client.ts
import { Anima, FigmaRestApi } from '@animaapp/anima-sdk';

const figmaRestApi = new FigmaRestApi({
  defaultOptions: {
    token: process.env.FIGMA_TOKEN!,
    onRateLimited: async ({ retryAfter, figmaPlanTier, figmaRateLimitType }) => {
      console.warn({ retryAfter, figmaPlanTier, figmaRateLimitType });
      return retryAfter > 0 && retryAfter <= 5; // Repository latency budget.
    },
  },
});

export const anima = new Anima({
  auth: { token: process.env.ANIMA_TOKEN! },
  figmaRestApi,
});
```

### Step 2: Bind Each Generation to a Maximum Wait

```typescript
const result = await anima.generateCode({
  fileKey: process.env.FIGMA_FILE_KEY!,
  nodesId: ['1:2'],
  figmaRateLimitMaxWait: 5,
  settings: { framework: 'react', language: 'typescript', styling: 'tailwind' },
});
console.log({ fileCount: Object.keys(result.files).length, sessionId: result.sessionId });
```

## Error Handling

- Let `FigmaRestApi` own Figma retry decisions. Do not add a second uncoordinated retry loop around the same request.
- Do not retry 401/403 authentication or permission failures, invalid node/file parameters, or policy rejections. Stop the batch, report the node ID and redacted status, and repair credentials or scope before resuming.
- Retry only bounded transient 5xx and network failures. Cap attempts and total elapsed time, cancel queued work after the budget is exhausted, and preserve the successful results separately from failed node IDs so a resume cannot regenerate the whole batch accidentally.
- Treat timeout, process restart, and partial writes as ambiguous outcomes: check the request fingerprint or cache before resubmitting, write output atomically, and quarantine incomplete files. Logs and receipts may contain counts, status classes, and hashes, but not tokens, design contents, user identifiers, or generated source.
- Alert when the observed rate, queue depth, quota remaining, or failure ratio crosses the configured threshold. A human must approve any change to concurrency or quota settings; rollback means restoring the last known-good limiter configuration and draining queued work.

## Examples

For a sandbox batch, keep the work bounded and make the outcome auditable without exposing design data:

```typescript
const nodeIds = ['synthetic-card', 'synthetic-button'];
const receipt = {
  batchId: 'sandbox-2026-01-15-a',
  requested: nodeIds.length,
  succeeded: 0,
  failed: 0,
  contactsExported: 0,
};

for (const nodeId of nodeIds) {
  try {
    await anima.generateCode({ fileKey: process.env.FIGMA_FILE_KEY!, nodesId: [nodeId], figmaRateLimitMaxWait: 5, settings });
    receipt.succeeded++;
  } catch (error) {
    receipt.failed++;
    // Store only a redacted status and node fingerprint; never serialize `error` or source.
  }
}
console.log(JSON.stringify({ ...receipt, tokenPresent: Boolean(process.env.ANIMA_TOKEN) }));
```

An acceptable completion receipt is `requested=2; succeeded=2; failed=0; contacts_exported=0` with the sandbox ID and limiter settings recorded separately. A production batch should use the same controls, a reviewed allowlist, and an owner-approved change record before increasing concurrency.

## Tool Discipline

Use Read and Grep to inspect the existing integration and generated diff before changing anything. Use Write or Edit only inside the approved generated-code, test, or configuration paths. Use the declared Bash commands only for the explicit install, validation, or diagnostic steps in this workflow; never print tokens, source designs, generated source, or private website captures.

## Output

- Bottleneck-throttled code generation matching API limits
- Batch generator for design system-scale operations
- 429 retry handler with progressive backoff

## Resources

- [Anima API Docs](https://docs.animaapp.com/docs/anima-api)
- [Bottleneck npm](https://www.npmjs.com/package/bottleneck)
