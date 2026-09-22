---
name: techsmith-hello-world
description: >-
  Prove an approved Windows Snagit installation with a non-capturing COM creation probe and optional operator-approved window capture. Use when validating a new TechSmith workstation safely. Trigger with "TechSmith hello world", "test Snagit COM", or "verify Snagit automation".
argument-hint: "[workstation-alias] [optional-output-directory]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- desktop-automation
- techsmith
- getting-started
model: inherit
effort: medium
compatibility: Designed for Claude Code; TechSmith product execution requires an approved Windows or macOS desktop as documented
---
# Snagit Verified COM Probe

## Overview

This skill separates installation proof from screen capture: the default hello world creates the supported COM object and verifies its expected members without calling `Capture()`. An optional second phase captures one operator-selected window only after scope and destination approval.

## Prerequisites

- Windows with Snagit installed and licensed for the current user
- An interactive desktop session; COM capture is not a headless web API
- Approval to instantiate the local COM server
- Separate approval and an approved destination for any optional capture

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect local scripts, manifests, logs, and tests. Use `WebFetch` only for current primary TechSmith documentation. Use `Write` or `Edit` only after confirming the target repository file and approval boundary.

## Current Contract

- Use the current ProgID `Snagit.ImageCapture.1`; official samples also demonstrate `SNAGIT.ImageCapture`.
- The safe default stops after object creation and member inspection.
- If capture is approved, use window input `1` and file output `2`, not historical values from this pack.
- Wait for asynchronous completion and validate the returned file before declaring success.

## Licensing and Authentication

TechSmith desktop activation is not API authentication. Resolve individual sign-in versus business-key or approved offline activation before execution. Redact all keys, account identifiers, activation artifacts, and sensitive endpoint details.

## Instructions

1. Confirm workstation alias, Windows session, installed Snagit version, license status, and no-capture default.
2. Create the COM object and inspect the availability of `Capture`, `IsCaptureDone`, `LastCaptureSucceeded`, and `LastFileWritten`.
3. Dispose of the object and report success if only an installation probe was authorized.
4. For optional capture, confirm the exact target window, output directory, preview mode, timeout, and retention.
5. Run one interactive window capture, wait with a deadline, and verify success plus canonical output path.
6. Delete or retain the test artifact according to the approval and record the decision.

## Approval Boundaries

Do not capture the full desktop or clipboard as a connectivity test. Never infer consent from the presence of an interactive session.

## Output

Return workstation alias, product version, ProgID creation result, inspected members, capture authorization, optional artifact validation, and cleanup.

## Error Handling

| Condition | Response |
|---|---|
| Not Windows | Report Snagit COM as unsupported on this platform; do not emulate it. |
| Class not registered | Confirm installation/version and use the vendor-documented registration recovery only with approval. |
| Capture not approved | Stop after COM inspection and report a successful no-capture probe. |
| Wrong output path | Quarantine or remove the test artifact and correct the boundary. |

## Examples

The example below shows the minimum redacted evidence expected from a successful invocation of this operator workflow.

```powershell
$probe = New-Object -ComObject 'Snagit.ImageCapture.1'
$members = $probe | Get-Member -Name Capture, IsCaptureDone, LastCaptureSucceeded, LastFileWritten
# Stop here unless a capture was separately approved.
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Snagit 2025 COM guide](https://assets.techsmith.com/Docs/Snagit-2025-COM-Server-Guide.pdf)
- [Official COM samples](https://github.com/TechSmith/Snagit-COM-Samples)
