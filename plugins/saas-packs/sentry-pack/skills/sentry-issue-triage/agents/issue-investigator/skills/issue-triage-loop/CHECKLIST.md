---
name: issue-triage-loop
description: |
  Severity, suspect release, and a postmortem skeleton for one Sentry issue.
  Not the inbound-filter matrix. Not a marketplace skill.
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Designed for Claude Code
tags: [sentry, nested, saas, checklist]
---

# issue-triage-loop

**Owner:** `sentry-issue-triage` → `issue-investigator`
**Not:** `noise-classifier` / `inbound-filter-matrix`. If the question is Ignore, Discard, or a health-check glob, stop and load that checklist instead.

## Checklist

1. Run `scripts/issue-context.py` on the issue JSON (pasted or read-only). Do not recompute severity.
2. Copy `severity`, `suspect_release`, `userCount`, `count`, and `timeline_timestamps` into the answer.
3. If `suspect_release` is null, write unknown. Do not pick a release from memory or from a nearby deploy.
4. Postmortem timeline uses only `timeline_timestamps`. No "about 10 minutes later".
5. Five whys stay empty unless the payload or a file the user opened states the cause.
6. Next check is one of: fingerprint-auditor, noise-classifier, perf-span-auditor, trace-bottleneck, log-correlator, or the symbolication handoff. Name which one and why.
7. Do not recommend a rate limit keyed on `environment`.
8. Do not call resolve, ignore, merge, or discard APIs.
9. Do not spawn `sdk-migrator`, `volume-cutter`, or `gdpr-deletion`.

## Output

Severity line, release line, timestamps used, next check, `writes: none`.

## Fail

Invented time, invented release, filter matrix pasted into this checklist, dollar figure, summed filtered+dropped.
