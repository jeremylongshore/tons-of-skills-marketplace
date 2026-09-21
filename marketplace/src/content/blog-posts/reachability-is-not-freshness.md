---
title: "Reachability Is Not Freshness"
description: "Endpoint reachability and data freshness require separate checks. A status page returned HTTP 200 while serving stale July snapshots."
date: "2026-09-17"
tags: ["devops", "automation", "testing", "ci-cd", "architecture", "debugging"]
featured: false
canonical: "https://startaitools.com/posts/reachability-is-not-freshness/"
---
The public status page was up. It answered. It was lying through a 200 status code.

For roughly two months, every route describing machine, catalog, or copy state returned the July 11 design-only snapshot. An unmanaged publisher was the root cause: the feed lacked a recurring job, atomic snapshots, and explicit publication timestamps separate from observation timestamps. Every monitoring check measured one thing only: does the endpoint answer? Not one asked whether the answer was current, so everything watching reported that everything was fine.

Six merged pull requests that day exposed the same defect wearing different clothes. The mechanism was different every time. The root error was always that a check was green because it measured the wrong thing.

## The publishing model replaced the unmanaged publisher

A single commit, `0740b86`, covered approximately 1900 lines across 22 files. The new model runs a controlled recurring publication job with distinct source clocks (when data was observed) separate from publication clocks (when the snapshot went live). Atomic recoverable snapshots. All 11 old reports kept their URLs, stayed labeled historical, and went read-only. An independent outside-in freshness check runs via Globalping with regional HTTPS probes on both Tons of Skills hostnames. The check has bounded claims: "Public source presence and endpoint reachability." A successful cloud probe does not claim every browser or ISP is healthy.

The build included `scripts/mission_control.py` (329 lines), `scripts/mission_control_job.sh` (48), `scripts/install_mission_control.sh` (77), `scripts/install_public_monitors.sh` (103), `scripts/regional_reachability.py` (93), `scripts/test_mission_control.py` (166), and the runbook (123 lines). Validation ran 19 hermetic unit, recovery, and regional tests. Site verifier covered 18 routes, 8 screenshots, 22 sitemap URLs. ShellCheck on all three runtime and install scripts. Gitleaks returned clean. Desktop, tablet, and mobile browser smoke covered stale, unknown, and revision regressions.

```
// Source clock and publication clock are separate
snapshot.source_timestamp = when_data_was_observed
snapshot.published_at = when_snapshot_went_live
failed_fetch.last_successful_observation = retained, not overwritten
```

But it was not complete.

## Failed probes are not unmeasured probes

Globalping can return a country probe with null TLS and body fields when a country endpoint fails. The code read those nulls as "no result for this country" and dropped the row entirely. A country that failed looked like a country that was never checked. No difference in the report. The fix keeps the explicit failed or unverified row with labels. Never treat it as successful. The signal must be loud: a failed measurement is measurably different from an unmeasured one. Regression coverage added. A labeled synthetic-alert prefix was added so native monitoring drills are safe to run without confusion.

## A drill exposed the sandboxed alert

A controlled native stale-fixture drill, deliberately feeding the system a stale snapshot to confirm it screams, delivered the product alert correctly. In doing so it exposed that the separate execution-failure service's strict filesystem sandbox denied the governed notifier's temporary file. The alert that fires when the job itself fails could not fire. The fix gave that service its own writable `PrivateTmp` while keeping the strict filesystem protections in place.

The governed alert contract sharpened. Exit codes carry distinct meanings:

```
// Execution-failure alert contract
exit 0   -> delivered, record in ledger
exit 5   -> delivered-duplicate, already logged, suppress re-alert
exit *   -> delivery failure, remains pending
```

This avoids both volume-cap noise and undelivered-alert masking. Duplicates stop producing noise without letting real failures hide. An initial new replay callback serialization error was caught and rerun during development. It was not treated as production evidence.

## An open tab rendered a stale report

The publisher was correct by this point. An already-open browser tab still showed the old report. The manifest advanced while the rendered page stayed frozen and appeared stalled. The client now compares parsed UTC clocks and keeps the highest attempted publication in session storage. Older, repeated, or alternating cached responses cannot trigger a reload loop, and unverifiable responses stay visibly stale.

The evidence here is the strongest detail: the new browser regression was run against the PREVIOUS production client first and failed with a navigation timeout. It passed after the repair, on desktop, touch tablet, and mobile. A test that was watched to fail.

## A self-consuming guard

This finding came from a late CodeRabbit review on PR 5. The refresh guard added to prevent reload loops is one-shot per publication. A malformed newer manifest could consume that guard before the corrected publication arrived, locking an open tab out of its own fix. The shared browser validator now checks exact string revisions, schema, semantic ISO calendar dates, explicit timezone, and future clock limits before it evaluates freshness or records a reload attempt. The reload path still allows an explicitly unavailable source to refresh the honest outage display when last-good clocks exist.

Coverage includes missing and non-string revisions, missing or impossible or future source clocks, leap dates, invalid hours, and the previous cases of normal, older, repeated, or alternating publications. Full regression test suite updated to pin the boundary.

## The same discipline about what a number claims

PR 7 added six Intent Solutions org projects and five personal repos to the site with explicit September 17 dating and one clear statement: "Stars are not customers, revenue, or evaluation outcomes." Same discipline about what a number is allowed to claim. A reachability check that answers on the endpoint cannot defend a freshness claim. Both dimensions need independent verification.

## What the day cost

Persistent system monitors went onto the Buzz host. The catalog deployments that had quietly preserved the separate report directory are now owned in source, which is the part that let the page rot for two months without anyone touching it. The redaction pass on the historical reports was manual.

Reachability is answering. Freshness is current. A check that is green on one of those has proved nothing about the other, and the day's real cost was finding that out five separate times in one afternoon.

The Kobiton case study started that day with Claude Opus 5. The blog pipeline ran on MiniMax M3.

## Related Posts

- [Liveness Without Health Is Theater](https://startaitools.com/posts/liveness-without-health-is-theater/)
- [A Green Result Only Covers What It Ran](https://startaitools.com/posts/a-green-result-only-covers-what-it-ran/)
- [The Status Nothing Could Write To](https://startaitools.com/posts/the-status-nothing-could-write-to/)
