---
title: "Rehearse the deploy, not the test suite"
description: "A production deploy rehearsal runs the real deploy scripts against the production Compose file. In catalyst-onboarding it caught a database data-directory permission bug the test suite could not."
date: "2026-10-01"
tags: ["deployment", "release-engineering", "devops", "production", "rehearsal"]
featured: false
canonical: "https://startaitools.com/posts/rehearse-before-production-catches-what-tests-cant/"
---

*Correction, 2026-10-03: An earlier version of this post misdescribed the bug and the rehearsal. The bug was in the production Compose file, not in a folder the deploy script created: `PGDATA` pointed at a subdirectory of a bind mount whose root was owned by root with mode 0700, so the postgres user could not reach it and the database never became healthy. The rehearsal caught it on its first attempt, outside the scripted steps. The rehearsal had ten steps, not six cases plus a seventh, and two of the cases (the failed redeploy and the bad version) were described wrongly. The run used real SOPS decryption with a throwaway key, not the production secrets. It took about nine minutes, not an hour, and the 4 a.m. page described in the cost section never happened; that section is now framed as a possibility. The record shows one pre-production review, not two independent reviewers, and the third should-fix item was a runbook note, not image versioning. The details below have been corrected.*

## The finding

A ten-step deploy rehearsal on a non-production host caught a production-breaking bug before production. The production Compose file pointed Postgres's data directory at a subfolder of a root-owned, locked-down mount, and the database never started. Had it shipped, the database would likely not have started on the VPS either. The test suite had nothing to say about it. The rehearsal's first attempt failed on it.

The rest of this post is the discipline behind that rehearsal: what to script, what to run, and what to refuse to merge until the rehearsal passes.

## What the rehearsal actually was

A production deploy package for `catalyst-onboarding` had shipped a full self-hosted runner: a deploy check, a staging test, a restore drill. The CI was green. A pre-production review still stopped the PR with two blockers and three should-fix items:

- Rollback after migration. The readiness probe would refuse to come up unless the schema matched the migration head baked into the image. Roll back a migrating deploy and the app is half-switched, reading a new schema from an old binary.
- Backup step with no time limit. The new database backup command had no timeout, so a wedged backup could hang the nightly server backup.

The three should-fix items: a path that could turn an outward flag on (document signing, which emails links) without a recorded approval, a failed redeploy that would roll back onto the same broken version, and the runbook did not say that Docker keeps env-file values in the container's stored config.

The builder fixed all five. CI was green again. Then the real test: the deploy package ran, in full, on the dev box, with real SOPS decryption (a throwaway key), as a non-root user, on paths kept off the production ones. The steps, condensed:

1. Deploy. Upgrade with a database change. Roll back. Verify the older image accepts the new schema exactly one revision forward, then deploy forward again.
2. Outward flag. Try to turn document signing on without the recorded approval. The Compose wrapper refused and the running app was untouched.
3. Failed redeploy. Turn the signing flag on with approval but without the signing config, so the new web cannot start. The deploy stopped the worker, raised an urgent alert and did not roll back onto the same broken image. Turning the flag off and redeploying brought it back.
4. Broken version. Deploy a version that migrates the schema and whose web app crashes on import. The deploy rolled itself back to the previous version.
5. Backup under a locked database. The backup step gave up in 3.4 seconds (and in 8.2 seconds under a session timeout) and kept the previous good dump. A failed backup hook does not stop the nightly backup.
6. Restore drill. After the lock released, a normal dump ran, and the restore drill restored it into a disposable database and verified it.

The bug that mattered was not one of those steps. The first rehearsal attempt never got that far. The production Compose file set `PGDATA` to a subfolder of the bind mount. With a mount root owned by root with mode 0700, the postgres user cannot even enter it, and the database never became healthy. The fix made the bind mount itself the data directory, which the Postgres image's entrypoint takes ownership of.

Nothing in the test suite creates that mount, so nothing in the test suite could see it. The rehearsal could, because it runs the production Compose file through the real deploy scripts the way production will.

That is the lesson. Tests check what the code does. The rehearsal checks what the deploy does. Those are not the same question.

## Why the discipline exists

A deploy is not a single command. It is a sequence of side effects: a directory created, a service file installed, a port opened, a database migration applied, a health check called, the old version stopped, the new version started, the load balancer re-pointed, the old version left running for a window in case the new one is bad. Every one of those steps has a small chance of failing in a way no test layer exercises. A unit test cannot simulate a half-applied schema migration because it sees a single schema, applied once, never rolled back. An integration test does not mount the production data directory with the production owner and mode, so it cannot see a database that is unable to reach its own data. The rehearsal is the only place where the deploy runs the way it will run, with the permissions it will have, against the filesystem state it will have to create.

## What the rehearsal script should cover

A rehearsal script for a production deploy should at minimum cover:

- The full deploy, including the pre-deploy switches (sending, feature flags, maintenance mode) and the post-deploy switches back on.
- A migration, a rollback, and a forward-fix on top of the rollback.
- A failed deploy at every external dependency (network, database, image registry, secrets backend) and the recovery path.
- The backup step under each of: a clean database, a locked database, a slow database, and a database the backup step cannot reach.
- A restore drill from the most recent backup, with a row count check, a hash check, and a swap-back.
- The alerting path. Kill a worker, confirm the alert reaches the on-call channel, restart, confirm the resolution note follows.

If the rehearsal cannot script one of those cases, the deploy is not ready.

## The cost

The rehearsal ran in about nine minutes, on top of the time spent on the review fixes. Without it, the first production deploy would have come up with a database that could not start. That is a possibility, not something that happened, but it is the kind of failure that lands at a bad hour and ends in a manual fix on the server. The trade is not close.

## Use this

- Rehearse the deploy, not the test. The deploy scripts and the production Compose file create the production state. The test suite only checks the code. If they disagree, the deployed configuration wins, and the rehearsal is the only way to find that out before production.
- Script the cases the test suite cannot reach. The production data directory with its real owner and mode. Migrations applied and rolled back. Outward flags that need an approval record. The backup step under a locked database. Each of these is one bug the rehearsal catches and the test suite never will.
- Block the merge on the rehearsal, not on the test suite. Green CI is necessary, not sufficient. The deploy package is not done until it has run end to end, through the real secrets-decryption path, on paths kept off production, and every case in the script has a recorded outcome.

## Also shipped

- Marketplace mirror sync had failed three Mondays running, with 21 sources held in quarantine; four Sonnet drift reviewers landed the verdicts (`Re-baseline`: box-cloud-filesystem, dolt-mcp-vcs, skills-janitor, brand-forge, skyvern, kobiton-automate; `Re-baseline with notes`: hermes-tweet, x-bug-triage, governed-second-brain, slack-channel, pr-to-spec; `Hold`: hyperflow, x-twitter-scraper; plus the osv-scanner v2.6.0 flag held pending decision).
- PR #1594 resolved three lapsed CI deadlines on merit: changed-package audit flipped to blocking (only fails on deps PR changed, none in the a2a-client or pr-to-spec range tested); strict frontmatter errors fixed in 10 repo files (9 remain in external mirrors, deadline extended to 2026-10-31); whole-corpus `npm audit` extended to 2026-10-31.
- Bob's Big Brain bulk-import triage found 16,202 "imported" rows are ICO compile output in three waves, not a vault import. 6,443 already retired by title-Jaccard supersession, with some false matches. 5,100 rows to deprecate in three reversible waves.
- Registrar Nightly canary had failed five nights running: canary controls grew from 3 to 6, but the nightly fixture's seed text covered the original 3 only. PR #356 fixed it; manual `workflow_dispatch` confirmed green.
- `repo-sweep` and `release` skills v3 merged: branch-protection bypass gone (PRs merge through GitHub API pinned to exact commit, no `--admin`, protection never changed); estate mode scans 199 repos in roughly 34 seconds; 68+26 tests pass; both skills grade A (96 and 95) on the validator.

## Related posts

- [Linking the public surface to the deployment thesis]({{< ref "link-public-surface-to-deployment-thesis.md" >}}) (2026-09-30). The deploy thesis is the contract. This post is one rehearsal of one package against it.
- [Team page ordering is a release decision]({{< ref "team-page-ordering-is-a-release-decision.md" >}}) (2026-09-28). The release decision lives in the deploy script, and the deploy script is what the rehearsal exercises.
- [Use the primitive, not the patch, in CodeQL]({{< ref "use-the-primitive-not-the-patch-codeql.md" >}}) (2026-09-27). The same logic applies. Reach for the primitive the platform already maintains, then rehearse the rule the platform enforces.
