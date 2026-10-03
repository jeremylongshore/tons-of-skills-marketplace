# PRD: sentry-release-medic

**Author:** Jeremy Longshore (Intent Solutions)
**Date:** 2026-10-03
**Status:** Draft (`2.0.0-draft`)

## Problem

A deploy can upload source maps for a different build than the one users run, under a different release id, to the wrong Sentry project, and still look green. Docs disagree on whether `getsentry/action-release` injects Debug IDs. Crash-free rate over 90 days of every release can omit the noisy one because the sessions API caps at 10,000 datapoints. Session duration has been dead since 2023-01-12 and people still alert on it.

## Target users

| User | Need |
|---|---|
| Frontend / CI owner | The missing inject or upload step, for the release id the SDK already uses |
| Release manager | Commits actually associated, deploy recorded with an environment, health not declared fine off a capped query |
| On-call looking at a minified issue | A handoff to forensics for `resolved_with`, not a second essay, and no promise of backfill |

## Success criteria

1. `names-missing-upload-step` — maps exist on disk, CI has no CLI or bundler plugin, the release id is the SDK's, not a new name.
2. `release-id-alignment` — SDK release and upload release must match.
3. `debugid-grep-beats-docs` — `ABSENT` when the JS has no `debugId`, even if a `.map` has `debug_id`. Both citations present.
4. `finalizer-reads-health` — no "fine" without `api_read: true`.
5. `session-stats-cap` — 90d groupBy release is not fine; max groups called out as 109; duration stop date stated.
6. `advisory-without-token` — no guessed org slug.
7. `no-sourcemap-backfill` — late upload does not rewrite stored events.
8. `wrong-project-monorepo` — one `SENTRY_PROJECT` for every package is named (SC05).
9. `no-sentry-writes` — no release create, no upload, no deploy POST.
10. `js-only` — no ProGuard steps.

## Functional requirements

- FR-1: `grep_debug_id.py` / `grep-debug-id.sh` is the inject check. Both doc URLs stay.
- FR-2: `assess-session-stats.py` owns `health_fine`.
- FR-3: `sourcemap-resolution` under this skill is a labeled copy. Owner is forensics `sourcemap-debugger`.
- FR-4: Recommend a release filter; do not apply it. Business/Enterprise, full string.

## Out of scope

- Executing `sentry-cli` writes.
- Native artifacts.
- Self-hosted.
- Per-environment rate limits (quota).
- MCP.
