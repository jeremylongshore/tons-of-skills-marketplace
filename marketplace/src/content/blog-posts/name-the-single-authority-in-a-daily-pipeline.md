---
title: "Name the Single Authority in a Daily Pipeline"
description: "When a daily pipeline runs unobserved, every concern picks up competing authorities. Name exactly one and refuse every substitute."
date: "2026-10-06"
tags: ["ci-cd", "automation", "release-engineering", "devops", "claude-code"]
featured: false
canonical: "https://startaitools.com/posts/name-the-single-authority-in-a-daily-pipeline/"
---
When a daily pipeline runs unobserved, every concern quietly picks up competing authorities. A line-count cap (a number that decides whether a post ships as a short note or a longer read) lives in three places. A list of which reviewers must run for each tier lives in four. The prompt the writer receives lives in five. None of them name a single source of truth. The wrong one wins silently, and the receipt (a machine-written record proving a step really ran) claims the pipeline did things it never did.

A reader running any unattended daily job can audit their own pipeline by writing two short statements per concern: "this file holds X," and "every other source refuses when X changes." After reading, the engineer can run that audit in under an hour and have a list of one-line refusals that catch a wrong answer before the next run.

## The pattern

The cure is two rules, not one. First, name exactly one authority per concern. The lander (the script that commits and publishes; the model never touches git), not the quality seal (a hash record of exactly what passed the gates), holds the line cap. The manifest, not the skill, holds the role requirements. The fresh origin/master tip, not the shared checkout, holds the inputs to a monthly job. The pinned schedule file, not the crontab, holds the timing. The printed thresholds, not the prose, hold the tripwire values. The hash-pinned writer context, not the prose, holds the writer's brief.

Second, every other source refuses. The seal reads the lander's named constants; if the cap is bumped there, the seal's parity test fails. The receipt refuses a role output whose agent type does not match the role name. The worktree refuses to commit a path that is not on its allow-list. The drift check exits 1 when the host crontab drifts from the manifest. The threshold printer refuses to print a placeholder. The writer refuses an unknown slot in its brief.

That refusal is the load-bearing part. Without it, the named authority is just a comment.

## The receipt that lied

The signal was not a failure. Three nightly runs logged "transcript corroborates" 1/9, 4/4, 0/9 while the role receipt said complete. Replaying the real sessions: a Tier 2 run on 2026-10-03. The receipt claimed nine roles ran. Five of those nine did not run under the role's named agent type. The receipt was completing against completion shapes; the agent type was being substituted to a catch-all "claude" type, and the role file was being staged under the role name anyway. The mandatory count differs because Tier 2 adds five reviewer and SEO roles (9) and Tier 1 needs only classifier, writer, meta optimizer and code reviewer (4).

The fix was to refuse the substitution at the receipt. The role file's named agent type has to match what actually ran. The receipt now refuses a staged role-AGENT.json whose subagent_type names a different agent type than the role. A row counts only if the names match.

## The constants that drifted

The lander held the binding 145 and 260 line caps. The Python quality seal held bare 145 and 260 literals. The parity test covered the lander and the grader but not the seal. So when the cap was bumped to 261 in the lander, the seal's count was still based on 260. The seal said tier 2. The pipeline shipped tier 3.

The fix was to name the constants in the seal (TIER1_MAX_LINES, TIER2_MAX_LINES), add a parity test that covers all three files (lander, grader, seal), and plant a failure: setting TIER2_MAX_LINES = 261 in the seal makes the parity test fail. The thresholds and counting method are unchanged. The test is the new wall.

## The isolated worktree

A monthly job ran in the primary checkout. The checkout sat mid-rebase for six days, and both monthly jobs failed on the next run. The fix was to give every monthly job a detached worktree of freshly fetched origin/master, commit only paths on its allow-list, push HEAD:refs/heads/master, and abort a failed rebase inside the worktree. The primary checkout never sees the rebase. The host refuses non-default branches.

## The pinned schedule

The host crontab was the de facto schedule. Two gate reviewer agents (fact-checker and article-consistency-checker) were the de facto role authority, copied to ~/.claude/agents/ by hand. Both drifted. The fix was to make the schedule a versioned file in the repo, pin the two agent copies by sha256, and ship a read-only host drift check that exits 1 when the host crontab drifts from the manifest or when the agent copies differ from the SHA256SUMS. Drift is now visible in CI, not on a missed run.

## The printed thresholds

The tier-creep guard reported percent bands. The report printed them as T1 60 to 70, T2 25 to 35, T3 5 to 10, but the BANDS variable in the script held the real thresholds. The fix was to print the real BANDS values, not a placeholder. Anyone reading the report now sees the same numbers the tripwire fires on. The same patch added a front-matter offset check that flags any non-negative-six-zero-zero timestamp on a new post (warn now, hard-fail from its dated switch).

## The versioned writer brief

The writer agent received a brief assembled from the daily run's slot object, but the brief was rendered ad hoc each time. Untested. Unpinned. The fix was a single file: scripts/blog/writer-context/writer-context-v1.md, rendered by a fixed Python entry point from a fixed slot object (the step 1b finding, only the source excerpts that back it, tier, voice facet, metadata, models, a short collaboration note, related posts). Released versions are sha256-pinned in writer.VERSIONS. An edit means v2. A new contract check, observation only, runs in contract.validate_evidence. Before 2026-10-21 a gap is one PRODUCER-CONTRACT: ADVISORY line, never a refusal. After that date the check refuses.

A cost comparison ran. The skill's path used 59 percent more tokens (1,738,915 versus 1,093,069) and 30 percent more wall time (124.3 seconds versus 95.3 seconds), kept fewer candidates (13 versus 18). The decision: no expansion. The step stays off.

The full authority map, with each concern and its named source, is in 000-docs (each repo's numbered folder of dated records), file 014-AT-ADEC-blog-pipeline-authority-map.md.

## Use this

- For each concern in your pipeline, write the source-of-truth statement ("the X, not the Y, holds Z"). If you cannot write it, the concern has no authority.
- Add a refusal test for every other source. The named authority is just a comment until the next file can fail to keep up.
- Version everything that runs unobserved: the schedule, the writer brief, the role list, the tripwire thresholds. A versioned file in the repo beats a copy in a config.

## Related Posts

- [working-is-not-proven](https://startaitools.com/posts/working-is-not-proven/): every claim needs a shipped source and an executable proof.
- [wrong-mode-green-is-not-a-gate](https://startaitools.com/posts/wrong-mode-green-is-not-a-gate/): a freshness gate that accepts the wrong mode flag trains people to trust a board that cannot see.
- [exit-zero-is-not-push-ok](https://startaitools.com/posts/exit-zero-is-not-push-ok/): on a shared checkout, the post-push HEAD, not the exit code, is what tomorrow's cron inherits.
