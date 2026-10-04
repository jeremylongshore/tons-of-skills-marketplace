---
name: sentry-release-medic
description: |
  Diagnose this Sentry deploy's artifacts, commits, and release health, and
  recommend the release, the upload, and the health read; does not create
  the release, upload maps, or record the deploy. Use when CI source maps
  fail, Debug IDs are missing, release health looks wrong, or GitHub Actions
  upload is broken.
  Trigger with "sentry github actions", "sentry release health",
  "source map upload", "debugId missing", "sentry-cli releases".
allowed-tools: Read, Grep, Bash(sentry-cli info:*), Bash(sentry-cli releases list:*), Bash(python3 "${CLAUDE_SKILL_DIR}/scripts/*"), Bash(bash "${CLAUDE_SKILL_DIR}/scripts/*")
argument-hint: "[pasted sentry-cli output, CI workflow file, or session query JSON]"
model: inherit
version: 2.0.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Designed for Claude Code
tags: [saas, sentry, release, ci, sourcemaps]
---

# Sentry Release Medic

Diagnose this deploy's artifacts, commits, and release health: the bytes
that run must be the bytes that were injected, uploaded, then deployed.
Treat a `debugId` grep of the built file, not a URL, as the source of truth
for "was it injected."

Recommend the fix. Do not call `sentry-cli releases` write commands, the
release-create API, or the upload API.

## Overview

Keep seed: `sentry-release-management`. Merged: `sentry-ci-integration` →
`sourcemap-uploader` / `ci-sourcemap-upload`; `sentry-deploy-integration` →
`release-finalizer` / `release-health`. Wrong-project uploads (SC05) stay
here. They are not an org-topology skill.

JavaScript Debug IDs only. Do not extend the grep into ProGuard or dSYM.

## Prerequisites

- SaaS. Self-hosted: stop. Do not invent a release pipeline for `sentry.conf`.
- Token scopes if a human later runs the CLI: `project:releases` and `org:read`.
  Check with `npx @sentry/cli info` or `sentry-cli info`. This skill does not
  mint a token.
- No token: advisory mode on a pasted `sentry-cli releases list` or workflow
  file. Do not guess an org slug or invent a release name.
- `python3` for `scripts/grep_debug_id.py` and `scripts/assess-session-stats.py`.
  `scripts/grep-debug-id.sh` is the same grep.

## Authentication

Advisory mode needs no token: it reads pasted CI output, workflow files, or
session query JSON. No command in this skill reads or requires a secret.

If a human later runs read-only commands against the Sentry API, that
command needs `SENTRY_AUTH_TOKEN` set in the shell environment with at
minimum the `project:releases` and `org:read` scopes (see
`references/ci-token-scopes.md`). Verify the scopes with `sentry-cli info`,
which reports the authenticated org and token scopes without printing the
token value. Never print or paste the token value in chat, logs, or this
skill's output.

## Instructions

Nested procedures are `CHECKLIST.md`. Read them. `skills:` on the agents is
empty so the marketplace does not grade these checklists.

Cross-skill calls are not proven. If an upload "succeeded" and frames are
still minified, Read the labeled copy:

`agents/sourcemap-uploader/skills/sourcemap-resolution/CHECKLIST.md`

Owner: forensics `sourcemap-debugger`. Do not restate `resolved_with` as a
second essay. Do not parse it by hand; forensics' `parse-resolved-with.py`
owns that parse. If that script is not on disk in the caller's tree, say so
and quote the copy's enum instead of inventing matchers.

### Step 1 — `sourcemap-uploader` (CI / inject / project)

Read `agents/sourcemap-uploader/skills/ci-sourcemap-upload/CHECKLIST.md`.

Order: build, inject, upload, deploy **those** files. Pin the action major.
`actions/checkout` `fetch-depth: 0` when commits must associate. One release
string shared by the SDK and the CLI. `--release` on `sourcemaps upload` does
not create the release.

Grep, do not debate the docs:

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/grep_debug_id.py" path/to/dist
# or: bash "${CLAUDE_SKILL_DIR}/scripts/grep-debug-id.sh" path/to/dist
```

Exit 0 is `PRESENT` (`debugId` in JS/HTML the browser will run). Exit 2 is
`ABSENT`. A `.map` that only has `debug_id` is still `ABSENT` for the running
bytes. The JSON cites both:

- Help Center: `getsentry/action-release@v3` with a `sourcemaps` path injects
  by default (CLI ≥ 2.17.0, bundler plugins ≥ 2.0.0).
- Blog "How to Fix Source Map Upload Errors": the GitHub Action and the
  Netlify plugin cannot inject Debug IDs.
- Actions doc: upload and release creation, after build and before deploy.
  It is not a tie-break.

Do not delete either citation. If `debugId` is absent, tell the user to run
`sentry-cli sourcemaps inject` or a current bundler plugin **before** upload,
then deploy those files. Re-check the action source at build time.

Monorepo (SC05): one `SENTRY_PROJECT` for every package is the bug. One upload
step per project, artifacts limited to that package's `dist`. A map in
project A does not symbolicate an event in project B. Do not invent a second
release name to paper over the wrong project.

### Step 2 — `release-finalizer` (finalize, deploy record, health)

Read `agents/release-finalizer/skills/release-health/CHECKLIST.md`.

Recommend: create the release (if commits must attach before the first event),
associate commits, finalize, record a deploy **with an environment**.
Environment-on-deploy is a tag, not a quota silo
(`references/environment-on-deploy.md`).

Health:

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/assess-session-stats.py" \
  --json sessions-query.json
```

`health_fine` is true only when `api_read` is true, the query is one project,
one environment and one release, the shape is not the 90-day group-by-release
cap, and `session.duration` is not requested. Session duration stopped
2023-01-12. The cap is 10,000 datapoints; 90 days grouped by release is at
most `floor(10000/91) = 109` releases. A truncated series is a false pass.
Do not mark health fine when the API was not read. Do not alert on session
duration.

Spawn `release-finalizer` when the user asks whether the release is healthy
or how to record the deploy. Do not spawn it to explain a minified stack
(that is Step 1 plus forensics).

### Recommend, do not apply

A bad release can be stopped with an inbound release filter. That filter is
Business/Enterprise, matches the full release string (glob, not SemVer), and
does nothing for events that omitted `release`. Print the string copied from
event JSON. Do not click the filter. Ignore still bills. Delete & Discard is
a different lever and is not this skill's button.

Uploading maps does not rewrite events already stored.

## Output

Return one advisory report, every line populated from the current deploy's
actual evidence (grep result, pasted JSON, workflow file) — never from
memory of a past session. Omit no line; state "not recorded" or "none"
rather than dropping a line that has no finding.

```
Mode: advisory | live
Release id (one): SDK_RELEASE == CLI_RELEASE, or MISMATCH: SDK_RELEASE vs MAPS_RELEASE
Debug ID grep: PRESENT | ABSENT
Citations: help center + blog (both)
Missing step: inject | upload | fetch-depth | project | none
Deploy environment: ENV_NAME or "not recorded"
Health: not fine | fine (state why the script said so)
Session duration: discontinued 2023-01-12  # fixed historical date, not a staleness claim
Wrote to Sentry: no
```

## Error Handling

| Error | Cause | Solution |
|---|---|---|
| No token | Cannot list releases | Advisory on pasted `sentry-cli releases list`. No guessed org. |
| Conflicting inject docs | Help Center vs blog | Grep. Cite both. Do not pick a winner. |
| Maps after the app is serving | Wrong bytes, or late upload | Inject, upload, deploy those files. No backfill. |
| Health looks fine on 90 days of every release | 10k cap | Run `assess-session-stats.py`. Refuse "fine." |
| `session.duration` chart empty | Stopped 2023-01-12 | Say so. Do not alert on it. |
| Workflow uploads every package to `web` | SC05 | Name the missing per-project step. Keep the release id. |

## Examples

### Example 1 — CI emits maps, no CLI and no bundler plugin

SDK `release: "frontend@1.4.2"`. Workflow builds `dist/` and deploys it.
Uploader names the missing upload step and says the release id must be
`frontend@1.4.2`. It does not invent `frontend@1.4.2-sourcemaps`.

### Example 2 — `debugId` absent

Fixture `references/fixtures/app-without-debugid.js` → verdict `ABSENT`,
both citations, next step inject-then-deploy. The sibling `.map` with
`debug_id` does not flip the verdict.

### Example 3 — "Is crash-free fine?"

Fixture `references/fixtures/session-query-90d.json` includes
`session.duration`, `statsPeriod: 90d`, `groupBy: [release]`,
`groups_returned: 109`. Script: `health_fine: false`, max groups 109,
duration discontinued. Do not say the release is healthy.

## Resources

- `references/action-release-conflict.md` — both citations, grep rule.
- `references/session-stats-limits.md` — 10k cap, duration stop date.
- `references/environment-on-deploy.md` — environment string on the deploy.
- `references/ci-token-scopes.md` — `project:releases`, `org:read`.
- `references/fixtures/`.
- Sessions API: https://docs.sentry.io/api/releases/retrieve-release-health-session-statistics/
- CLI upload: https://docs.sentry.io/platforms/javascript/sourcemaps/uploading/cli/
- Debug IDs: https://docs.sentry.io/platforms/javascript/sourcemaps/troubleshooting_js/debug-ids/
