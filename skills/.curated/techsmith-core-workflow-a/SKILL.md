---
name: techsmith-core-workflow-a
description: >-
  Build a bounded Windows Snagit image-capture workflow with the supported COM server, exact enums, asynchronous completion, and verified file output. Use when automating approved documentation captures. Trigger with "Snagit COM capture", "automate Snagit screenshot", or "Snagit file output".
argument-hint: "[script-path] [approved-output-directory]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- desktop-automation
- techsmith
- capture
model: inherit
effort: medium
compatibility: Designed for Claude Code; TechSmith product execution requires an approved Windows or macOS desktop as documented
---
# Snagit Controlled COM Capture

## Overview

This skill implements the supported Snagit COM path without inventing a web API. It resolves the installed type library, creates `Snagit.ImageCapture.1`, sets an approved input/output, waits for asynchronous completion, and accepts a file only after success and path validation.

## Prerequisites

- Windows with a licensed, approved Snagit installation and interactive desktop
- A capture subject and output directory approved for the data classification
- The official 2025 COM guide or documentation matching the installed version
- A timeout, cancellation path, and artifact-retention policy

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect local scripts, manifests, logs, and tests. Use `WebFetch` only for current primary TechSmith documentation. Use `Write` or `Edit` only after confirming the target repository file and approval boundary.

## Current Contract

- Use ProgID `Snagit.ImageCapture.1` or the official sample's compatible `SNAGIT.ImageCapture` alias.
- Use exact inputs desktop `0`, window `1`, region `4`; use outputs file `2`, clipboard `4`.
- Set `OutputImageFile` options before invoking `Capture()` when file output is selected.
- Treat `Capture()` as asynchronous; wait for `IsCaptureDone`, then check success and `LastFileWritten`.

## Licensing and Authentication

TechSmith desktop activation is not API authentication. Resolve individual sign-in versus business-key or approved offline activation before execution. Redact all keys, account identifiers, activation artifacts, and sensitive endpoint details.

## Instructions

1. Confirm the installed Snagit version, COM registration, interactive session, capture scope, and approved destination.
2. Load enum definitions from the installed type library or a pinned copy of TechSmith's official enum sample.
3. Create the image-capture object and set input, output, preview behavior, cursor inclusion, file type, and destination explicitly.
4. Invoke one capture and wait with a bounded deadline rather than an unbounded tight loop.
5. Check `LastCaptureSucceeded`, canonicalize `LastFileWritten`, and reject paths outside the approved directory.
6. Validate file existence, nonzero size, expected format, and retention metadata before downstream use.

## Approval Boundaries

Interactive capture can expose sensitive screen content. Require a named subject and operator approval; never default to the full desktop, clipboard, or an unrestricted destination.

## Output

Return product version, ProgID, input/output enums, elapsed time, success flag, canonical redacted path, file validation, and cleanup decision.

## Error Handling

| Condition | Response |
|---|---|
| COM creation fails | Verify Windows installation and registration; stop before changing the registry. |
| Capture deadline exceeded | Cancel downstream work, preserve only redacted state, and require operator inspection. |
| `LastCaptureSucceeded` false | Record capture state and error event data without accepting a file. |
| Output path escapes boundary | Quarantine the artifact and correct directory configuration. |

## Examples

The example below shows the minimum redacted evidence expected from a successful invocation of this operator workflow.

```powershell
$capture = New-Object -ComObject 'Snagit.ImageCapture.1'
$capture.Input = 1   # siiWindow
$capture.Output = 2  # sioFile
# Configure OutputImageFile, call Capture(), then wait with a deadline.
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Snagit 2025 COM guide](https://assets.techsmith.com/Docs/Snagit-2025-COM-Server-Guide.pdf)
- [Official PowerShell samples](https://github.com/TechSmith/Snagit-COM-Samples/tree/main/PowerShell)
