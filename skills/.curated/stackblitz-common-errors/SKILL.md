---
name: stackblitz-common-errors
description: >-
  Diagnose WebContainer startup, isolation, Service Worker, dependency, process, preview, and browser failures from evidence before changing code or headers. Use when a StackBlitz runtime or embed fails, hangs, or behaves differently across browsers. Trigger with "StackBlitz error", "WebContainer failed to boot", or "SharedArrayBuffer error".
argument-hint: "[project-path] [symptom]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.7.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- stackblitz
- troubleshooting
- webcontainers
model: inherit
effort: medium
compatibility: Designed for Claude Code
---
# WebContainer Failure Triage

## Overview

This skill follows a deterministic diagnosis order: browser capability, served headers, lifecycle ownership, runtime events, process exit, dependency compatibility, and preview behavior. It avoids speculative retries and unsafe header weakening.

## Prerequisites

- A reproducible URL or local command and the affected browser/version
- Permission to inspect application code, response headers, and bounded browser/runtime logs
- A synthetic reproduction when the failing project contains sensitive data

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to find boot calls, headers, runtime events, process handling, and dependency manifests. Use `WebFetch` only for current official StackBlitz or WebContainers documentation. Use `Write` or `Edit` only after the failing layer is identified; never retrieve secrets or full user projects for diagnosis.

## Current Contract

- A SharedArrayBuffer or `crossOriginIsolated` failure starts with the actual HTML response's COOP/COEP headers, including `304` behavior.
- A released proxy or duplicate-start failure requires proving whether `boot()` ran more than once, including under HMR.
- Dependency installs should preserve exit code and bounded output; a lockfile can improve repeatability and startup time.
- Native Node addons are unavailable unless an alternative is implemented in JavaScript or WebAssembly.
- Browser privacy controls can block required Service Worker or third-party storage behavior.
- Preview failures are investigated through process exit plus `error`, `port`, and `server-ready` events.

## Authentication

Redact API keys, registry tokens, OAuth details, cookies, source contents, and dynamic preview URLs from shared evidence. For private-package failures, report auth state and package identity without printing credential values.

## Workflow

1. Reproduce with the smallest synthetic project and record browser, URL, secure-context, and isolation state.
2. Inspect the final document headers and cached response behavior.
3. Count boot paths and trace HMR, navigation, and teardown ownership.
4. Capture bounded runtime events, spawned command, exit code, and the final useful output lines.
5. Compare the dependency with documented WebContainer constraints, especially native addons and install behavior.
6. Apply one layer-specific fix, repeat the reproduction, and record rollback plus remaining browser variance.

## Approval Boundaries

Do not disable browser security, relax COOP/COEP or CSP broadly, clear user browser data, replace dependencies, or change production hosting without explicit authorization. Present the failing layer and narrow fix first.

## Output

Return the reproduction, evidence by layer, root cause or ranked hypotheses, exact fix made or proposed, verification, redactions, rollback, and unresolved compatibility risk.

## Error Handling

| Symptom | Evidence-led response |
|---|---|
| SharedArrayBuffer transfer fails | Verify secure context, COOP/COEP, matching boot option, and cached headers. |
| Proxy is released | Find duplicate boot or premature teardown paths, including HMR. |
| Install stalls or fails | Preserve lockfile state, exit code, and bounded output; inspect native-addon use. |
| Preview never appears | Correlate process exit with `port`, `error`, and `server-ready` events. |

## Examples

For a preview that works in Chromium but fails in Firefox private browsing, record browser constraints and Service Worker evidence, preserve a static fallback, and avoid changing the runtime code without a cross-browser reproduction.

## Resources

- [Official StackBlitz and WebContainers references](references/official-docs.md)
- [WebContainers troubleshooting](https://webcontainers.io/guides/troubleshooting)
- [Browser configuration](https://webcontainers.io/guides/browser-config)
