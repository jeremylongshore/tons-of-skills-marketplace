---
name: stackblitz-local-dev-loop
description: >-
  Establish a reproducible local development and browser-test loop for a WebContainer host, including isolation-header assertions, single-boot behavior under HMR, and cleanup checks. Use when a StackBlitz integration works manually but lacks dependable regression coverage. Trigger with "test WebContainers locally", "StackBlitz dev loop", or "WebContainer Playwright test".
argument-hint: "[project-path] [test-command]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.7.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- stackblitz
- testing
- webcontainers
model: inherit
effort: medium
compatibility: Designed for Claude Code
---
# WebContainer Local Development Loop

## Overview

This skill turns a manually tested WebContainer host into a repeatable local loop. It separates pure file-tree and state-machine tests from browser integration tests that require SharedArrayBuffer, Service Workers, WebAssembly, and real response headers.

## Prerequisites

- A named host application with an existing test framework or permission to add focused coverage
- A supported desktop browser available to the project's browser-test runner
- The repository's normal local HTTPS or localhost convention

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to locate runtime construction, HMR boundaries, response headers, unit tests, and browser tests. Use `WebFetch` only for current official StackBlitz or WebContainers documentation. Use `Write` or `Edit` for minimal user-requested tests and configuration.

## Current Contract

- Unit-test pure transformations such as flat-files-to-`FileSystemTree` without booting WebContainers.
- Test actual boot, process, Service Worker, and preview behavior in a real browser runner rather than a DOM-only simulator.
- Assert the final document is a secure context and `crossOriginIsolated` before boot.
- Preserve one boot promise across HMR; a module reload must not create a second concurrent instance.
- Exercise disposal separately from HMR so `teardown()` does not invalidate an instance still owned by the current page.

## Authentication

Use synthetic public dependencies by default. If the browser test requires licensed or private-package access, bind credentials through the CI secret store, restrict the test environment, redact logs, and skip with an explicit reason when authorized credentials are unavailable.

## Workflow

1. Map pure logic, browser-only logic, startup ownership, and deployment-header ownership.
2. Add fast unit tests for file-tree validation, state transitions, path policy, and bounded log formatting.
3. Add one browser smoke test that verifies isolation, boots once, mounts a synthetic fixture, observes a zero-exit command, and reaches preview readiness.
4. Trigger the repository's HMR path and confirm the boot owner remains singular.
5. Exercise navigation/disposal and confirm listeners and processes are released without breaking a surviving owner.
6. Run the narrow test first, then the project's normal lint, typecheck, and browser-test gates.

## Approval Boundaries

Do not weaken browser security flags, disable isolation checks, commit credentials, or make a flaky integration test silently optional. Changes to shared CI browsers, production headers, or licensed secrets require explicit authorization.

## Output

Return the test-layer map, exact assertions, browsers exercised, commands run, HMR and cleanup evidence, skips with reasons, changed files, and remaining platform limitations.

## Error Handling

| Condition | Response |
|---|---|
| DOM simulator cannot boot | Move runtime behavior to a real browser test; keep only pure logic in unit tests. |
| HMR causes a second boot | Hoist and cache the boot promise at the application's stable ownership boundary. |
| CI lacks isolation | Inspect the served response and proxy chain; do not launch with unsafe browser flags. |
| Browser support differs | Record the exact supported/beta behavior rather than declaring universal compatibility. |

## Examples

Given a Vite host with Playwright, add a pure `FileSystemTree` unit test and one Chromium smoke test that asserts `crossOriginIsolated`, observes one boot, receives a preview URL, and cleans up after navigation.

## Resources

- [Official StackBlitz and WebContainers references](references/official-docs.md)
- [WebContainers browser support](https://webcontainers.io/guides/browser-support)
- [Configuring headers](https://webcontainers.io/guides/configuring-headers)
