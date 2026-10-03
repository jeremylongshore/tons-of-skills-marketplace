---
name: inbound-filter-matrix
description: |
  Canonical inbound-filter matrix (OP05–OP07). Owner is noise-classifier.
  Ignore still bills. Discard is plan-gated and prospective. Not a marketplace skill.
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Designed for Claude Code
tags: [sentry, nested, saas, checklist]
---

# inbound-filter-matrix

**Canonical owner:** `sentry-issue-triage` → `noise-classifier`
**Copies:** quota `volume-cutter` may keep a labeled copy (`COPIED-FROM.md` / `OWNER.md`). Do not silently fork this matrix into `sampler-and-filters`. Delete copies when cross-skill agent calls work.

This checklist is not `issue-triage-loop`.

## What the toggles drop (before quota, once enabled)

Project → Inbound Filters. They are off until someone turns them on. They do not inherit onto new projects (SC03).

| Toggle | Drops | Does not drop |
|---|---|---|
| Browser extensions | Known extension errors | Your app frames |
| Legacy browsers | Known legacy-browser errors | Current browsers |
| Web crawlers | Crawler traffic | Real users |
| React hydration | Hydration errors the filter recognizes | Every React error |
| ChunkLoadError | That class | Unrelated dynamic-import failures you have not named |
| Localhost | Localhost events | Staging hosts |
| Legacy browser filters / web crawlers | See docs | Custom user agents you did not list |
| Transactions from health checks | Transaction names matching the glob list below | Error events from those URLs; names that miss the glob |

Filtered ≠ dropped. Only accepted events count toward quota. Do not add filtered and dropped into one "lost" number.

## Health-check glob (Help Center, 2026-08-13)

The transaction filter matches a fixed list, including `*healthcheck*`, `*health-check*`, `*heartbeat*`, `*/health`, `*/healthy`, `*/healthz`, `*/_health`, `*/live`, `*/livez`, `*/ready`, `*/readyz`, `*/ping`, `*/up`.

- `ping_health` does **not** match.
- `/api/v1/status` does **not** match unless it fits a glob.
- Error events from a health URL are **not** dropped by this filter.

For names that miss: recommend SDK `ignoreTransactions` / `beforeSendTransaction` for the real transaction names, and a separate error drop (`beforeSend` or an error-message filter) for probe failures you do not want. Error-message filters and release filters are Business/Enterprise — label them. Do not invent spike-protection's plan placement.

## Ignore vs Discard (OP07)

| Action | Alerts | Quota | Plan | Scope | Retrospective? |
|---|---|---|---|---|---|
| Ignore | Stops paging that issue | Still bills; the events are still happening | all | issue | no |
| Resolve | Until it regresses | A new event counts again | all | issue | no |
| Delete & Discard | Issue disappears | Future events with that fingerprint do not count | Business or Enterprise | per project, list under Inbound Filters | **No.** Prospective. Already accepted events stay counted. |
| SDK `ignoreErrors` / `denyUrls` | Never sent | Never accepted | n/a (your deploy) | that SDK | Next deploy only |

Discarded issues are invisible, so a real regression of that fingerprint will not page. Recommend Discard only for junk you will never fix. Copy the same errors into SDK `ignoreErrors` so you are not paying ingest processing to drop them. Un-discard from the list when the decision was wrong. Do not click Discard from this skill.

Parent must know the plan (user statement or a read) before recommending Discard. If the plan is unknown, say Discard is plan-gated and stop at the label.

## Recommendation labels

Return exactly one primary label:

- `ignore` — alerts only; quota unchanged
- `discard` — quota, Business/Enterprise, prospective, fingerprint-wide
- `sdk-drop` — next deploy (`ignoreErrors`, `denyUrls`, `ignoreTransactions`)
- `enable-builtin` — a filter toggle that is off and matches the class

## Fail

Merging this matrix into the postmortem. Claiming Ignore stops billing. Claiming Discard rewrites history. Recommending an environment rate limit. Summing filtered and dropped. Calling the discard API.
