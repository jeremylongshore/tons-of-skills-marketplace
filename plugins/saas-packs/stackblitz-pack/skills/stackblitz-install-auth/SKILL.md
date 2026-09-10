---
name: stackblitz-install-auth
description: >-
  Prepare a StackBlitz WebContainer or JavaScript SDK integration with pinned packages, compatible isolation headers, and the correct commercial or private-package authentication path. Use when adding StackBlitz to an existing web application or reviewing its startup contract. Trigger with "install StackBlitz", "set up WebContainers", or "configure WebContainer auth".
argument-hint: "[project-path] [webcontainer|embed]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- stackblitz
- webcontainers
- setup
model: inherit
effort: medium
compatibility: Designed for Claude Code
---
# StackBlitz Integration Preflight

## Overview

This skill produces a repo-grounded installation and startup plan for either a custom WebContainer application or a StackBlitz SDK embed. It separates ordinary browser startup from commercial API-key configuration and organization-scoped private-package authentication.

## Prerequisites

- A named browser application and permission to inspect its package and hosting configuration
- A decision between `@webcontainer/api` and `@stackblitz/sdk`, or evidence that both are needed
- A licensing decision for production commercial use before release

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect package manifests, lockfiles, browser entrypoints, headers, and existing secret bindings. Use `WebFetch` only for current official StackBlitz or WebContainers documentation. Use `Write` or `Edit` only after the evidence pass, and never place API keys or OAuth material in source files.

## Current Contract

- Pin the package version selected by the repository's dependency policy; do not install an unreviewed moving tag.
- Call `configureAPIKey` before `WebContainer.boot()` when a commercial license supplies an API key.
- Call `auth.init` before boot when organization users need private-package access; the user must be logged in, belong to the issuing organization, and authorize the site.
- Match the `Cross-Origin-Embedder-Policy` response header to the `coep` boot option. Use HTTPS outside localhost.
- A StackBlitz SDK embed is a separate surface and does not require booting a custom WebContainer in the host application.

## Authentication

Public prototypes may not need user authentication, but production commercial use requires a licensing review. Treat the WebContainer API key as a secret runtime binding. Treat the auth client ID and scope as configuration, initialize auth during page loading, and handle `need-auth`, `authorized`, and `auth-failed` explicitly. Never infer that ordinary StackBlitz login grants access to private packages.

## Workflow

1. Inspect the framework, package manager, lockfile, client/server boundary, CSP, and current response-header configuration.
2. Choose the minimum package surface and record the installed or proposed pinned version.
3. Decide whether the integration needs a commercial API key, organization auth, neither, or both.
4. Configure consistent COOP/COEP headers and the matching boot option; verify the final HTML response, including cached responses.
5. Add one startup module that orders API-key configuration, auth initialization, and the single boot call correctly.
6. Validate in a supported desktop browser over the same origin and headers intended for deployment.

## Approval Boundaries

Default to inspection and a proposed patch. Require explicit authorization before changing production headers, CSP, identity-provider settings, licensed API-key bindings, or deployment configuration. Never create, rotate, expose, or revoke a credential without a separately authorized operational step.

## Output

Return the selected integration mode, package/version evidence, licensing and auth decision, header/boot contract, changed or proposed files, verification results, rollout plan, rollback, and unresolved browser or policy risks.

## Error Handling

| Condition | Response |
|---|---|
| API key configured after boot | Stop and move configuration before the first boot call. |
| Auth reports `need-auth` | Present the user-authorized flow; do not loop or fabricate authorization. |
| `crossOriginIsolated` is false | Inspect actual response headers and cache behavior before changing code. |
| Integration mode is unclear | Compare custom runtime requirements with embed-only requirements before installing both SDKs. |

## Examples

Given an existing Vite app, identify its lockfile and hosting headers, select a pinned WebContainer API version, document whether commercial licensing applies, and propose a single ordered startup module without reading any secret value.

## Resources

- [Official StackBlitz and WebContainers references](references/official-docs.md)
- [WebContainer API reference](https://webcontainers.io/api)
- [StackBlitz JavaScript SDK](https://developer.stackblitz.com/platform/api/javascript-sdk)
