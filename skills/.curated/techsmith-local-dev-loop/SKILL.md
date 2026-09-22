---
name: techsmith-local-dev-loop
description: >-
  Iterate on Snagit COM automation with official samples, a fake adapter, bounded live probes, and disposable local output. Use when developing or reviewing Windows capture scripts. Trigger with "Snagit local development", "test Snagit PowerShell", or "iterate TechSmith automation".
argument-hint: "[repository-path] [sample-scenario]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- desktop-automation
- techsmith
- development
model: inherit
effort: medium
compatibility: Designed for Claude Code; TechSmith product execution requires an approved Windows or macOS desktop as documented
---
# Snagit COM Local Development Loop

## Overview

This skill keeps most development deterministic and screen-safe. Logic is tested against a fake capture adapter; the smallest live probe uses a licensed interactive workstation and one operator-selected window only when necessary.

## Prerequisites

- A repository with a narrow capture adapter and tests
- TechSmith's official Snagit COM samples and guide pinned for reference
- Optional licensed Windows workstation with an interactive session
- Disposable local output directory, deadline, and artifact cleanup policy

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect local scripts, manifests, logs, and tests. Use `WebFetch` only for current primary TechSmith documentation. Use `Write` or `Edit` only after confirming the target repository file and approval boundary.

## Current Contract

- Keep COM creation behind one adapter so unit tests do not require Snagit.
- Load official enum definitions rather than scattering unexplained integers.
- Model `Capture()` as asynchronous and cover success, false result, timeout, and invalid output path.
- A live loop captures only an explicitly selected test window and never runs continuously.

## Licensing and Authentication

TechSmith desktop activation is not API authentication. Resolve individual sign-in versus business-key or approved offline activation before execution. Redact all keys, account identifiers, activation artifacts, and sensitive endpoint details.

## Instructions

1. Inspect repository conventions, existing adapter boundaries, test runner, fixtures, and output policy.
2. Copy or translate only the needed contracts from TechSmith's official sample; retain source attribution.
3. Write fake-adapter tests for enum mapping, configuration order, timeout, success checks, path containment, and cleanup.
4. Run lint and unit tests on every change without starting Snagit.
5. When a live probe is justified, confirm operator/window/destination, run once, and compare evidence with the fake contract.
6. Edit the adapter or tests from the observed mismatch, rerun, and remove disposable output.

## Approval Boundaries

Do not turn the development loop into a background screen recorder, poll the desktop indefinitely, or commit captured images and videos as fixtures.

## Output

Return changed files, offline test results, live-probe authorization/result, contract differences, artifact cleanup, and the next bounded experiment.

## Error Handling

| Condition | Response |
|---|---|
| Official sample differs from adapter | Update the adapter contract and add a regression test before another live probe. |
| No interactive workstation | Continue with fakes and mark live behavior unverified. |
| Capture timeout | Stop the COM operation and inspect state; do not loop forever. |
| Fixture contains sensitive pixels | Remove it from history and replace it with synthetic metadata. |

## Examples

The example below shows the minimum redacted evidence expected from a successful invocation of this operator workflow.

```text
iteration=7; offline_tests=18_pass; live_probe=one-window; output=deleted; contract_delta=none
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Official PowerShell samples](https://github.com/TechSmith/Snagit-COM-Samples/tree/main/PowerShell)
- [Snagit 2025 COM guide](https://assets.techsmith.com/Docs/Snagit-2025-COM-Server-Guide.pdf)
