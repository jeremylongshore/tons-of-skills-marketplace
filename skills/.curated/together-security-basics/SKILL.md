---
name: together-security-basics
description: >-
  Secure Together AI integrations with project-scoped keys, environment isolation, prompt/output data controls, bounded model behavior, safe logging, rotation, and incident response. Use when threat-modeling or hardening Together usage. Trigger with "Together security", "protect Together API key", or "Together data controls".
argument-hint: "[repository-path] [environment] [data-classification]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- together-ai
- security
model: inherit
effort: high
compatibility: Designed for Claude Code; verification may require secret-store and Together AI project access
---
# Together AI Security Basics

## Overview

This skill maps credentials, data, model output, tool use, logs, and paid asynchronous actions to explicit controls and owners.

## Prerequisites

- Data classification and approved Together use cases
- Project/environment inventory and credential owners
- Request/response logging, retention, and deletion policy
- Model-output validation and any downstream tool-execution boundary

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to find provider calls, secrets, logging, persistence, and model-output consumers. Use `WebFetch` for current Together authentication and API behavior. Use `Write` or `Edit` only for approved controls; never read or reproduce secret values.

## Current Contract

- Together keys are project-scoped; create separate development, CI, and production credentials.
- Keep keys server-side and out of source, browser bundles, prompts, logs, fixtures, and fork workflows.
- Treat prompts, uploaded files, outputs, model IDs, and job artifacts according to their data classification.
- Model output is untrusted input to downstream systems; validate structure and require authorization for side effects.

## Authentication

Inject `TOGETHER_API_KEY` from an approved secret store and send it only as the SDK credential or Bearer header over HTTPS. Define rotation, revocation, leak detection, owner removal, and emergency shutdown procedures.

## Instructions

1. Inventory keys, projects, callers, endpoints, data classes, storage, and downstream actions.
2. Remove tracked or client-side credentials and separate secrets by environment and workload.
3. Minimize prompt/upload content, redact diagnostics, and enforce retention/deletion policy.
4. Validate structured output and isolate any tool execution behind independent authorization.
5. Bound tokens, concurrency, retries, batch/fine-tune submissions, and dedicated provisioning.
6. Test credential revocation, provider failure, prompt injection, unsafe output, and incident response.

## Approval Boundaries

Do not upload sensitive datasets, enable model-driven side effects, broaden key sharing, or retain prompts/outputs beyond policy without the named data and security authorities.

## Output

Return trust boundaries, key/project map, data-flow controls, output-validation rules, cost/side-effect bounds, test evidence, gaps, owners, and remediation deadlines.

## Error Handling

| Condition | Response |
|---|---|
| Credential is exposed | Revoke or rotate immediately and scrub retained artifacts. |
| Data classification unknown | Stop before sending or uploading content. |
| Output fails validation | Reject it; do not coerce unsafe content into an action. |
| Provider access is abused | Disable the affected key/project path and preserve audit evidence. |

## Examples

The example below shows the minimum redacted evidence expected from a successful invocation of this operator workflow.

```text
keys=per-environment; prompts=minimized; outputs=untrusted-validated; side-effects=separately-authorized
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Authentication](https://docs.together.ai/docs/api-keys-authentication)
- [Chat API](https://docs.together.ai/reference/chat-completions)
- [Error codes](https://docs.together.ai/docs/error-codes)
