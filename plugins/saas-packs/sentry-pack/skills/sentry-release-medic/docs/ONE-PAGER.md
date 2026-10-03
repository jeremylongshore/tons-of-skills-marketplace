# ONE-PAGER: sentry-release-medic

**Version:** 2.0.0-draft
**Date:** 2026-10-03

## Who

Whoever owns the workflow that builds, uploads, and deploys a JavaScript app, and whoever is about to gate a merge on crash-free rate.

## What

The missing step (inject, upload, fetch-depth, or project), one release id, a Debug ID grep with both citations, and a health verdict the session-stats script is willing to call fine.

## When

"Sentry GitHub Actions," "source map upload," "debugId missing," "is this release healthy?" Not when the only question is an error `beforeSend`.

## Where

The built `dist/` (or the file that will be served) and the workflow YAML. Pasted `sentry-cli releases list` if there is no token. SaaS. Not self-hosted.

## Why

Minified stacks and fake-green crash-free rates come from deploying bytes that were never injected, from a 10k-row sessions query, and from docs that disagree. The artifact and the API limits are checkable. The docs are not a tie-break.

## Stack

- Router: `SKILL.md`
- Scripts: `grep_debug_id.py`, `grep-debug-id.sh`, `assess-session-stats.py`
- Agents: `sourcemap-uploader`, `release-finalizer`
- Checklists: `ci-sourcemap-upload` (canonical), `release-health`, labeled copy of `sourcemap-resolution`
- References: action-release conflict, session-stats limits, environment-on-deploy, token scopes

## Do not

Pick one `action-release` URL. Treat a source map's `debug_id` as proof the JS was injected. Invent a second release name. Mark health fine on a capped or unread query. Alert on session duration. Upload or create the release from this skill. Invent ProGuard steps.
