---
name: stackblitz-hello-world
description: >-
  Build a minimal, controlled WebContainer smoke test that boots once, mounts a small project, observes process exit, and captures the preview URL. Use when proving browser/runtime compatibility before building a larger in-browser development experience. Trigger with "StackBlitz hello world", "test WebContainers", or "run Node in the browser".
argument-hint: "[project-path] [entrypoint]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- stackblitz
- webcontainers
- quickstart
model: inherit
effort: medium
compatibility: Designed for Claude Code
---
# WebContainer Controlled Smoke Test

## Overview

This skill adds or plans the smallest useful WebContainer proof: one instance, one deterministic file tree, one bounded dependency install, one server process, and one preview readiness observation. It avoids presenting a tutorial snippet as a production architecture.

## Prerequisites

- A browser application already passing the StackBlitz integration preflight
- Cross-origin isolation and HTTPS behavior verified for the target environment
- A small synthetic project that contains no proprietary source or secrets

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to establish the application entrypoint, package versions, and existing lifecycle ownership. Use `WebFetch` only for current official StackBlitz or WebContainers documentation. Use `Write` or `Edit` for a user-requested smoke-test implementation after inspection.

## Current Contract

- `WebContainer.boot()` is expensive and permits only one concurrent instance; centralize ownership.
- `mount()` accepts a `FileSystemTree` or supported binary snapshot and copies it into the virtual filesystem.
- Check a spawned install process through its `exit` promise before starting the server.
- Register `server-ready`, `error`, and cleanup handlers before relying on a preview URL; retain the unsubscribe functions.
- Use the URL emitted by `server-ready` rather than constructing a preview host.

## Authentication

The smoke test must not contain API keys, registry tokens, cookies, or `.env` data. If commercial API-key configuration or organization auth is required, consume the existing runtime binding and initialization module without displaying its value or duplicating the flow.

## Workflow

1. Confirm the current package and browser support assumptions from repository evidence.
2. Reuse or create a singleton owner for the WebContainer instance.
3. Define a tiny synthetic project with a locked dependency set and explicit start script.
4. Mount the tree, spawn the repository-approved install command, stream bounded status output, and fail on a nonzero exit.
5. Subscribe to readiness and error events, start the server, and attach the emitted URL to the intended preview element.
6. Record cleanup behavior for listeners, processes, and `teardown()` when the owning view is permanently disposed.

## Approval Boundaries

Do not add arbitrary user source, private packages, production secrets, telemetry, or broad network access to the smoke test without explicit authorization and a security review. Do not alter production isolation headers merely to make a local example pass.

## Output

Return the exact test surface, package and header evidence, lifecycle owner, expected state sequence, bounded logs, preview readiness result, cleanup path, and any environment-specific limitation.

## Error Handling

| Condition | Response |
|---|---|
| A second boot path exists | Stop and consolidate lifecycle ownership before testing. |
| Install exits nonzero | Preserve the exit code and bounded output; do not blindly retry. |
| Preview never becomes ready | Check process exit and `port`/`error` events before changing ports. |
| Test needs real customer code | Replace it with a synthetic fixture and report the missing contract separately. |

## Examples

For a Vite host, mount a two-file synthetic Node project, wait for a successful install exit, start its server, and verify the `server-ready` URL in one supported browser without committing any generated dependency tree.

## Resources

- [Official StackBlitz and WebContainers references](references/official-docs.md)
- [WebContainers quickstart](https://webcontainers.io/guides/quickstart)
- [WebContainer API reference](https://webcontainers.io/api)
