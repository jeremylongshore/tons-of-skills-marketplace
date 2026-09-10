---
name: techsmith-webhooks-events
description: >-
  Process Snagit COM completion and local TechSmith artifact events with bounded watchers, stable-file checks, deduplication, and recovery. Use when a desktop workflow needs event-driven handoff without pretending TechSmith exposes webhooks. Trigger with "TechSmith events", "Snagit capture event", or "watch Camtasia output".
argument-hint: "[watch-directory] [event-manifest-path]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- desktop-automation
- techsmith
- events
model: inherit
effort: medium
compatibility: Designed for Claude Code; TechSmith product execution requires an approved Windows or macOS desktop as documented
---
# TechSmith Local Capture and File Events

## Overview

Snagit COM offers capture event callbacks or completion polling, while local files can be observed with an operating-system watcher; these are local signals, not authenticated vendor webhooks. This skill converts noisy callbacks into durable artifact-ready events only after the file is stable and valid.

## Prerequisites

- Approved local directory, artifact types, data classification, and retention
- One durable event store with job identity, source path hash, and processing state
- A bounded watcher lifetime, reconciliation interval, and shutdown behavior
- Downstream consumer contract and quarantine destination

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect local scripts, manifests, logs, and tests. Use `WebFetch` only for current primary TechSmith documentation. Use `Write` or `Edit` only after confirming the target repository file and approval boundary.

## Current Contract

- Prefer Snagit COM completion events where the client runtime supports them; otherwise use bounded `IsCaptureDone` polling.
- Filesystem watcher notifications are hints and may duplicate, reorder, or omit events.
- Do not emit artifact-ready until size and modification time stabilize and format validation passes.
- Deduplicate by durable job/output identity and reconcile the directory periodically.

## Licensing and Authentication

TechSmith desktop activation is not API authentication. Resolve individual sign-in versus business-key or approved offline activation before execution. Redact all keys, account identifiers, activation artifacts, and sensitive endpoint details.

## Instructions

1. Define allowed directory roots, extensions, stable-file interval, event schema, idempotency key, and lifecycle states.
2. Subscribe to the narrow COM event or local filesystem create/change signal required by the workflow.
3. Canonicalize the path, reject escapes and disallowed types, and correlate it with an authorized job.
4. Wait for stable size/time across bounded observations, then validate format, nonzero content, and checksum.
5. Insert or update the durable event idempotently before invoking downstream work.
6. Reconcile missed files, dead-letter repeated failures, emit metrics, and stop the watcher cleanly on shutdown.

## Approval Boundaries

Do not expose the watch directory over a public endpoint, call local events webhooks, process actively written project files, or upload an artifact before authorization and validation.

## Output

Return watcher scope, event counts, deduplicated identities, stability/validation results, downstream acknowledgements, reconciled misses, dead letters, and shutdown state.

## Error Handling

| Condition | Response |
|---|---|
| Duplicate notification | Acknowledge the existing durable identity without repeating side effects. |
| File never stabilizes | Quarantine or defer it and preserve bounded metadata. |
| Watcher overflow or restart | Run full allowlisted reconciliation from the last durable checkpoint. |
| Path not tied to an authorized job | Reject it and alert without opening the media. |

## Examples

The example below shows the minimum redacted evidence expected from a successful invocation of this operator workflow.

```text
signal=file-change; job=export-441; stable=3/3; checksum=recorded; event=artifact-ready; duplicates=2
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Snagit COM event model](https://assets.techsmith.com/Docs/Snagit-2025-COM-Server-Guide.pdf)
- [Camtasia local-storage model](https://support.techsmith.com/hc/en-us/articles/203730028-Working-with-Camtasia-Editor-TSCPROJ-and-TREC-Files)
