---
name: stackblitz-core-workflow-a
description: >-
  Architect a custom in-browser development experience around WebContainers with explicit file, editor, terminal, process, preview, and persistence boundaries. Use when evolving a playground into a maintainable IDE-like product. Trigger with "build a WebContainer IDE", "browser code editor architecture", or "StackBlitz playground design".
argument-hint: "[project-path] [experience-scope]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- stackblitz
- architecture
- browser-ide
model: inherit
effort: high
compatibility: Designed for Claude Code
---
# Custom WebContainer Experience Architecture

## Overview

This skill converts an IDE-like feature request into a bounded architecture. It keeps the host UI, virtual filesystem, editor models, terminal streams, runtime processes, preview frames, and persistence strategy separate so a prototype does not accidentally become an unsafe monolith.

## Prerequisites

- Named user journeys and a target browser application
- A decision that a custom WebContainer experience is preferable to a StackBlitz SDK embed
- Product, licensing, security, and persistence owners for production use

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to map the host framework, editor and terminal libraries, application state, persistence, and runtime boundary. Use `WebFetch` only for current official StackBlitz or WebContainers documentation. Use `Write` or `Edit` only for a user-approved bounded slice.

## Current Contract

- The host application owns a single lifecycle adapter; individual panes do not call `boot()` or `teardown()`.
- File explorer paths are validated and normalized before virtual-filesystem operations; editor models use stable canonical paths.
- Terminal input/output is explicitly bound to one process and released on disposal.
- Preview URLs come from runtime events and are treated as untrusted application content, not trusted host UI.
- The WebContainer filesystem is not a persistence guarantee. Define an explicit save/export/versioning path before claiming durable work.
- Register error, port, and server readiness observers with bounded logging and unsubscribe ownership.

## Authentication

Do not mount host secrets, auth tokens, customer `.env` files, or ambient browser credentials into user-controlled projects. If private packages are required, use the documented organization auth boundary and disclose which project code can access installed material.

## Workflow

1. Define the smallest user journey and decide which panes and runtime capabilities it truly needs.
2. Draw ownership for host state, lifecycle adapter, filesystem, editor models, process/terminal handles, preview, and persistence.
3. Establish a typed message/event contract between panes instead of sharing raw runtime globals.
4. Implement one vertical slice: open a synthetic file, edit it, write it, run a bounded command, and display the emitted preview URL.
5. Add path-policy, process-cancellation, preview isolation, save/export, and permanent-disposal behavior.
6. Verify keyboard/accessibility behavior, HMR ownership, memory cleanup, and recovery from failed startup before expanding features.

## Approval Boundaries

Require explicit approval before executing arbitrary user code, persisting or exporting user files, connecting private registries, injecting preview scripts, or enabling collaboration/telemetry. Present data flow, abuse cases, retention, and rollback first.

## Output

Return the user journey, component and trust-boundary map, lifecycle and data contracts, implemented slice, verification evidence, persistence semantics, rollout stages, rollback, and open product/security decisions.

## Error Handling

| Condition | Response |
|---|---|
| UI panes share raw runtime state | Introduce a scoped adapter and typed events before adding features. |
| Editor and filesystem diverge | Reconcile by canonical path and explicit write acknowledgements. |
| Preview is treated as trusted | Isolate it and define allowed host-preview communication. |
| Persistence is unspecified | Label the experience ephemeral and stop durability claims. |

## Examples

For an educational playground, implement one synthetic project with a file pane, editor, bounded terminal command, preview, and explicit download/export action while leaving collaboration and private packages out of scope.

## Resources

- [Official StackBlitz and WebContainers references](references/official-docs.md)
- [WebContainers introduction](https://webcontainers.io/guides/introduction)
- [Working with the filesystem](https://webcontainers.io/guides/working-with-the-file-system.html)
