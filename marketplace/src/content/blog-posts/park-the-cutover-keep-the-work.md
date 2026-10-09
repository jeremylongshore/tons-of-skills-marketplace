---
title: "Park a Migration Without Losing the Work"
description: "Park a migration as an atomic fast-forward to a feature branch with the full gate suite on the merged commit. Five invariants keep parked work recoverable."
date: "2026-10-08"
tags: ["architecture", "release-engineering", "devops", "ci-cd", "migration", "decision-record"]
featured: false
canonical: "https://startaitools.com/posts/park-the-cutover-keep-the-work/"
---
A migration that ships by reaching the default branch with a green badge still has a second decision hidden inside it: do we point production at it today, in a week, or ever. When the build and the deploy are welded together, that second decision leaks into rollback theater even when the right answer is to wait months. The pattern this post calls publish-and-park splits them on purpose, so parking an owner can be the cutover's moment instead of its point of no return.

A Flask-to-Django refactor in `catalyst-onboarding` (a public onboarding repo) reached that fork in October. The Django stack was complete, gated, and pushed to two feature branches as atomic fast-forwards. Production stayed on Flask. The work stayed on the feature branches where it had landed. The pattern that made the cutover reversible is what this post is about.

## What is the publish-and-park pattern for software migrations?

The publish-and-park pattern splits a refactor's build from its cutover so parking the work is reversible. The gate suite runs on the merged commit on a feature branch with no production mutation, and a dated "do not cut over" record lands in the repo. Production stays on the old stack until a separate decision points it at the new one.

## The pattern, in one sentence

Push the refactor to its feature branches as an atomic fast-forward, run the full gate suite on the merged commit, ship nothing to production, write the explicit "do not cut over" record, and open a successor planning repo so the parked work has somewhere forward to go.

Five invariants make a parked refactor recoverable instead of abandoned:

1. **Atomic push to a feature branch.** The work lands as one fast-forward commit. No merge commit. No force push. The branch tip is byte-identical to the merged result.
2. **Full gate suite on the merged commit.** Unit, integration, contract, coverage audit, security, and an independent reviewer all run against the tip. Green badge is recorded on the commit, not on a moving branch.
3. **No production mutation at ship time.** The cutover is a separate operation, owned by a separate decision, executed on a separate day.
4. **An explicit "do not cut over" document.** A dated decision record lives at the top of the repo. Future readers find it before they touch the parked work.
5. **A successor repo.** The parked work has somewhere forward to go. It is not a dead branch waiting for a code archaeologist.

When all five hold, parking an owner is reversible. When any one is missing, parking an owner is abandonment in slow motion.

## The build-up trail

The Flask to Django migration was not a weekend. It was six stacked PRs landed over a single day, each one a thin slice of the new lifecycle. The numbering gap between #113 and #115 is an unrelated CI-infra fix that interleaved between the intake and review slices; it is not part of the migration stack and it would be a mistake to read the migration as seven PRs because of it.

```
PR #113 feat(intake):     add native Django intake and durable Temporal mail
PR #115 feat(review):     run native stages with durable evidence and bounded admission
PR #116 feat(deploy):     promote authenticated immutable image archives
PR #117 feat(profile):    persist native review profiles and durable CRM projection
PR #118 feat(ci):         record complete shard phase and worker timings
PR #119 feat(onboarding): add Select partner footers and repair bounded CI setup
```

Each PR carried its own gate subset. The full suite ran only when the last commit on the immutable milestone branch was in place. That ordering matters: a partial green badge on a partial stack is not a parking artifact. It is a half-truth.

## The atomic push

The push that turned the work into a parking artifact looked like this:

```bash
# After the full makecheck suite passed locally and was re-run by CI on the same SHA:
git push origin feat/django-agreement-lifecycle:feat/django-agreement-lifecycle \
  --ff-only
git push origin feat/django-agreement-notifications:feat/django-agreement-notifications \
  --ff-only
```

Two pushes, both fast-forward only. The remote tip is byte-identical to the local tip. No merge commit hides what was actually shipped. No force push re-writes history. A reader six months from now can run `git log` on either branch and reconstruct the exact build state.

The atomic property is the load-bearing one. A merge commit would let a future force-push hide reverts. A non-fast-forward push would break anyone who already has the branch checked out. Neither breaks the next person, but both break the parking pattern's audit trail.

## The gate suite on the merged commit

The full gate suite ran on the immutable milestone commit, not on the moving feature branches:

```
makecheck terminal PASS 598.411s
  1746 unit + 1 skip
  2764 SQLite + 160 skip
  436 pilot
  static + security

PG terminal 4659 PASS / 14 skip / 4673 collected
  1262.33s test / 1271.060s whole

v2 coverage audit PASS
Independent reviewer APPROVE <commit> ONLY
```

The reviewer line is the one most teams skip. A human (or a strictly scoped reviewer agent) confirms the gate results match the code. Without that confirmation, a green badge is a CI vendor's promise. With it, a green badge is a recorded decision by the team that owns the codebase. The parked refactor is recoverable because the gate results are pinned to the commit, not to the workflow run.

## The cutover stays on Flask

Production stayed on Flask main. The Django stack was pushed to its feature branches, and the PR was converted to draft. A full-ref backup bundle was written to `~/backups/catalyst-onboarding-preserve-*` the following morning; the path-embedded date is for the snapshot job that wrote it, not for the work itself. The bundle is belt-and-suspenders: the feature branches are the primary artifact, the backup is the secondary. Neither mutates production.

This is the second decision, the one the publish-and-park pattern splits out. The decision is not "is the work done." It is "is this the right moment to point production at it." The two questions have different owners, different evidence, and different reversibility costs. Welding them together is what makes migrations feel like a one-way door.

## Why not the obvious approach?

The obvious approach is to merge the Django stack to `main`, let CI go green, and cut over. Three reasons that fails:

1. **The badge is on the branch, not the commit.** A green badge on `main` after the merge tells you the gate suite passed against a moving target. Anyone who has reset `main` to undo the merge invalidates the badge retroactively. The parked refactor has no such exposure: the gate results are pinned to the commit SHA on the feature branch, and that SHA does not move.
2. **Cutting over is a single failure domain.** If the cutover breaks, you do not know whether the bug is in the new code, in the deploy step, or in the rollback. With the cutover decoupled, the new code can sit on a feature branch for months while the deploy step is rehearsed separately. The two failure domains stay separate.
3. **The "do not cut over" decision has nowhere to live.** A merge to `main` is the act of cutting over, by definition. There is no document you can write that says "this is on `main` but do not use it" without breaking the social contract that `main` is production. The decision record has to land before the merge, which means the merge has to be deferred, which means the work has to live on a feature branch.

The pattern is not a workaround for a missing feature. It is the only shape that makes parking an owner recoverable.

## The "do not cut over" record

The decision record is a PR, not a wiki page and not a numbered-record entry. PR #124 in `catalyst-onboarding` carries the dated decision that the Django stack stays parked and Flask stays in production. The PR body names the commit, links the full-ref bundle, lists the gates that passed, and names the successor repo.

The PR is the artifact a future reader finds before they touch the parked work. A wiki page rots. A numbered-record entry (each repo's dated folder of decision history) can be moved, renamed, or lost when the numbering scheme changes. A PR lives at the top of the repo's pull request list until it is closed, and its merge commit lives in `main` history forever.

## The successor repo

The parked refactor is not abandoned because it has a successor: `intent-solutions-io/catalyst-onboarding-v2`, opened the following morning with the beads (a tracked task record in the repo's issue database) prefix `catalyst-v2` and no code. The planning-phase foundation exists so the parked work has somewhere forward to go.

A parked refactor without a successor is a dead branch. A parked refactor with a successor is a deferred plan. The successor repo does not have to contain the parked work; it has to contain the plan for the parked work. The Django stack on `feat/django-agreement-lifecycle` is the parking artifact; `catalyst-onboarding-v2` is the forward home.

## What survives a routine branch cleanup

The parked refactor survived a repo sweep that removed 34 temporary worktrees and deleted 25 merged branches. The work lives on the published feature branches and on `main` history, not in disposable worktrees or speculative branches.

Atomic fast-forward pushes land on real branches with real tips. A repo sweep that removes temporary worktrees and merged branches cannot touch those tips without changing the published history. That is a consequence of invariant one: durable artifacts outlive routine cleanup.

## What did not change the parked work

In the 24 hours after the parking decision, a parallel hardening window merged fifteen fixes in `claude-code-plugins`: patched advisories in shipped MCP servers, upgraded `actions/cache`, `actions/github-script`, `codecov-action`, the cosign installer, `download-artifact`, `pnpm/action-setup`, and Vitest. None of those PRs touched the parked Django work. None of them needed to. The decoupling held under a load that would have broken a single-stack deployment.

The point is not that the hardening window was easy. The point is that it was possible without a deploy coordination meeting. Two repos, two lifecycles, no shared cutover.

## Use this

- **Push the refactor as `--ff-only` to a feature branch, not as a merge to `main`.** The atomic property is what makes the gate suite pin to a commit instead of a moving branch.
- **Run the full gate suite on the merged commit, including the independent reviewer.** A CI badge is the vendor's promise; a reviewer-approved badge is the team's promise.
- **Write the "do not cut over" decision as a PR, and open a successor planning repo.** The decision has to live where the next reader will find it, and the parked work has to have somewhere forward to go.

The Django stack in `catalyst-onboarding` is parked. The work is not abandoned. The five invariants held, and parking the cutover became a reversible decision instead of a one-way door.

The parked Django work and the dated parking decision: [intentsolutions pull 120](https://github.com/intent-solutions-io/catalyst-onboarding/pull/120) and [pull 124](https://github.com/intent-solutions-io/catalyst-onboarding/pull/124).

## Frequently asked questions

### How do you park a refactor without abandoning it?

Five invariants hold: the work lands as an atomic fast-forward push, the gate suite pins to the merged commit (including an independent reviewer), no production mutation happens at ship time, a "do not cut over" decision record lands in the repo, and a successor repo gives the parked work somewhere forward to go. Drop any one and the parked work becomes abandoned in slow motion.

### When should you delay a production cutover after a green merge?

Delay when a green badge sits on a moving branch, when the cutover and rollback share one failure domain, or when the "do not cut over" decision has nowhere to live. Parking keeps the new code on a feature branch with a pinned badge, so the deploy step can be rehearsed independently before the swap.

### Why not merge to main and cut over later?

A green badge on main sits on a moving target that any reset invalidates retroactively, a cutover welded to a merge is one failure domain, and a "do not cut over" decision has no place to live when main is the act of cutting over. Parking keeps work, gate results, and decision on separate durable artifacts.

## Related Posts

- [three-pass-settlement-recurring-ai-pipeline-contract](https://startaitools.com/posts/three-pass-settlement-recurring-ai-pipeline-contract/): A recurring AI pipeline contract project settles only after a third evidence pass that closes every named gap with a concrete file and pins every changed gate manifest. Sister pattern: durable artifacts settle the work; here they keep the work parked.
- [name-the-single-authority-in-a-daily-pipeline](https://startaitools.com/posts/name-the-single-authority-in-a-daily-pipeline/): When a daily pipeline runs unobserved, every concern accumulates competing authorities; the cure is to name exactly one authority per concern. Decision-22 is the named authority here.
- [link-public-surface-to-deployment-thesis](https://startaitools.com/posts/link-public-surface-to-deployment-thesis/): The publish-and-park pattern breaks the public-surface-to-deployment link on purpose; the cataloged post argues the opposite. Worth reading both before committing a migration.

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "How do you park a refactor without abandoning it?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Five invariants hold: the work lands as an atomic fast-forward push, the gate suite pins to the merged commit (including an independent reviewer), no production mutation happens at ship time, a 'do not cut over' decision record lands in the repo, and a successor repo gives the parked work somewhere forward to go. Drop any one and the parked work becomes abandoned in slow motion."
      }
    },
    {
      "@type": "Question",
      "name": "When should you delay a production cutover after a green merge?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Delay when a green badge sits on a moving branch, when the cutover and rollback share one failure domain, or when the 'do not cut over' decision has nowhere to live. Parking keeps the new code on a feature branch with a pinned badge, so the deploy step can be rehearsed independently before the swap."
      }
    },
    {
      "@type": "Question",
      "name": "Why not merge to main and cut over later?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "A green badge on main sits on a moving target that any reset invalidates retroactively, a cutover welded to a merge is one failure domain, and a 'do not cut over' decision has no place to live when main is the act of cutting over. Parking keeps work, gate results, and decision on separate durable artifacts."
      }
    }
  ]
}
