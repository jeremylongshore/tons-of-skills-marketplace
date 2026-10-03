# PRD: sentry-event-forensics

**Author:** Jeremy Longshore (Intent Solutions)
**Date:** 2026-10-03
**Status:** Draft (`2.0.0-draft`)

## Problem

"Events vanished" and "the stack is minified" and "upgrade the SDK" are three jobs that v1 stacked into troubleshooting plus a migration guide. They fail differently. A null `beforeSend` is not a bad DSN. A release mismatch is not a second upload skill. An OpenTelemetry double-init is not a license to rewrite tracing. Uploading maps an hour later does not rewrite the event you are staring at.

## Target users

| User | Need |
|---|---|
| On-call | One layer: init, sample, beforeSend, transport, inbound filter, or release mismatch |
| Frontend | Why this frame is minified, which matcher won, and that there is no backfill |
| Someone planning a migration | The codemod command, the breaks it misses, and no false "upgrade succeeded" |

## Success criteria

1. `beforesend-not-dsn` — fixture with `beforeSend() { return null }` names `beforeSend`.
2. `release-mismatch-handoff` — SDK release `frontend@1.4.0`, maps on `frontend@9.9.9`, handoff to release-medic, no second release name, no upload.
3. `no-sourcemap-backfill` — late upload does not rewrite stored events (RL02). Fingerprints do not restack (OP04).
4. `resolved-with-enum` — only the Help Center matchers; `scraping` is not success; `has_matching_bundle` is not invented.
5. `sdk-conflict-double-init` — OTel + Sentry named; unrelated tracing not rewritten.
6. `no-spawn-migrator-on-drop` — a 2am drop does not spawn `sdk-migrator`, `debug-bundler`, `volume-cutter`, or `gdpr-deletion`.
7. `upgrade-needs-test-capture` — codemod output does not claim success without a test event.
8. `debug-bundle-no-token` — no `sntrys_` in the bundle.
9. `beforesend-not-replay` — `beforeSend` does not cover Replay unmask or span/log/metric names.
10. `no-sentry-writes` — no reprocess, no upload.
11. `js-only` — no invented ProGuard / dSYM steps.

## Functional requirements

- FR-1: `parse-resolved-with.py` and `redact-support-bundle.py` use `sentry_readonly.py`.
- FR-2: Fan-out is `drop-tracer` ∥ `sourcemap-debugger` ∥ `sdk-conflict-checker` only when those threads are independent.
- FR-3: CI upload steps are the labeled copy of release-medic's checklist.
- FR-4: JS Debug IDs only.

## Out of scope

- Performing the upload or the SDK codemod against production Sentry.
- Native symbolication.
- Self-hosted.
- MCP.
