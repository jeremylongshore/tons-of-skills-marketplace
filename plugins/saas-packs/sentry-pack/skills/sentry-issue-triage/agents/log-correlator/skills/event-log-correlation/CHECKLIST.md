---
name: event-log-correlation
description: |
  Tie one Sentry event id to a log query, or say the code never writes it.
  Not an APM install guide. Not a marketplace skill.
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Designed for Claude Code
tags: [sentry, nested, saas, checklist]
---

# event-log-correlation

**Owner:** `sentry-issue-triage` → `log-correlator`

## Procedure

1. Take `event_id` from the event JSON. Do not invent one.
2. Run `scripts/find-event-id-log.py --root <repo the user named> --event-id <id>`.
3. If `verdict` is `log query possible`, return `query` unchanged (it already contains the id) and cite one hit path. Do not widen into a metrics platform.
4. If `verdict` is `codebase never writes it`, say that sentence. The fix, if they want one later, is to log `event_id` from the SDK scope. Do not implement it unless they ask, and do not install Datadog.
5. `references` may mention that APM tours existed in v1 `sentry-observability`. They are not steps.

## Output

The query or the explicit miss. `datadog_install: false`. `writes: none`.

## Fail

A query that omits the event id. Claiming a log line exists when the script found none. Recommending a vendor install as the correlation path.
