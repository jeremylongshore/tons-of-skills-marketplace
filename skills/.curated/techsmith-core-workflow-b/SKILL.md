---
name: techsmith-core-workflow-b
description: >-
  Manage a controlled Camtasia batch export using local standalone projects and the installed version's modern exporter. Use when producing approved project queues without legacy CamtasiaProducer assumptions. Trigger with "Camtasia batch export", "produce Camtasia projects", or "Camtasia render queue".
argument-hint: "[project-manifest] [output-directory]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- desktop-automation
- techsmith
- export
model: inherit
effort: medium
compatibility: Designed for Claude Code; TechSmith product execution requires an approved Windows or macOS desktop as documented
---
# Camtasia Modern Batch Export

## Overview

This skill builds a reproducible export manifest while respecting Camtasia's desktop boundaries. It stages standalone projects on a local non-synced drive, validates media and version compatibility, and uses the modern Batch Export experience or a command contract explicitly verified for the installed release.

## Prerequisites

- Licensed Camtasia Editor on an approved workstation
- Projects saved as standalone or exported/zipped with all referenced media
- Local non-synced scratch and output directories with capacity headroom
- An approved export preset and acceptance checks for the produced media

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect local scripts, manifests, logs, and tests. Use `WebFetch` only for current primary TechSmith documentation. Use `Write` or `Edit` only after confirming the target repository file and approval boundary.

## Current Contract

- Camtasia projects are not backward-compatible; pin the producing workstation version.
- Keep active projects, media, scratch, and export targets on local storage while Camtasia is open.
- The legacy exporter was removed in 2024.1.3; never assume `CamtasiaProducer.exe` exists.
- Prefer the current Batch Export UI; automate export only from documentation or help output matching the installed version.

## Licensing and Authentication

TechSmith desktop activation is not API authentication. Resolve individual sign-in versus business-key or approved offline activation before execution. Redact all keys, account identifiers, activation artifacts, and sensitive endpoint details.

## Instructions

1. Build a manifest of project path, project version, media completeness, preset, destination, and expected output.
2. Copy approved standalone projects to local scratch only after verifying checksums and free space.
3. Open a canary project in the pinned Camtasia version and resolve missing-media or font/codec warnings.
4. Queue projects in the modern Batch Export workflow with one approved preset per output class.
5. Monitor completion, failure state, output growth, and workstation capacity without launching duplicate exporters.
6. Validate each output's existence, duration, streams, dimensions, and checksum before promotion or archival.

## Approval Boundaries

Do not rewrite TSCPROJ internals, run active projects from synchronized storage, or silently substitute an export preset. A failed project must not block evidence for completed items.

## Output

Return the pinned Camtasia version, manifest digest, local scratch path, per-project result, preset, media validation, promotion state, and cleanup.

## Error Handling

| Condition | Response |
|---|---|
| Project newer than workstation | Move the job to the matching or newer approved Camtasia version. |
| Missing media | Restore a standalone/zipped project or original local paths before export. |
| Legacy exporter requested | Reject the plan and select the modern exporter supported by the installed release. |
| Output validation fails | Keep the output quarantined and preserve project-specific diagnostics. |

## Examples

The example below shows the minimum redacted evidence expected from a successful invocation of this operator workflow.

```text
project=release-demo.tscproj; version=2026.x; storage=local; preset=approved-mp4; validation=pass
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Project and recording files](https://support.techsmith.com/hc/en-us/articles/203730028-Working-with-Camtasia-Editor-TSCPROJ-and-TREC-Files)
- [Legacy exporter removal](https://support.techsmith.com/hc/en-us/articles/31882425655565-Removal-of-Legacy-Exporter-From-Camtasia-2024)
