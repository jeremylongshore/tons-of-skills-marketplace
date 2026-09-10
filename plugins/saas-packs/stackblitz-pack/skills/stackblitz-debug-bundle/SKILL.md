---
name: stackblitz-debug-bundle
description: >-
  Produce a privacy-safe WebContainer diagnostic bundle with browser capability, isolation-header, lifecycle, event, process-exit, dependency, and resource evidence. Use when an incident needs a shareable artifact rather than ad hoc console screenshots. Trigger with "StackBlitz debug bundle", "collect WebContainer diagnostics", or "WebContainer incident evidence".
argument-hint: "[project-path] [output-path]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.7.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- stackblitz
- diagnostics
- privacy
model: inherit
effort: medium
compatibility: Designed for Claude Code
---
# Privacy-Safe WebContainer Diagnostic Bundle

## Overview

This skill defines or implements a bounded diagnostic artifact for WebContainer problems. The bundle records state and outcomes, not arbitrary source, environment values, complete terminal output, browser history, cookies, or credential material.

## Prerequisites

- A named incident or reproducible failure and an approved output location
- Agreement on who may receive the bundle and how long it may be retained
- Permission to inspect the relevant host configuration and bounded runtime evidence

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to locate existing logging, header, boot, event, and process instrumentation. Use `WebFetch` only for current official StackBlitz or WebContainers documentation. Use `Write` for a new approved bundle schema or artifact and `Edit` for narrow instrumentation changes.

## Current Contract

- Record a schema version, capture time, application release, package versions, coarse browser family/version, secure-context state, and `crossOriginIsolated` boolean.
- Record the presence and normalized values of relevant response headers without unrelated headers or cookies.
- Record lifecycle transitions, event names, process command identity, exit code, duration, and a bounded/redacted output tail.
- Record only filesystem counts and tested synthetic paths; do not enumerate or copy user file contents.
- Record resource symptoms such as out-of-memory errors without inventing a universal numeric memory quota.
- Make every redaction and omitted evidence class visible in the bundle metadata.

## Authentication

Never include API-key values, OAuth parameters, registry credentials, cookies, URLs carrying tokens, `.env` content, private package metadata beyond the minimum identity, or full user-agent/client fingerprint data. Record auth state as a coarse enum when relevant.

## Workflow

1. Define the incident ID, audience, retention, schema, byte cap, and redaction rules.
2. Collect static package and hosting configuration from repository evidence.
3. Collect browser capability, served-header, and lifecycle state from the failing session.
4. Add bounded event and process evidence, preserving exit codes and timestamps.
5. Apply automatic redaction, then perform a human review before sharing.
6. Reproduce once with a synthetic fixture and attach the bundle hash plus collection limitations.

## Approval Boundaries

Require explicit authorization before adding runtime telemetry, persisting a bundle, collecting user-session evidence, or sending the artifact outside the approved audience. A human must review the final bytes before external disclosure.

## Output

Return the schema and bundle path, SHA-256 digest, byte count, collected and omitted fields, redaction result, reproduction link or command, audience/retention, and unresolved evidence gaps.

## Error Handling

| Condition | Response |
|---|---|
| Bundle exceeds its cap | Keep structured summaries and trim repeated output deterministically. |
| Secret-like material is detected | Refuse publication, redact from source, regenerate, and review again. |
| Runtime is unavailable | Emit a partial bundle labeled with missing dynamic evidence. |
| User source is requested | Substitute counts, hashes, or a synthetic reproduction. |

## Examples

For an intermittent boot failure, create a JSON bundle containing package versions, header values, lifecycle transitions, event names, one process exit record, redaction metadata, and a digest—without source files or secret values.

## Resources

- [Official StackBlitz and WebContainers references](references/official-docs.md)
- [WebContainer API events](https://webcontainers.io/api)
- [WebContainers troubleshooting](https://webcontainers.io/guides/troubleshooting)
