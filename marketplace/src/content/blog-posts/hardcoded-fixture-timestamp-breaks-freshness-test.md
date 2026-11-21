---
title: "Freshness Tests: Generate Fixture Timestamps at Run Time"
description: "Build test fixture timestamps with date -u at run time when a backup age check reads age from the file name. A hardcoded one goes stale."
date: "2026-11-06"
tags: ["testing", "bash", "debugging", "devops", "claude-code"]
featured: false
canonical: "https://startaitools.com/posts/hardcoded-fixture-timestamp-breaks-freshness-test/"
---
A test with a fixed timestamp in a fixture name passed the day it was written, then began failing the next day and blocked the repository's full test gate (the check every merge must pass) on the main branch. This post covers what broke, the fix, and the second failing case the fix exposed. You will also get two rules for when a timestamp in a test is a bug.

## What the check does

A backup gets copied to a second machine, an off-host copy, and a bash script confirms the newest copy is recent enough. The age comes from the file name, which carries a UTC timestamp:

```bash
epoch=$(date -u -d "${stamp:0:4}-${stamp:4:2}-${stamp:6:2} ${stamp:9:2}:${stamp:11:2}:${stamp:13:2}" +%s)
age_h=$(( ($(date +%s) - epoch) / 3600 ))
```

Here `stamp` is the part of the name after the prefix. The age is whole hours, compared against a limit that defaults to 30. Anything under an hour is 0.

## What broke

The test set up three sample backup sets. The newest one was named with a fixed timestamp, 01:30 UTC on 4 November. The test also wrote a small JSON record saying that set finished at the current moment, but the age check ignores it and reads only the name.

The test merged on 4 November at 06:27 UTC. At that moment the name was about five hours old, so the check passed.

Whole hours round down, and an age of exactly 30 still passes. So a name stamped 01:30 UTC on 4 November passes until 08:30 UTC on 5 November. After that, the newest set counts as stale and the check fails. That is about 26 hours after the merge. The changelog says the check began failing "30 hours later" and blocked the pnpm check on main; with whole hours rounding down, the first failing age is 31. The sources do not record the first failing run, so the exact hour it went red is unknown.

## The fix

Claude Code, running Claude Opus 5.5, hit a failing full repository gate (pnpm check, exit code 1) while working on an unrelated change. Claude Opus 5.5 read the test and named the cause: the script judges freshness from the date in each set's name, and the test hard-codes that name.

The fix builds the name from the clock:

```bash
FRESH=$(date -u +%Y%m%dT%H%M%SZ)
mkset "catalyst-${FRESH}" "$now"
```

It replaced every reference to the fixed name with the generated one: 22 in all, counting that line.

## The second failure

The first run after the rename showed 25 passed and 1 failed. The failing case was "stale off-host copy pages." That case sets the limit to 0 and expects a page, which means it expects the newest set to be stale.

With the old fixed name, the age was large, so the page fired and the case passed. The fixture date had been carrying the test. With a name built seconds earlier, the age in whole hours is 0. The check evaluates 0 <= 0, which is true, so it does not page. The negative case fails.

The test had been passing only because its fixture date was old. The fix changed the case's limit from 0 to -1. Every age, including 0, now exceeds that limit, so the stale path fires every time. The case forces the condition it claims to test.

After that change the off-host test showed 26 passed and 0 failed. A shellcheck run at warning severity exited 0, and the full repository gate exited 0.

## What it cost

In this case the cost was a red gate on main. The fix merged on 6 November at 20:50 UTC. The sources do not record how long the gate stayed red before that. The agent's read was that every other pull request would hit the same failure.

## The rules

Two rules came out of this, and neither one is specific to bash.

First, when production code derives an age from a timestamp, that timestamp is a clock input. Build it from the current time inside the test, or pass the clock in explicitly. A literal date is only safe if the code never compares it with now.

Second, after you fix one fixture, recheck every test on the stale path. For each one, ask whether it still fails when the input is fresh. A negative test that only fails because its fixture is old was passing for the wrong reason. Force the path with a limit every age exceeds, as the -1 did here.

## Use this

- Search your test fixtures for fixed timestamps in file names, then check whether any production code reads age from those names. Generate those names with `date -u` at run time.
- For every test that expects a stale result, run it once with a fresh fixture and confirm it still fails. If it passes, rewrite it to force staleness, for example with a limit below zero.
- After any change to a freshness check, run the suite against one fixture dated now and one dated a few days back (both computed relative to the current time), and compare the results with what you expect.

## Related Posts

- [Reachability Is Not Freshness](https://startaitools.com/posts/reachability-is-not-freshness/)
- [Every Verdict Carries the Scope It Actually Ran](https://startaitools.com/posts/a-green-result-only-covers-what-it-ran/)
- [Test Gate Exit Codes: Add a Could-Not-Run Result (pytest)](https://startaitools.com/posts/test-gate-could-not-run-vs-failed/)
