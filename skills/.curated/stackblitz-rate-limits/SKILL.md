---
name: stackblitz-rate-limits
description: >-
  Establish evidence-based WebContainer capacity budgets for boot concurrency, mounted files, dependency installs, processes, previews, memory symptoms, and browser support. Use when a StackBlitz experience is slow, unstable, or being prepared for wider rollout. Trigger with "WebContainer limits", "StackBlitz capacity", or "WebContainer performance budget".
argument-hint: "[project-path] [journey]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.7.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- stackblitz
- performance
- capacity
model: inherit
effort: medium
compatibility: Designed for Claude Code
---
# WebContainer Capacity and Constraints

## Overview

This skill replaces unsupported universal quota tables with measured application budgets. WebContainer capacity depends on the browser, device, project, dependency graph, concurrent embeds, and hosted runtime; the output records local thresholds and graceful degradation rather than claiming a fixed vendor limit.

## Prerequisites

- A named user journey, supported browser/device matrix, and representative synthetic project
- Existing performance or browser-test tooling, or permission to define a measurement plan
- Product thresholds for startup, interaction, failure recovery, and fallback

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect mounted inputs, lockfiles, process creation, embeds, cleanup, and existing performance budgets. Use `WebFetch` only for current official StackBlitz or WebContainers documentation. Use `Write` or `Edit` only for an approved measurement harness or bounded optimization.

## Current Contract

- Only one WebContainer may be booted concurrently on a page; additional experiences must share ownership or defer loading.
- Multiple projects, processes, dependencies, and embeds consume browser memory; out-of-memory behavior is device- and browser-dependent.
- Native addons do not run unless replaced by JavaScript or WebAssembly implementations.
- Including the applicable lockfile can avoid fresh dependency resolution and improve repeatability.
- Mount only required files and prefer one bulk `mount()` for initial hydration.
- Use lazy or click-to-load embeds and a static fallback when the page contains several interactive examples.

## Authentication

Capacity tests use synthetic public packages by default. Never copy private source, tokens, registry credentials, or customer dependency metadata into a benchmark artifact. Licensed enterprise behavior must be tested only in its authorized environment.

## Workflow

1. Define the critical journey and measurable startup, install, preview, memory-symptom, and recovery thresholds.
2. Inventory mounted bytes/files, dependency count and lockfile, process count, preview count, and cleanup behavior.
3. Measure a cold run and a repeat run across the supported browser/device matrix.
4. Vary one dimension at a time using synthetic fixtures and record the first degraded or failed state.
5. Apply the smallest optimization: reduce mounted inputs, pin/trim dependencies, reuse lifecycle ownership, defer embeds, or terminate unused processes.
6. Re-measure, set an application-owned budget, and define a user-visible fallback before rollout.

## Approval Boundaries

Do not run load experiments against customer projects, weaken browser security, remove required functionality, or change production loading behavior without explicit scope. Show measured impact and rollback before rollout.

## Output

Return the journey and matrix, input dimensions, measurements, application budgets, bottleneck evidence, optimization, before/after result, graceful fallback, rollback, and limits not established by evidence.

## Error Handling

| Condition | Response |
|---|---|
| Browser reports out of memory | Reduce concurrent projects/processes and mounted/dependency size; preserve fallback. |
| Install time is unstable | Pin inputs, include the lockfile, and separate network variance from runtime work. |
| A native addon fails | Select a JavaScript/WebAssembly alternative or declare the project incompatible. |
| No vendor quota is documented | Publish a measured application budget, not an invented universal number. |

## Examples

For a documentation page with six embeds, measure cold and click-to-load behavior, keep one active runtime at a time, define a static fallback, and record browser/device thresholds without claiming a fixed memory limit.

## Resources

- [Official StackBlitz and WebContainers references](references/official-docs.md)
- [WebContainers troubleshooting](https://webcontainers.io/guides/troubleshooting)
- [Working with the filesystem](https://webcontainers.io/guides/working-with-the-file-system.html)
