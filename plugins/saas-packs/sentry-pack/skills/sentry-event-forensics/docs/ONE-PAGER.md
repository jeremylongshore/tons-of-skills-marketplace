# ONE-PAGER: sentry-event-forensics

**Version:** 2.0.0-draft
**Date:** 2026-10-03

## Who

On-call debugging a missing event or a minified frame. A developer planning an SDK major or a Rollbar/Bugsnag exit.

## What

One layer where the event died, or a migration sequence that does not claim success early. For maps: which matcher won, and a handoff when the release ids differ.

## When

"Sentry events missing," "source maps not resolving," "SDK conflict." Upgrade and vendor cutover only when those words are the ask. Not on every drop.

## Where

Pasted event JSON, init snippet, or repo. SaaS semantics. Not self-hosted sizing.

## Why

The usual wrong answers (bad DSN, re-upload the maps, upgrade the SDK, turn on debug) hide the layer that actually dropped the event, and they promise a backfill Sentry does not do.

## Stack

- Router: `SKILL.md`
- Scripts: `parse-resolved-with.py`, `redact-support-bundle.py`
- Agents: `drop-tracer`, `sourcemap-debugger`, `sdk-conflict-checker`; `sdk-migrator` and `debug-bundler` off by default
- Checklists as `CHECKLIST.md`
- Labeled copy of `ci-sourcemap-upload`

## Do not

Blame the DSN for a null `beforeSend`. Claim maps rewrite history. Spawn an upgrade on a drop. Print `sntrys_`. Invent native symbolication. Write to Sentry.
