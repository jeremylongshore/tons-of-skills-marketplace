---
name: sentry-local-dev-loop
description: |
  Detect calls to the cut sentry-local-dev-loop skill and explain why it was cut (sentry-pack 2.0.0, disposition: Cut).
  Use when a saved prompt still names it. Trigger with "sentry-local-dev-loop" or "/sentry-local-dev-loop".
argument-hint: "[the question you used to ask sentry-local-dev-loop]"
allowed-tools: Read
version: 2.0.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Designed for Claude Code
tags: [sentry, deprecated, redirect, v1-compat]
---

# sentry-local-dev-loop (retired in sentry-pack 2.0.0)

> [!WARNING]
> **Retired.** Disposition: **Cut**. Replacement: no replacement (cut).

## Overview

Redirect saved workflows that still name `sentry-local-dev-loop` to the right sentry-pack 2.0.0
skill.

## What changed in 2.0.0

sentry-pack 1.x was 30 tutorial skills organized around SDK features. Version 2.0.0 replaces them
with five operational skills organized around the jobs operators actually bring to Sentry: finding
quota burn (`sentry-quota-leak-hunter`), explaining a missing or wrong event
(`sentry-event-forensics`), repairing a release or sourcemap (`sentry-release-medic`), triaging an
issue (`sentry-issue-triage`), and proving PII scrubbing (`sentry-pii-scrub-enforcer`). Each v1 slug
was kept, merged into one of those five, or cut. All five are advisory: they read pasted config and
event JSON and recommend changes; they do not change Sentry.

## Prerequisites

None. Authentication: none required. This redirect makes no Sentry calls and needs no DSN or token.

## Instructions

1. Stop using `sentry-local-dev-loop`; it no longer contains instructions.
2. Tell the user it was cut: Dev DSN and Spotlight setup are dropped; debug-mode steps live in event-forensics.
3. If part of the request maps to a v2 skill, name that skill; otherwise drop the workflow.

## Output

A short message stating the skill was cut and why, plus the v2 skill that covers any part of the
request. No Sentry data is read or changed.

## Error Handling

If the request does not fit the replacement, say so and stop. Do not recreate the retired v1
tutorial.

## Examples

A saved prompt that says `/sentry-local-dev-loop` gets this answer: the skill was cut. Dev DSN and
Spotlight setup are dropped; debug-mode steps live in event-forensics. If the question is really
about quota, event loss, releases, triage or PII, use that v2 skill:

| If the request is about | Use |
|---|---|
| Quota burn, sampling, rate limits | `sentry-quota-leak-hunter` |
| A missing, dropped or wrong event | `sentry-event-forensics` |
| Releases, sourcemaps, CI upload | `sentry-release-medic` |
| Triage, root cause, log correlation | `sentry-issue-triage` |
| PII scrubbing and project standards | `sentry-pii-scrub-enforcer` |

## Resources

- Migration map: `../../000-docs/phase0-kill-list.md` (section 3). Use Read to open it when the replacement is unclear.
- Decision record: `../../000-docs/001-AT-ADEC-sentry-v2-rebuild-decisions.md`
- This redirect is removed in a later release, after saved workflows have migrated.
