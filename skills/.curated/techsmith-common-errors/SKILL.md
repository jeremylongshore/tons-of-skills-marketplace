---
name: techsmith-common-errors
description: >-
  Analyze and classify Snagit COM, Camtasia recorder, project-storage, export, installation, and activation failures from redacted evidence. Use when TechSmith automation fails or behaves differently after an upgrade. Trigger with "TechSmith error", "Snagit COM failure", or "Camtasia export problem".
argument-hint: "[product] [failure-symptom]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- desktop-automation
- techsmith
- troubleshooting
model: inherit
effort: medium
compatibility: Designed for Claude Code; TechSmith product execution requires an approved Windows or macOS desktop as documented
---
# TechSmith Automation Error Triage

## Overview

This skill diagnoses the layer that failed before suggesting a change. It distinguishes COM registration, executable/version drift, interactive-session limits, local-storage violations, missing media, licensing, and removed legacy exporter assumptions.

## Prerequisites

- Product name, exact installed version, operating system, and architecture
- A redacted command, exit code, error text, and relevant local paths
- Confirmation whether the job ran interactively, remotely, or as a service
- Permission to inspect logs without collecting captures, project media, or license material

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect local scripts, manifests, logs, and tests. Use `WebFetch` only for current primary TechSmith documentation. Use `Write` or `Edit` only after confirming the target repository file and approval boundary.

## Current Contract

- Snagit COM creation failures are registration or Windows-environment problems, not API authentication failures.
- Camtasia 2022+ recorder automation uses `CamtasiaRecorder.exe`; old executables and short switches are historical.
- The legacy exporter is absent from Camtasia 2024.1.3+.
- Active Camtasia projects on network, cloud, external, or actively synced paths are unsupported.

## Licensing and Authentication

TechSmith desktop activation is not API authentication. Resolve individual sign-in versus business-key or approved offline activation before execution. Redact all keys, account identifiers, activation artifacts, and sensitive endpoint details.

## Instructions

1. Capture the exact product/version, executable or ProgID, working directory, session type, and first failing operation.
2. Classify the failure as install/registration, activation, command contract, interactive desktop, project/media, export/codec, permissions, or capacity.
3. Compare only the implicated surface with current official documentation and the installed type library or executable help.
4. Reproduce with the smallest safe probe: COM instantiation, executable discovery, local sample project, or output-directory write.
5. Apply one reversible fix at a time and rerun the same probe.
6. Record the confirmed cause, evidence, remediation, rollback, and residual risk.

## Approval Boundaries

Never request a software key, raw capture, customer video, or full project archive as routine diagnostic evidence. Do not recommend disabling endpoint security as a generic fix.

## Output

Return the failure layer, safe evidence, confirmed cause or ranked hypotheses, one reversible action, verification result, and escalation package.

## Error Handling

| Condition | Response |
|---|---|
| `REGDB_E_CLASSNOTREG` | Confirm Windows, installed Snagit version, and registration; use the documented elevated `/register` recovery only with approval. |
| Recorder switch ignored | Check executable generation and replace historical short switches with documented current switches. |
| Project media missing | Restore original local paths or a standalone/zipped project; do not edit TSCPROJ internals first. |
| Legacy producer missing | Remove the obsolete dependency and use the modern export workflow supported by the installed version. |

## Examples

The example below shows the minimum redacted evidence expected from a successful invocation of this operator workflow.

```text
layer=command-contract; product=Camtasia-2026; cause=legacy-exporter-assumption; action=replace-current-workflow
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Legacy exporter removal](https://support.techsmith.com/hc/en-us/articles/31882425655565-Removal-of-Legacy-Exporter-From-Camtasia-2024)
- [Cloud storage compatibility](https://support.techsmith.com/hc/en-us/articles/203732738-Cloud-Storage-Compatibility-FAQ)
