---
name: stackblitz-sdk-patterns
description: >-
  Design a durable WebContainer lifecycle adapter for filesystem, process, event, preview, and teardown operations. Use when multiple UI components need WebContainer access or an integration has race-prone boot and cleanup logic. Trigger with "WebContainer SDK patterns", "manage WebContainer lifecycle", or "StackBlitz runtime adapter".
argument-hint: "[project-path] [runtime-module]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.7.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- stackblitz
- architecture
- webcontainers
model: inherit
effort: medium
compatibility: Designed for Claude Code
---
# WebContainer Lifecycle Adapter

## Overview

This skill creates or reviews one application-owned boundary around WebContainer startup and capabilities. The adapter makes boot idempotent, exposes explicit runtime states, tracks event unsubscriptions and processes, and prevents UI components from independently manipulating a shared instance.

## Prerequisites

- A named repository and the components that currently own runtime behavior
- The installed `@webcontainer/api` type definitions as the local API authority
- Expected mount, process, preview, export, and disposal use cases

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to map imports, boot calls, process ownership, filesystem mutations, event subscriptions, and teardown paths. Use `WebFetch` only for current official StackBlitz or WebContainers documentation. Use `Write` or `Edit` after proposing the adapter boundary and compatibility impact.

## Current Contract

- Cache the boot promise, not only the resolved instance, so concurrent callers cannot race into two boots.
- Model at least idle, booting, ready, failed, and disposed states; make invalid transitions visible.
- Retain the unsubscribe function returned by `on()` and the handles returned by `spawn()`.
- Treat filesystem writes and `export()` as explicit data operations with caller-owned paths and size bounds.
- `teardown()` invalidates the instance, processes, and filesystem; call it only at the permanent owner boundary.
- Prefer adding preview instrumentation in the served application; use `setPreviewScript` only after reviewing its advanced-feature warning and compatibility risk.

## Authentication

The adapter may accept already-resolved configuration but must not expose secret values through state, logs, errors, or browser storage. Initialize commercial keys and organization auth before adapter boot through the dedicated preflight layer.

## Workflow

1. Inventory every WebContainer import, boot call, event listener, process handle, filesystem writer, and teardown call.
2. Define the adapter's state machine and minimum methods from observed consumers.
3. Centralize a single boot promise and make failed startup recoverable only through an explicit reset or disposal policy.
4. Wrap spawn with exit, output-bound, cancellation, and ownership metadata.
5. Wrap subscriptions so each consumer can unsubscribe and the owner can perform final cleanup.
6. Add focused concurrency, failure, HMR, and teardown tests before migrating consumers incrementally.

## Approval Boundaries

Do not migrate all consumers, change persistent/export behavior, terminate active processes, or alter production preview instrumentation without explicit scope. Show the compatibility plan and rollback before replacing an existing runtime singleton.

## Output

Return the lifecycle inventory, proposed state machine and API, migrated call sites, concurrency and cleanup evidence, authentication boundary, compatibility risks, and rollback procedure.

## Error Handling

| Condition | Response |
|---|---|
| Concurrent callers race | Share one boot promise and test simultaneous acquisition. |
| Process output never closes | Apply cancellation and output bounds; retain the process handle. |
| A consumer tears down globally | Move teardown to the permanent owner and give consumers scoped unsubscribe methods. |
| Installed types differ from docs | Follow the pinned local types and record the planned version review. |

## Examples

Given three React components that each call `boot()`, replace them with one tested adapter whose cached promise owns the runtime while components receive scoped filesystem, process, and subscription capabilities.

## Resources

- [Official StackBlitz and WebContainers references](references/official-docs.md)
- [WebContainer API reference](https://webcontainers.io/api)
- [API versioning and support](https://webcontainers.io/guides/api-support)
