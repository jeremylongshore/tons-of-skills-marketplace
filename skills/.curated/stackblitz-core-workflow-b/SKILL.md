---
name: stackblitz-core-workflow-b
description: >-
  Design and implement a StackBlitz JavaScript SDK embed with an explicit project source, load strategy, UI options, persistence expectations, and responsive fallback. Use when documentation, training, or product pages need an interactive code example without owning a custom WebContainer runtime. Trigger with "embed StackBlitz", "StackBlitz SDK project", or "interactive code example".
argument-hint: "[project-path] [project-id|github-path|inline]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- stackblitz
- embedding
- documentation
model: inherit
effort: medium
compatibility: Designed for Claude Code
---
# StackBlitz Embed Integration

## Overview

This skill selects and implements the supported SDK method for an existing StackBlitz project, a public GitHub path, or an inline project. It treats the embed as third-party executable content with explicit loading, persistence, accessibility, and browser-support boundaries.

## Prerequisites

- A named host page and the source of the project to embed
- Confirmation that source code is public and safe to send to or execute through StackBlitz
- A static fallback and intended responsive behavior

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect the host component, content source, CSP, existing third-party scripts, and responsive patterns. Use `WebFetch` only for current official StackBlitz documentation. Use `Write` or `Edit` after the embed source and trust boundary are confirmed.

## Current Contract

- Use `embedProjectId` for an existing StackBlitz project, `embedGithubProject` for a public GitHub repository/path, and `embedProject` for a generated inline project.
- Inline projects live in browser memory unless a user forks them into a StackBlitz account; do not promise automatic persistence.
- Use current `EmbedOptions`; do not depend on deprecated `forceEmbedLayout` behavior.
- `clickToLoad` is a useful consent/performance boundary for expensive or numerous embeds.
- Treat the returned VM instance as an integration capability with an explicit owner and disposal path.
- WebContainer-based embeds have stricter browser constraints than static code fallbacks.

## Authentication

Do not embed private repositories, secrets, licensed source, or authenticated application state through a public project method. If enterprise origin or private access is required, stop and obtain the documented organization configuration and security approval.

## Workflow

1. Inspect the host page, choose the authoritative project source, and classify its sensitivity.
2. Select one SDK method and a pinned SDK version from the repository lockfile.
3. Define height, view, theme, `openFile`, and `clickToLoad` from the user journey; avoid deprecated options.
4. Add a titled container, loading state, error state, and accessible static link or code fallback.
5. Reconcile CSP, privacy disclosure, responsive layout, and browser support with the site owner.
6. Test initial load, user-triggered load, failure, keyboard flow, narrow viewport, and navigation cleanup.

## Approval Boundaries

Require explicit authorization before adding a third-party executable embed, changing CSP, loading private code, selecting an enterprise origin, or adding analytics. Show the data/source flow and fallback before deployment.

## Output

Return the selected source and SDK method, package/version evidence, embed options, trust and persistence semantics, accessibility/fallback behavior, tests run, changed files, rollout, and rollback.

## Error Handling

| Condition | Response |
|---|---|
| GitHub project cannot load | Verify the public repository, branch/tag/commit, and optional subfolder path. |
| Inline work disappears | Explain browser-memory semantics and offer an explicit fork/export path. |
| Embed breaks narrow layouts | Use a responsive container and preserve the static fallback. |
| Host CSP blocks the embed | Propose the narrow official origins; never disable CSP wholesale. |

## Examples

Given a public tutorial repository pinned to a commit, add a click-to-load embed opening the relevant file and provide a normal GitHub link plus static code sample when the runtime cannot load.

## Resources

- [Official StackBlitz and WebContainers references](references/official-docs.md)
- [StackBlitz JavaScript SDK](https://developer.stackblitz.com/platform/api/javascript-sdk)
- [SDK options reference](https://developer.stackblitz.com/platform/api/javascript-sdk-options)
