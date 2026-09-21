---
title: "Hustle P1: COPPA Delete, Cosign Slice 1, SQLite Race"
description: "SQLite PRAGMA busy_timeout fixed a Next build race widened by migration 0005; same day shipped parent delete plus export (COPPA) and per-signer co-signatures."
date: "2026-09-19"
tags: ["hustle", "verified-stats", "privacy", "coppa", "release-cadence", "sqlite"]
featured: false
canonical: "https://startaitools.com/posts/hustle-p1-cluster-account-delete-cosign/"
---
Hustle closed its P1 cluster in one working day. PR #66, PR #69, and the named-co-signatures commit shipped within twelve hours of each other. Three release tags followed (v2.3.0, v3.0.0, v3.1.0). The cadence is what the work looks like when the bead hierarchy is honest and every child ships with its own test suite.

PR #66 is the unglamorous one. Fifty-eight query-layer functions gated to athlete ownership. Same schema, same routes.

The work was moving `WHERE athleteId = ?` checks into the helper layer so every call site stops needing to remember. Before the patch, the helper returned rows for any athlete id passed to it; the gating lived at the route handler, where it could be forgotten. After, the helper itself refuses to scope a query without an `athleteIds` array that the caller provides. Each function reads `req.session.parentId`, fetches the parent's athlete list once, and threads it through.

The P1 status reflects how much blast radius a missed check has in a parent-of-N product. One parent id is a global key for kids, schedules, games, biometrics, journal entries. One missed `AND` anywhere in the query layer hands over one child's full history to the caller. The diff is mechanical; the verification was the discipline.

Fifty-eight is a lot of functions to retest. The trick was keeping the existing 74-file unit suite green while the helper gained its ownership guard. It did, and nothing else did, and that is the result that ships. The new tests live in `query-ownership.test.ts`; each function gets a "passes with correct parent", "fails with wrong parent", and "fails with empty athlete list" triple.

PR #69 is the larger story. Account deletion plus full data export. App Store 5.1.1(v) requires in-app deletion; COPPA and parent-review rights require both deletion and access.

The shape: POST /api/account/delete re-authenticates with the password, requires the user to type DELETE, runs one SQLite transaction with `ON DELETE CASCADE` for the user, every athlete, and every athlete-scoped row.

The catch: cascade cannot reach everything. Email-keyed verification tokens, the waitlist entry, and `workspaceMember.addedBy` rows in other families' workspaces need explicit deletes. `addedBy` is `NOT NULL` with `ON DELETE NO ACTION`, so the user delete would have blocked silently mid-transaction; the fix was to re-attribute those rows to that workspace's owner before the cascade ran. The re-attribution query is a single `UPDATE workspaceMember SET addedBy = ? WHERE addedBy = ?` per workspace where the deleted parent had invited someone.

Uploaded files (`{userId}/...`) are removed after commit through a new `rm` helper that refuses paths outside `STORAGE_ROOT` (the helper is the kind of thing that gets asked about in code review, so the test covers an attempted traversal with `../../etc/passwd`). A live Stripe subscription blocks the whole thing with a 409 until canceled.

Rate-limit math is 5 deletions per 15 minutes per user and 10 exports per hour, both enforced at the route layer in front of the auth check. GET /api/account/export is the read twin: one JSON download with everything the parent owns, minus the password hash, the PIN hash, and Stripe IDs. The export is shaped as `{ user, athletes: [...], games: [...], biometrics: [...], journal: [...], dreamGym: [...], schedules: [...], assessments: [...], workspaces: [...] }` so a parent can hand the file to a school administrator and have the proof-of-data conversation. A receipt email follows every deletion with a timestamp and a one-line reason.

Then the bug underneath it. The "Yes, Delete Everything" button in Settings had no click handler. None. The UI rendered for months with a real-looking button that called nothing.

The commit wires it to ask for the password plus typed DELETE, calls the API, and signs out. A new "Download my data" card calls the export. The original button was a placeholder I never closed out; that is the lesson to write down. A delete button with no handler is worse than a missing button, because it teaches users that the affordance exists and is broken.

Named parent co-signatures slice 1 lands the same day. The verified-stats differentiator for recruiters used to be a bare boolean: was this game verified? It could not answer who signed it, or whether a coach could add a second signature.

The new `gameVerification` table (migration 0005) stores one row per signer with role (parent or coach), display name, signer user id (null for coaches, who have no account), method (pin or link), and timestamp. Rows cascade on game delete. Migration 0005 backfills every already-verified game with a parent/pin signature named from the owning parent's profile.

`verifyGameAdmin` now writes the signature row and the denormalized flag in one transaction and throws `AlreadyVerifiedError` when this parent has already signed that game. POST /api/verify returns the signature and answers "already verified" per signer. The old game-level early exit used to block a parent signing after a coach; it is gone.

GET /api/games includes the verifications array; the games list now shows "Verified by Dana Reyes (Parent)". Coach co-sign links are slice 2 and need parent `coach_cosign` consent plus an answer to counsel question 6 in `000-docs/287`.

The CI build caught a real race in the same window. PR #70 failed in "Build application" with `SqliteError: database is locked` while collecting config for `/api/admin/billing/replay-events`. `next build` runs several workers that each import the db module and run migrations against the same fresh SQLite file. Without a busy timeout, whichever worker loses the race fails immediately.

Earlier builds got lucky; migration 0005 widened the window because it added more `ALTER TABLE` work that all the workers wanted to perform at once. The race comes from `src/lib/db/index.ts` being imported by every worker. Every worker pays the import cost once, including the `migrate()` call.

The fix is a one-liner:

```typescript
const db = new Database(path);
db.pragma("busy_timeout = 10000");
db.pragma("journal_mode = WAL");
migrate(db);
```

`PRAGMA busy_timeout = 10000` is set after open, before `journal_mode` and on-import `migrate()`. Three consecutive `next build` runs from a deleted `data/hustle.db` and a clean `.next` all exit 0 with zero "database is locked" lines. The unit suite still passes. The same setting protects runtime concurrency: the deploy restart and the trial-reminder timer both touch the DB.

Omarchy got a quieter day. PR #38 adds the Commands section and the catalogue pipeline architecture to the project CLAUDE, addressing two CodeRabbit findings (the gate workflow was undocumented and the data flow between catalogue and merge step had no diagram).

The Commands section now lists `omarchy-gate`, `omarchy-preview-server`, `omarchy-single-test`, and the Playwright journey runner with the exact invocation each one wants. The pipeline section describes the data flow: catalogue raw facts, validate against `inventory.json`, push to a worktree for review, merge-is-deploy on green.

PR #39 lands workbooks 014 to 032 for The Beacon Wakes (typing adventure blueprint set), corrects "Omatrail" to "omaTrail" across documents 004 to 013 (an OCR artifact from the original scans that nobody caught until the workbooks started referencing earlier docs), and adds `scripts/worktree-hygiene.py` plus SessionStart/WorktreeCreate hooks.

The hooks are report-only: refuse paths outside the repo, never delete. The script prints a per-worktree summary that names the worktree, the branch, the upstream commit, and the working-tree status; it does not rewrite anything. A CI workflow runs the same check on every push.

The typing-adventure project subagents are scoped to the new BLUE GOLD BLUE brief, renumbered to 033 to end a 005 collision (a workbook titled "005" was duplicated by the new "005 Brief"). Catalogue public-facts refresh was a routine regeneration. No drama in the omarchy work; the docs were the bottleneck and they shipped.

Verification posture for the day: `game-verifications.test.ts` (6 tests covering parent/pin and coach/link signatures, AlreadyVerifiedError, and the game-delete cascade), E2E `10-game-cosign.spec.ts` plus 04 journey (7 passed), unit 74 files / 929 passed, integration 16, tsc clean, `next build` succeeded after the busy_timeout commit. Account lifecycle covered by `account-lifecycle.test.ts` (5 tests, in-memory DB plus real temp upload dir).

Three release tags in twelve hours. None of them are paradigm shifts. Each one is a bead closing with its test suite green and its doc reference pinned. The cadence is the work.

v2.3.0 carries PR #66 (ownership) on its own because that commit alone was a behavior change to every query layer; v3.0.0 carries PR #69 (delete plus export) as a major bump because account deletion is a non-backward-compatible surface that touches every athlete-scoped row; v3.1.0 carries the cosign slice because the new schema migration 0005 needed a tag of its own. Three commits, three tags, twelve hours, one epic.

The bead hierarchy under `hustle-4dc` had the right shape for this: each child shipped with its own test surface, its own PR, and its own documentation reference, so the merge order kept everything moving and the release train followed the fastest child, not the slowest.

## Related Posts

- [Hustle E2E Stabilization Sprint and Bounty Tracker Init](https://startaitools.com/posts/hustle-e2e-stabilization-sprint-bounty-tracker-init/)
- [IRSB: Four Releases One Day, Perception Watchlist, Hustle Cookies](https://startaitools.com/posts/irsb-four-releases-one-day-perception-watchlist-hustle-cookies/)
