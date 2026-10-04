---
name: sentry-event-forensics
description: |
  Diagnose and detect why a Sentry event, source map, or trace is missing, or
  scope an SDK upgrade or vendor migration. Use when events are missing,
  maps fail to resolve, SDKs conflict, or switching vendors.
  Trigger with "sentry events missing", "source maps not resolving",
  "sentry debug".
allowed-tools: Read, Bash(sentry-cli info:*), Bash(python3 "${CLAUDE_SKILL_DIR}/scripts/*")
argument-hint: "[pasted event JSON, init snippet, or sentry-cli output]"
version: 2.0.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Designed for Claude Code
tags: [saas, sentry, forensics, sdk, sourcemaps]
---

# Sentry Event Forensics

Diagnose one cause on one layer — init, sample, `beforeSend`, transport,
inbound filter, release mismatch, or SDK conflict — instead of "turn on debug
and look."

`sdk-migrator` and `debug-bundler` stay nested and **off** the default fan-out.
A 2am drop does not get an upgrade plan or a support bundle unless the user
asked for that phase.

Symbolication scope is **JavaScript Debug IDs only**. ProGuard, dSYM, and
other native artifacts are named and unspecified. Do not invent those steps.

## Overview

Keep seed: `sentry-advanced-troubleshooting`. Merged under this parent:
`sentry-debug-bundle` → `debug-bundler`, `sentry-upgrade-migration` and
`sentry-migration-deep-dive` → `sdk-migrator`. v1 bodies are not copied.

Event-side `resolved_with` and `debug_meta` live here. The CI inject/upload
procedure is owned by `sentry-release-medic` / `sourcemap-uploader`. Until
cross-skill calls are proven, Read the labeled copy. Do not restate it as a
second procedure and do not edit it into one.

## Prerequisites

- SaaS. Self-hosted: say the SaaS drop model may not match and stop.
- Advisory: pasted event JSON, init snippet, or `sentry-cli` text. No token
  required. Do not guess an event id or org slug.
- `python3` for `scripts/parse-resolved-with.py` and
  `scripts/redact-support-bundle.py`. Both import `sentry_readonly` and refuse
  writes.

## Authentication

Advisory only: this skill works on pasted event JSON, an init snippet, or
`sentry-cli` text, with no token required. If a human later runs read-only
`sentry-cli` commands, scope the token to `project:read` and set it as the
`SENTRY_AUTH_TOKEN` environment variable — never print it or paste it into
chat. `redact-support-bundle.py` strips any `sntrys_`-prefixed token found in
a draft bundle.

## Instructions

Nested procedures are `CHECKLIST.md`. Read them. Do not look for a nested
`SKILL.md`.

1. Check the pasted input to isolate which layer is broken before deciding
   whether to fan out (Step 1).
2. Run the matching script or nested checklist for that layer (Steps 2-6).
3. Verify the evidence names one cause and one owner for any handoff.
4. Report the result in the `## Output` format below.

### Step 1: Decide whether to fan out

Spawn in parallel when the user says events are missing **and** maps are
wrong **and** another SDK is in the process:

- `drop-tracer` — `agents/drop-tracer/skills/silent-drop-diagnosis/CHECKLIST.md`
- `sourcemap-debugger` — `agents/sourcemap-debugger/skills/sourcemap-resolution/CHECKLIST.md`
- `sdk-conflict-checker` — `agents/sdk-conflict-checker/skills/sdk-conflict-isolation/CHECKLIST.md`

If the user already grepped `debugId` and it is absent, stay on the parent:
one paragraph, "deployed bytes were not injected," no swarm. Point at
release-medic for the inject. Do not grow a second Debug ID essay.

If only one layer is in play, spawn only that agent.

### Step 2: Do not spawn on a plain diagnosis

- `sdk-migrator` (`sdk-major-upgrade`, `vendor-cutover`) — only when the user
  asked to upgrade the SDK or cut over from Rollbar/Bugsnag.
- `debug-bundler` — only when the user asked for a support bundle.
- `volume-cutter` and `gdpr-deletion` are not this skill. Do not spawn them
  from a missing-event page.

### Step 3: Check source maps

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/parse-resolved-with.py" \
  --json event.json --maps-release "frontend@9.9.9"
```

The script prints per-frame `resolved_with` against the known enum
(`debug-id`, `url`, `index`, `release`, `release-old`, `scraping`, `unknown`).
It sets `has_matching_bundle` to null. It sets `not_retroactive` true.
A release mismatch sets `handoff` to release-medic `sourcemap-uploader`.

When the cause is "release id A, maps on release B," Read the labeled copy:

`agents/sourcemap-debugger/skills/ci-sourcemap-upload/CHECKLIST.md`

Owner: `sourcemap-uploader`. Do not invent a second release name. Do not
upload. Uploading maps later does not rewrite events already stored.

`has debug_meta` ≠ `has a matching bundle`. `resolved_with=scraping` is not
a Debug ID success. `resolved_with=release-old` is not evidence the upload
just applied.

### Step 4: Separate `beforeSend` from Replay

A `beforeSend` that returns null drops error events in the client. It does
not cover Session Replay unmask, and it does not scrub span, log, or metric
names. If the user thinks `beforeSend` fixed privacy, hand that to
`sentry-pii-scrub-enforcer` / `replay-privacy` without copying that checklist.
If `beforeSend` returns null for every event, the cause is `beforeSend`, not
the DSN.

### Step 5: Run the migration phase (only when asked)

`sdk-migrator` emits the JS v7→v8 codemod command and the breaks the codemod
misses, or the Python 1.x→2.x breaks, or the vendor parallel-run sequence.
It does **not** claim the upgrade succeeded without a test capture. It does
not run the codemod against the repo unless the user asked to edit code, and
it still does not tell Sentry the upgrade worked.

### Step 6: Build a support bundle (only when asked)

`debug-bundler` collects SDK version, init snippet, DSN **host** (not a raw
auth token), `sentry-cli info` with secrets removed, and whether a test
capture was attempted. Run:

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/redact-support-bundle.py" --json bundle.txt
```

Output must not contain `sntrys_`.

## Output

```
Cause: SINGLE_CAUSE
Layer: init | sample | beforeSend | transport | inbound filter | release mismatch | sdk conflict | migration | bundle
Evidence: EVENT_ID_OR_SCRIPT_FIELD_OR_INIT_LINE
Handoff: OWNER_AGENT_OR_NONE
Backfill: no — stored events are not rewritten
Wrote to Sentry: no
Agents spawned: AGENT_LIST
```

Pick one cause. If two threads return evidence, say which one explains the
missing event and which is a second problem.

## Error Handling

| Error | Cause | Solution |
|---|---|---|
| `beforeSend() { return null }` | User blames the DSN | Name `beforeSend`. Do not blame the DSN. |
| Maps uploaded an hour later | Expectation of reprocessing | Say Sentry does not reprocess. New events only. |
| OTel and Sentry both init | Double transport / double spans | Name the double-init. Do not rewrite unrelated tracing. |
| `sntrys_` in a bundle draft | Token copied into notes | Run `redact-support-bundle.py`. Fail if it remains. |
| Native stack (ProGuard / dSYM) | Out of JS scope | Say unspecified. Do not invent a mapping file. |
| Self-hosted | Out of scope | Stop. |

## Examples

### Example 1 — No events, `beforeSend` returns null

Fixture `references/fixtures/event-beforesend-null.json`. Cause: `beforeSend`.
Layer: `beforeSend`. Not the DSN. Do not spawn `sdk-migrator`.

### Example 2 — Maps on release `frontend@9.9.9`, SDK reports `frontend@1.4.0`

Fixture `references/fixtures/event-release-mismatch.json` plus
`--maps-release frontend@9.9.9`. Script sets `release_mismatch`. Handoff:
release-medic `sourcemap-uploader` via the labeled `ci-sourcemap-upload` copy.
Do not upload. Do not claim a backfill.

### Example 3 — Readable frame is `scraping`

Fixture `references/fixtures/event-resolved-with.json`. `debug-id` on one
frame does not mean the pipeline is healthy. Call out `scraping`. Do not
tell the user to publish maps on the CDN.

## Resources

- `references/events-not-appearing.md` — layer order.
- `references/resolved-with-enum.md` — matchers the script accepts.
- `references/sdk-conflicts.md` — OTel / double init.
- `references/known-pitfalls.md` — DSN typo, missing `flush()`, CORS, null `beforeSend`.
- `references/fixtures/`.
- Help Center resolved_with: https://www.sentry.help/en/articles/13964309-how-were-my-source-maps-resolved
- Help Center no reprocessing: https://www.sentry.help/en/articles/13965232-javascript-how-do-i-verify-debug-ids-for-source-maps
- JS v7→v8: https://docs.sentry.io/platforms/javascript/migration/v7-to-v8/
- Python 1.x→2.x: https://docs.sentry.io/platforms/python/migration/1.x-to-2.x/
