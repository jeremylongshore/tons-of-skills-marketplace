---
title: "Next.js 16 Hustle: Rate Limits and Admin Fail-Closed"
description: "Hustle shipped seven P0 security PRs in one day: SQLite rate limits, fail-closed admin, AUTH_URL fix, debug routes deleted. What landed and what broke."
date: "2026-09-18"
tags: ["nextjs", "security", "production", "audit", "claude-code"]
featured: false
canonical: "https://startaitools.com/posts/seven-merges-one-audit-zero-leaks/"
---
Seven pull requests merged into hustle on a single day. Forty-one commits across the repo, plus a 968 line operator audit (doc 286) closed into the main branch through PR 64. The P0 security cluster that had been open since the access-control review finally shipped: rate limits on the auth endpoints, a fail-closed admin allow-list, a public-origin fix on the AUTH_URL, npm audit patches on every critical and high CVE, and three debug API routes deleted from production entirely. Two hundred and four lines gone.

The whole day's hustle work ran under Claude Opus 5 in the Claude Code CLI. Zero operator course-corrections. Sixteen errors hit and self-recovered. That ratio is high, not the operator having to step in. The model made its own messes and cleaned them up.

## SQLite rate limits on the auth surface

PR 60 added SQLite backed rate limits to login, signup, password reset, and PIN endpoints. The implementation reads from the existing `/data/hustle.db` file through Drizzle, so no new infrastructure. A request that exceeds the threshold returns a 429 and increments a counter in a `rate_limit_attempts` table keyed by IP and endpoint. Same table format for all four endpoints, one helper function. The thresholds are conservative (login at 5 per minute per IP, signup at 3) and tunable per endpoint through environment variables.

The reason it is SQLite and not Redis: hustle has no Redis. It runs as one Next.js 16 container talking to one SQLite file. Adding Redis would have meant a new service, new backup story, new deploy step. A table with an index on `(ip, endpoint, created_at)` and a periodic prune job does the same job in 80 lines of code, and it shares the existing backup story that borg is already taking off the volume every night.

## Fail-closed admin and the debug route deletion

PR 62 was the day. Two holes closed.

The first: the admin tools had a "fail open" default. If `ADMIN_USER_IDS` was unset or empty, the previous code let any authenticated user hit admin endpoints like `replay-events`. The new code reads the env var, parses it as a comma-separated list of user IDs, and on empty list returns 403. There is no implicit admin. The fix is a 12 line change but it took the model three iterations to get the precedence right inside the middleware chain, because middleware auth happens before route auth in Next.js 16 and the order of checks matters.

The second: three API routes under `/api/debug/{auth-state,biometrics,workout-logs}` previously let any signed-in user read another family's athlete records. They were development scaffolding that should never have shipped. They were deleted entirely in the same PR. Five routes in total came out, including `/api/hello` and `/api/test-post`. 204 lines gone; if a developer needs them back for local debugging, they live in git history.

After deploy I ran `ls /app/.next/server/app/api/debug` on the live container and got "No such file or directory". That was the receipt.

## The AUTH_URL that pointed at 0.0.0.0

PR 63. Auth.js was emitting callback URLs starting with `https://0.0.0.0:8084` because `AUTH_URL` was set to the local bind address instead of the public origin. The session callbacks worked (the JWT round-tripped fine) but the URLs in email links and OAuth redirects resolved to a hostname that does not exist on the public internet. The fix sets `AUTH_URL` to `https://hustlestats.io` (with `AUTH_TRUST_HOST=true` for the Caddy terminated TLS case). One env var, one config file. The model caught this by reading through the email transport logs and noticing the recipient-facing URLs contained the bind address.

## npm audit across the dependency tree

PR 61. Next 16.2.1 to 16.3.5, Auth.js 5.0.0-beta.31 to 5.0.0-beta.32, and the rest. Every critical and high CVE that `npm audit` reported got patched. The `package-lock.json` diff was the largest single change in the PR. There were no breaking API changes between 16.2.1 and 16.3.5 that affected hustle's usage, and the Auth.js beta bump only changed one default around session token rotation that we already disabled. Verification was the existing E2E suite (87 tests) and a manual login round-trip.

## The 286 audit

PR 64 landed a 968 line operator audit document, `000-docs/286-AA-AUDT-appaudit-devops-playbook.md`, written specifically for a new collaborator named Ravi. Section 1 is the system in five minutes (one Next.js app, one Docker container, one SQLite file, Caddy in front). Section 8 is the access control posture before and after the day's PRs. The doc names what shipped, what is still open, and what is actively dangerous.

Three risks from section 1, before the day's work closed any:

1. Access control had two holes. Both closed in PR 62.
2. AI features were dead in production (no `ANTHROPIC_API_KEY` in the env). Still dead. Documented as known.
3. The product handles 13 to 18 year olds' biometric and workout data, and the safety or consent foundation (doc 285) is not built yet. Doc 287 is the design draft for counsel, but it is not merged. This is the open one.

PR 65 refreshed the 286 status lines after deploy, since several lines from the pre-deploy snapshot were already stale by the time the audit merged.

## The 287 design

Doc 287, parent consent records and athlete sub-accounts, went 171 lines. Draft state, not merged, queued for counsel. It addresses the third risk from 286 directly. The work day did not solve the problem, it produced the artifact that lets the legal conversation start. Hustle has 3 user accounts, 0 athletes, 0 games, 0 workspaces. The code is far ahead of the usage. Doc 287 exists so that when the first athlete account gets created, the consent foundation is the first thing built, not an afterthought.

## What broke along the way

The release-changelog GitHub Actions job crashed with exit code 128 on the first attempt. The previous-release tag lookup failed. PR `fa91f1cb fix(ci): find the previous release tag reliably so Release stops failing on main` fixed it. The fix uses `git describe --tags --abbrev=0` against the main branch ref instead of trusting a workflow context variable that does not always populate.

A `git mv 000-docs/262-MS-archive 000-docs/262-MS-archive/262-MS-archive` died with "fatal: can not move directory into itself". The doc-filing archive move tried to nest the directory inside itself. The recovery was to split the move: `git mv 000-docs/262-MS-archive/000-INDEX.md 000-docs/000-INDEX.md` first, then `mkdir -p` the destination. The split worked. The remaining files moved cleanly.

`python3 /home/jeremy/000-projects/hustle/scripts/check_resend_secrets.py` returned `[Errno 2] No such file or directory`. The actual file is `check-resend-secrets.py` (kebab-case, not snake_case). One character correction. The Bash tool's `cp` and `mv` aliases both had prompted for confirmation by the time I noticed. The `\command` bypass kept things moving.

## intent-outreach

The DealMachine plan got retargeted. The addendum that captures residential data fields (address, parcel ID, owner-occupied flag) for skip-trace enrichment downstream moved from Twenty to ERPNext as the data substrate, because the broader Twenty to ERPNext migration is underway and writing skip-trace fields into a system that is being deprecated would have been a re-do. Two commits, both docs. The Twenty side now reads as historical context rather than the implementation target.

## Also shipped

Doc 287 itself (the consent design draft) is the most important artifact of the day that did not become a merge. The doc-filing archive reorg settled (the 262-MS move finished), and `bd init` stood up beads in hustle for tracking the residual work that survived the P0 cluster.

A small billing refactor (commit `105ce5cd`) derived UI plan limits from the enforced plan-mapping table, so the same numbers live in one place instead of drifting between the UI tier card and the server-side enforcement. That was a quiet fix for a quiet bug. The next person who changes a plan limit changes it once.

Hustle's next move is the consent foundation. The 286 audit names it, 287 sketches it, counsel has to bless it. Until then, athlete accounts stay unbuilt on purpose. The "purpose" part is the change from earlier in the year, when the data model could have absorbed athletes without the foundation in place. The system now refuses to be the kind of app that lets a 14 year old's workout log leak through a debug route.

## Related Posts

- [IRSB Four Releases in One Day, Perception Topic Watchlist, and Hustle Session Cookies](https://startaitools.com/posts/irsb-four-releases-one-day-perception-watchlist-hustle-cookies/)
- [Hardening a Marketplace in One Day](https://startaitools.com/posts/hardening-a-marketplace-in-one-day/)
- [Hustle E2E Stabilization Sprint and Bounty Tracker Init](https://startaitools.com/posts/hustle-e2e-stabilization-sprint-bounty-tracker-init/)
