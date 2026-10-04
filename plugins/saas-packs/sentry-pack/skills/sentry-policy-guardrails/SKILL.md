---
name: sentry-policy-guardrails
description: |
  Route the retired sentry-policy-guardrails skill to sentry-pii-scrub-enforcer, which now owns this job (sentry-pack 2.0.0, disposition: Merge).
  Use when a saved prompt or workflow still names sentry-policy-guardrails. Trigger with "sentry-policy-guardrails" or "/sentry-policy-guardrails".
argument-hint: "[the question you used to ask sentry-policy-guardrails]"
allowed-tools: Read
version: 2.0.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Designed for Claude Code
tags: [sentry, deprecated, redirect, v1-compat]
---

# sentry-policy-guardrails (retired in sentry-pack 2.0.0)

> [!WARNING]
> **Retired.** Disposition: **Merge**. Replacement: `sentry-pii-scrub-enforcer`.

## Overview

Redirect saved workflows that still name `sentry-policy-guardrails` to the right sentry-pack 2.0.0
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

1. Stop using `sentry-policy-guardrails`; it no longer contains instructions.
2. Invoke `sentry-pii-scrub-enforcer` instead. It handles this job: prove PII scrubbing works and catch project-standard drift.
3. Update the saved prompt or workflow to name `sentry-pii-scrub-enforcer` so this redirect is no longer needed.
4. Keep the original question intact when you switch; `sentry-pii-scrub-enforcer` expects the same symptoms, config or event JSON the old prompt supplied.

## Output

A short redirect message that names `sentry-pii-scrub-enforcer` as the replacement, states the
reason it moved, and gives the updated prompt to use. No Sentry data is read or changed.

## Error Handling

If the request does not fit the replacement, say so and stop. Do not recreate the retired v1
tutorial.

## Examples

A saved prompt that says `/sentry-policy-guardrails` becomes `/sentry-pii-scrub-enforcer` with the
same question. Reason for the move: Project-standard drift checks fold into scrub-enforcer agents.

## Resources

- Migration map: `../../000-docs/phase0-kill-list.md` (section 3). Use Read to open it when the replacement is unclear.
- Decision record: `../../000-docs/001-AT-ADEC-sentry-v2-rebuild-decisions.md`
- This redirect is removed in a later release, after saved workflows have migrated.
