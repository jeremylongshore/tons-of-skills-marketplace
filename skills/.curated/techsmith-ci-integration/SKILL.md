---
name: techsmith-ci-integration
description: >-
  Gate Snagit COM and Camtasia automation changes with secretless contract tests plus an explicitly licensed Windows smoke lane. Use when adding CI for TechSmith scripts or deployment assets. Trigger with "TechSmith CI", "Snagit contract tests", or "Camtasia automation checks".
argument-hint: "[repository-path] [windows-runner-label]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- desktop-automation
- techsmith
- ci
model: inherit
effort: medium
compatibility: Designed for Claude Code; TechSmith product execution requires an approved Windows or macOS desktop as documented
---
# TechSmith Desktop Automation CI

## Overview

This skill separates portable checks from workstation-only product execution. Pull requests can validate scripts, enum contracts, manifests, and fixtures without installing licensed desktop software; a protected Windows lane may run a bounded smoke test only when the organization supplies an approved license and interactive session.

## Prerequisites

- A repository containing the PowerShell, C#, deployment, or packaging assets
- A CI runner matrix that distinguishes ordinary hosted runners from approved TechSmith workstations
- Sanitized fixtures for COM success, missing registration, timeout, and file-output failure
- A named owner for any licensed smoke-runner credential and cleanup

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect local scripts, manifests, logs, and tests. Use `WebFetch` only for current primary TechSmith documentation. Use `Write` or `Edit` only after confirming the target repository file and approval boundary.

## Current Contract

- Keep the default pull-request lane secretless and independent of Snagit or Camtasia installation.
- Validate official Snagit enum values: window `1`, region `4`, file output `2`, clipboard output `4`.
- Do not make `CamtasiaProducer.exe` or a legacy exporter a CI prerequisite for current releases.
- Treat the licensed Windows smoke lane as optional, protected, serialized, and manually dispatchable.

## Licensing and Authentication

TechSmith desktop activation is not API authentication. Resolve individual sign-in versus business-key or approved offline activation before execution. Redact all keys, account identifiers, activation artifacts, and sensitive endpoint details.

## Instructions

1. Inventory scripts, manifests, expected output paths, and all places that instantiate a COM object or product executable.
2. Add parser, lint, and unit checks for argument construction, bounded polling, exit handling, redaction, and cleanup.
3. Use fakes for `IsCaptureDone`, `LastCaptureSucceeded`, and `LastFileWritten`; cover timeout and wrong-path cases.
4. Pin a Windows runner label for the product smoke job and require a protected environment with no fork-secret exposure.
5. Run one non-destructive COM creation probe or recorder version probe; never create an unattended recording in pull requests.
6. Publish JUnit-style results and a redacted environment manifest, then remove temporary artifacts.

## Approval Boundaries

Do not place a software key in repository secrets available to forked workflows. Do not install, activate, record, capture, or upload user content on an unapproved hosted runner.

## Output

Return portable-gate results, fixture coverage, licensed-lane disposition, runner identity, product/version evidence, artifact cleanup, and any blocked approval.

## Error Handling

| Condition | Response |
|---|---|
| No Windows smoke runner | Pass portable gates and report the product smoke as explicitly skipped. |
| COM class not registered | Fail the smoke lane with registration diagnostics; do not retry installation. |
| Interactive desktop unavailable | Stop before capture and classify the runner as unsuitable. |
| Secret detected in logs | Cancel publication, rotate the credential, and purge the artifact. |

## Examples

The example below shows the minimum redacted evidence expected from a successful invocation of this operator workflow.

```text
lane=portable; scripts=pass; enum_contract=pass; licensed_smoke=skipped(no-approved-runner)
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Recorder command line](https://support.techsmith.com/hc/en-us/articles/203728678-Using-Command-Lines-to-Operate-the-Camtasia-Recorder)
- [Official COM samples](https://github.com/TechSmith/Snagit-COM-Samples)
