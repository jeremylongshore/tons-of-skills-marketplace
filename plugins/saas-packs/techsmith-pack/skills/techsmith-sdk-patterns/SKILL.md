---
name: techsmith-sdk-patterns
description: >-
  Implement Snagit image capture behind a narrow typed adapter with official enums, ordered configuration, bounded async completion, and path-safe results. Use when productionizing COM automation in PowerShell or .NET. Trigger with "Snagit SDK patterns", "Snagit COM adapter", or "type-safe Snagit capture".
argument-hint: "[repository-path] [language]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- desktop-automation
- techsmith
- sdk
model: inherit
effort: medium
compatibility: Designed for Claude Code; TechSmith product execution requires an approved Windows or macOS desktop as documented
---
# Snagit Typed COM Adapter

## Overview

This skill isolates vendor COM details from business workflow code. The adapter owns object creation, enum translation, configuration order, completion deadlines, event or polling behavior, normalized errors, result validation, disposal, and a fake implementation for tests.

## Prerequisites

- Windows and a language/runtime capable of COM interop
- The installed Snagit type library plus TechSmith's current guide and official samples
- A repository boundary for adapter, domain request/result, and fakes
- Approved capture inputs, destinations, timeout, and retention policy

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect local scripts, manifests, logs, and tests. Use `WebFetch` only for current primary TechSmith documentation. Use `Write` or `Edit` only after confirming the target repository file and approval boundary.

## Current Contract

- Resolve `Snagit.ImageCapture.1` through one factory and report registration errors distinctly.
- Represent inputs with typed values desktop `0`, window `1`, region `4`; outputs file `2`, clipboard `4`.
- Configure file type, naming, directory, preview, and cursor before `Capture()`.
- Normalize asynchronous completion to a deadline-bound result containing success, state, and canonical file path.

## Licensing and Authentication

TechSmith desktop activation is not API authentication. Resolve individual sign-in versus business-key or approved offline activation before execution. Redact all keys, account identifiers, activation artifacts, and sensitive endpoint details.

## Instructions

1. Read repository conventions and locate every direct COM creation or raw enum use.
2. Define `CaptureRequest`, `CaptureResult`, typed enums, normalized error categories, and cancellation behavior.
3. Implement a factory and adapter around the smallest official COM interface needed by the workflow.
4. Add bounded event or polling completion, success checks, canonical path containment, file validation, and disposal.
5. Write a fake adapter and tests for configuration order, timeout, failure, path escape, and cleanup.
6. Migrate one caller at a time and compare results with one approved live capture.

## Approval Boundaries

Do not expose the raw COM object to application layers, accept arbitrary ProgIDs or output paths, or make unbounded capture calls from request handlers.

## Output

Return adapter interface, enum source, migrated callers, test matrix, live verification, compatibility notes, and remaining raw-COM sites.

## Error Handling

| Condition | Response |
|---|---|
| Type library differs | Generate or bind against the installed version and record compatibility instead of forcing a cast. |
| Completion timeout | Return a typed timeout and block output consumption. |
| COM success but file invalid | Return an artifact-validation failure and quarantine the path. |
| Disposal fails | Record it and recycle the worker before accepting more jobs. |

## Examples

The example below shows the minimum redacted evidence expected from a successful invocation of this operator workflow.

```text
CaptureRequest(Input.Window, Output.File, approvedDir, timeout) -> CaptureResult(success, canonicalPath, elapsed)
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Snagit 2025 COM guide](https://assets.techsmith.com/Docs/Snagit-2025-COM-Server-Guide.pdf)
- [Official C# and PowerShell samples](https://github.com/TechSmith/Snagit-COM-Samples)
