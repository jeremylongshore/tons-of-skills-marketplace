---
name: ideogram-hello-world
description: >-
  Generate and persist one bounded Ideogram V4 image through the current multipart endpoint. Use when testing a first server-side request or reviewing a minimal integration. Trigger with "first Ideogram image", "test Ideogram V4", or "build an Ideogram smoke test".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<prompt-class> <output-path> [environment]"
version: 1.11.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, ideogram, generation]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live generation requires network access, a key, and prepaid credit"
---
# First Ideogram V4 Generation

## Overview

Prove the smallest current Ideogram integration: one server-side multipart request, one checked response, and immediate persistence of any returned image. Keep the smoke test bounded because the call spends prepaid credit and response URLs expire.

## Prerequisites

- An approved `IDEOGRAM_API_KEY`, positive API credit, and a non-sensitive prompt.
- Server-side network access and durable storage outside the repository.
- A request deadline, maximum output count, and named spend owner.

## Current Contract

The synchronous V4 route is `POST /v1/ideogram-v4/generate` using `multipart/form-data`. Supply either `text_prompt` or `json_prompt`, never both. Structured JSON prompts disable magic prompt. A result can be present but unsafe, represented by `is_image_safe=false` and an empty URL.

## Authentication

Send `IDEOGRAM_API_KEY` only as the `Api-Key` header to `https://api.ideogram.ai`. Keep the request on a trusted server and never echo the key, prompt, response URL, or image bytes into logs or receipts.

## Instructions

1. Confirm the prompt classification, destination, output count, deadline, and approval for a paid live request.
2. Build a multipart body with exactly one prompt form, a supported aspect ratio, and an explicitly reviewed rendering option.
3. Send the request to the V4 synchronous route with the server-side API key and a bounded timeout.
4. Reject non-success status codes and validate the response schema before reading image fields.
5. Check `is_image_safe`; treat an unsafe item or empty URL as a policy outcome, not a downloadable success.
6. Download an approved image immediately, verify content type and byte limit, and store it under an application-owned opaque identifier.
7. Return content-free request, storage, timing, safety, and cleanup evidence.

## Tool Discipline

Use Read, Glob, and Grep to inspect the existing adapter, storage boundary, and fixtures. Use Write and Edit only for approved code, fixture, or documentation changes. Do not run a paid request merely because this skill was selected.

## Approval Boundaries

Require approval for live spend, sensitive prompts, customer images, external publication, or durable retention. The smoke test must not overwrite an existing asset; rollback removes only the newly created opaque object and associated test metadata.

## Error Handling

- `400` indicates an invalid combination or endpoint-specific option; V4 `FLASH` is currently not accepted.
- `401`, `422`, and `429` require authentication, validation, and capacity-specific handling.
- A successful HTTP response with `is_image_safe=false` must not be retried by mutating the prompt automatically.

## Output

Return endpoint, environment, prompt class, HTTP status, output and safe-item counts, opaque generation or request identifiers, durable storage key, latency, cost owner, and rollback status. Exclude raw prompts, credentials, image URLs, and image bytes.

## Examples

- Generate a synthetic square label design, persist it to a test bucket, then delete it after assertions.
- Report `endpoint=v4-sync; outputs=1; safe=1; persisted=yes; url_retained=no; cleanup=complete`.

## Validation

Re-run the adapter's deterministic fixture test, verify exactly one prompt form was sent, confirm the URL was not retained, and check storage and deletion receipts. Live output quality alone does not prove schema, safety, or retention correctness.

## Resources

- [Current first-party evidence map](references/official-docs.md)
