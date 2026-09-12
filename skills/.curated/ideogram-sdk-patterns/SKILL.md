---
name: ideogram-sdk-patterns
description: >-
  Design an owned Ideogram REST adapter for multipart uploads, typed responses, deadlines, and vendor isolation. Use when building or reviewing application client code without inventing an official SDK. Trigger with "wrap Ideogram API", "build an Ideogram client", or "review Ideogram adapter code".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<language> <adapter-path> <endpoint-family>"
version: 1.11.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, ideogram, architecture]
model: inherit
effort: high
compatibility: "Designed for Claude Code; examples are transport patterns, not claims of an official SDK"
---
# Ideogram REST Adapter Patterns

## Overview

Contain Ideogram transport behavior behind a small application-owned interface. Preserve endpoint-specific multipart contracts, error bodies, safety outcomes, asynchronous identifiers, and storage handoff without coupling business logic to raw vendor payloads.

## Prerequisites

- A target language, HTTP client, schema library, test runner, and adapter ownership boundary.
- Current OpenAPI plus endpoint documentation for the exact route.
- Defined deadlines, concurrency, retry, data handling, and compatibility policies.

## Current Contract

Ideogram exposes REST and an OpenAPI document. Endpoint payloads are not interchangeable: V4 generation uses multipart form fields, some operations include files, and asynchronous routes return a generation identifier for later reconciliation. Avoid presenting a third-party package or local wrapper as an official Ideogram SDK.

## Authentication

Inject `IDEOGRAM_API_KEY` only inside the trusted transport adapter and send it as `Api-Key` to `https://api.ideogram.ai`. Redact headers, multipart content, prompts, image inputs, response URLs, and binary bodies from logs and exceptions.

## Instructions

1. Inventory only the endpoint families required by the application and pin their current schemas.
2. Define owned request types that make mutually exclusive fields such as `text_prompt` and `json_prompt` impossible to combine.
3. Centralize host, authentication, deadlines, response byte limits, error decoding, and content-type checks.
4. Preserve vendor status, request or generation identifiers, `is_image_safe`, and unknown fields needed for drift review.
5. Separate submission, polling, webhook reconciliation, asset download, and durable storage interfaces.
6. Retry only classified transient failures with bounded jitter and an operation deadline; never replay ambiguous writes blindly.
7. Validate with synthetic fixtures and one approved live smoke after schema or endpoint changes.

## Tool Discipline

Use Read, Glob, and Grep to identify existing clients and call sites. Use Write and Edit only for approved adapter, type, test, or documentation changes. Selection does not authorize package installation, live spend, or replacement of a production client.

## Approval Boundaries

Require review before adding dependencies, changing retry semantics, exposing new prompt or image fields, switching endpoints, enabling paid traffic, or altering durable storage. Keep vendor migration and application API compatibility decisions explicit.

## Error Handling

- Return typed authentication, validation, throttling, capacity, unsafe-output, timeout, and unknown-vendor errors.
- Preserve enough sanitized response detail to diagnose `400` and `422` without copying sensitive content.
- Fail closed on unexpected content type, oversized download, unsafe output, or unrecognized terminal state.

## Output

Return the adapter surface, endpoint map, schema version or retrieval date, retry and deadline policy, tests run, compatibility risks, live-check status, and rollback plan. Do not return credentials, prompts, image bytes, or expiring URLs.

## Examples

- Expose `generateV4`, `submitV4`, `getGeneration`, and `persistAsset` as separate owned operations.
- Adapt a vendor `429` into an application `CapacityDeferred` result carrying sanitized retry metadata.

## Validation

Run contract and call-site tests, compare multipart field names to first-party docs, inject every error class, and verify logs remain content-free. Confirm the old adapter can be restored without losing in-flight generation state.

## Resources

- [Current first-party evidence map](references/official-docs.md)
