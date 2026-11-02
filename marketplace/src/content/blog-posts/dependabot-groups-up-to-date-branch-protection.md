---
title: "Dependabot Groups for Up-to-Date Branch Protection"
description: "Dependabot groups turn one PR per dependency into one per ecosystem. Why up-to-date branch protection makes single PRs a serial rebase queue."
date: "2026-10-30"
tags: ["ci-cd", "devops", "automation", "release-engineering", "claude-code"]
featured: false
canonical: "https://startaitools.com/posts/dependabot-groups-up-to-date-branch-protection/"
---
Eight dependency pull requests sat open on one repository, and all eight were behind the default branch by 25 commits. Their checks were green, but only against the old base.

By the end of this note you will know how to set Dependabot to open one grouped pull request per ecosystem (one package manager, such as pip or GitHub Actions), why that clears the queue, and what grouping does not cover.

Dependabot is GitHub's bot that opens a pull request whenever one of your dependencies has a newer release. Branch protection is the repository setting that blocks a merge until required checks pass. This repository also required each branch to be up to date with the default branch before merging.

That rule is sensible. It has a cost when many pull requests are open at once.

Merging one pull request moves the default branch forward. Every other open pull request is now behind it. Each one has to rebase and wait for a fresh CI run, the automated checks on each pull request, before it can merge. Merging that one puts the rest behind again. Eight single-dependency updates become eight rebases and eight full CI runs, one after another.

The eight pull requests were opened on 2026-10-26. When reviewed on 2026-10-30, every one was behind main by 25 commits. The arithmetic is the problem, not any single update.

## What the first plan was

The assistant, Claude Fable 5.1, followed the arithmetic. Its plan was to rebase and merge all eight, one at a time, with fresh CI on each. It also noted a shortcut: one combined bump commit in a single pull request. That would work, but it routes around Dependabot instead of configuring it.

The operator interrupted with a one-line question: can't you turn down the Dependabot noise. The assistant answered that grouped updates in the Dependabot config would turn eight pull requests into one or two, and that a monthly schedule would cut the cadence. The operator chose to merge the config change first and let Dependabot regroup. The hand rebase was cancelled.

The first plan accepted the queue as a cost to pay down by hand. The correction treated it as a setting to change.

## The config

The change lives in `.github/dependabot.yml`. These are the relevant keys of the pip block (its existing Django ignore entry is left out here). The github-actions block changed the same way.

```yaml
- package-ecosystem: "pip"
  directory: "/"
  schedule:
    interval: "monthly"
  open-pull-requests-limit: 2
  groups:
    python-dependencies:
      patterns: ["*"]
```

Three settings do the work.

- `groups` with the pattern `"*"` puts every update for that ecosystem into one pull request.
- `interval: "monthly"` replaces the weekly Monday run. The commit's stated expectation is two grouped pull requests a month.
- `open-pull-requests-limit: 2` caps how many are open per ecosystem at once.

The existing ignore for Django major versions stays in place. A major move is still an owner decision, so grouping does not change it.

Verification before merge was a local YAML parse. GitHub validates the schema on push and reports config errors in the Dependabot tab.

## What grouping does not cover

Security updates are not grouped by default. They still arrive as their own pull requests as soon as GitHub publishes the advisory. The config file carries a comment saying so.

Grouping cuts routine version churn. This config leaves that default alone, so security advisories reach you exactly as they did before.

## The blocker that had to clear first

The grouping change could not merge on its own. The image scan had started failing on every branch. The scanner, grype, flagged a critical CVE (a published vulnerability ID) in the Python interpreter of the base image python:3.14.8-slim. The fix for that CVE shipped in 3.14.10, so the scan job failed until the base image moved.

The fix moved the application and CI containers to python:3.14.10-slim, a base image published 2026-10-28. The change touched the Dockerfile, the compose file and two CI workflows. The required check's name stayed the same. The branch ruleset pins that exact string, and only the repository owner can change the ruleset, so renaming the check would have blocked the merge.

The base-image move broke a test of its own. One test hard-coded 3.14.8 in a regular expression. The first CI run failed with `'NoneType' object has no attribute 'group'`, which is what a pattern looks like when it no longer matches the file. The fix made the expression accept any 3.x.y slim pin. The test now asserts that the pinned version equals the version the interpreter reports. Locally, 52 tests passed in the new container, and a separate run of the image test file passed all 6.

That test failure is the kind that stays in the record. A version string was written into a test as a fact, and the first upgrade broke it.

## What happened after the merge

All times are UTC on 2026-10-30.

- 16:51: the grouping change was opened.
- 18:51: the grouping change merged.
- 18:52: Dependabot opened a github-actions group with three updates.
- 18:54: Dependabot opened a python-dependencies group with six updates.
- 19:22: the python group merged.
- 19:44: the github-actions group merged.

Dependabot closed seven of the eight single pull requests itself. The eighth was closed by hand. The repository ended the day with zero open pull requests.

The stale singles were not the latest versions either. The python group took ruff to 0.17.3 where a single had offered 0.17.2, and pydantic-ai-slim to 2.62.0 where a single had offered 2.60.0. The grouped pull requests, opened four days after the singles, already pointed past them.

The session ran from 16:47 to 20:19 UTC, about three and a half hours. The config diff is a few lines. Getting it to merge took the base-image change and its test fix.

The grouping change, with its rationale and verification notes, is public: [catalyst-onboarding-v2 #142](https://github.com/intent-solutions-io/catalyst-onboarding-v2/pull/142). The Python 3.14.10 base-image move and its test fix are a separate pull request: [catalyst-onboarding-v2 #143](https://github.com/intent-solutions-io/catalyst-onboarding-v2/pull/143).

## Use this

- Group each ecosystem with a catch-all pattern, and cap open pull requests per ecosystem so the queue stays short.
- Parse the YAML locally before you push, then check the Dependabot tab for config errors, since GitHub validates the schema on push.
- Keep a separate review path for security updates. With the default left alone, grouping does not collect them, and they arrive as soon as GitHub publishes the advisory.

## Related Posts

- [Release from the tested commit, not the bot commit](https://startaitools.com/posts/release-from-tested-commit-not-bot-commit/)
- [Docker hardening your test suite cannot see](https://startaitools.com/posts/docker-hardening-your-test-suite-cannot-see/)
