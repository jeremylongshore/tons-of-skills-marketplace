---
title: "Three Self-Healing Classes for an Unattended AI Pipeline"
description: "Three self-healing classes keep an unattended AI pipeline quiet: repair rounds, depth-capped provider failover, and nightly catch-up of older dates."
date: "2026-09-20"
tags: ["automation", "ci-cd", "ai-agents", "devops"]
featured: false
canonical: "https://startaitools.com/posts/three-classes-of-self-healing-and-slow-is-not-failed/"
---
A nightly blog pipeline used to fail the same way every time the AI provider hiccuped: page a human at 4am, wait for a coffee, then retry. The page was the system's loudest output and its dumbest. Three classes of self-healing now sit between the failure and the page. This post is about what those classes are, what the meta-lesson underneath them turned out to be, and the BLOCKER independent review caught before the change shipped.

The pipeline writes one post a night on a strict cron at 04:00. It runs headless against a model, runs an in-process contract verifier against the result, then hands the file to a deterministic lander (the script that commits and publishes; the model never touches git). The producer is the AI step. The verifier is the gate. The lander is the publish. If the verifier says no, the producer gets the verifier's exact message back and tries again. If the provider is the problem, a different provider runs the same attempt. If neither helped, the night ends in quarantine (set aside instead of published) and the next morning runs catch-up. Each class has a hard ceiling.

## Class 1: repair rounds

When the producer finishes and the verifier rejects the result for a nameable reason, the same session is resumed in the same workspace with the verifier's exact text handed back as the prompt. `claude -p --resume <run id>` keeps the context, so the model sees its own output and the gate's complaint together, which is the cheap path to fixing a real gap. The contract re-verifies after each round, exactly as after the first attempt. The cap is `BLOG_REPAIR_ROUNDS` (2). Two shots, no more. Repair is honest only when the same author can plausibly do better on the same artifact with the same complaint.

The hard limit is what the loop will never do. The repair prompt and the call site both refuse to edit the pipeline, the gates, the skill, or the contract. Touching git is out. Relabelling a failing verdict as passing is out. A repair that wants to widen its own scope stops being repair.

## Class 2: depth-capped provider failover

If the run is still not accepted after the repair rounds, and the router did not say stop, the wrapper re-invokes itself once with the other full-toolchain provider. `auto` (MiniMax-backed Claude) and `claude` (OAuth Claude) backstop each other. The child gets a fresh session id, a fresh workspace, and inherits the pipeline lock so two writers do not race for the same date. Depth is capped at 1. A failover that fails over again is just a loop with extra steps. The child stays silent on its own failure and the parent pages only when both have failed, not when one has succeeded on the second try.

The router decides the action deterministically before any model is asked. Provider-fault regexes match the run log; unsafe-pattern regexes force stop; repairable patterns match the verifier's captured message. Anything unrecognised falls through to failover, the cheapest honest next move. The cheap model is asked last, only to classify, and only its one-word answer is accepted. A model never widens what the loop may do.

## Class 3: nightly catch-up of missed dates

Repair and failover save a night when one provider or one attempt fails. They cannot save a night when everything is down. Catch-up does. After the night's own date, the scheduled run looks back `BLOG_CATCHUP_DAYS` (3), finds dates with no post on the deploy branch using one `git grep` against origin/master, and tries each, newest first, as a quiet child that may itself repair and fail over. Attempts per date are capped (`BLOG_CATCHUP_MAX_ATTEMPTS`, 3) and recorded in `catchup-state.json` (a small JSON file in the local state directory). A date that reaches the cap is reported exactly once. Between children the loop waits for the release workflow to settle, because the lander's post push is a plain fast-forward the release bot races.

The whole night has a hard ceiling. Each child runs under `timeout --kill-after=120 <remaining>`, where the remaining budget is recomputed between children. The night cannot run into the next 04:00 fire and hold the lock while that night's own run exits as LOCKED without a trace. The 3-attempt cap means a date that cannot be written stops costing tokens. A date that cannot succeed is asked to stop.

```
timeout --kill-after=120 "$remaining_budget" \
  bash -c "$run_one_child $date"
```

The cap is what makes "tonight's run completed" actually mean tonight's run completed. Without it, a wedged date holds the lock for hours and the next morning's run sees a lock file instead of a clean tree.

## The meta-lesson: slow is not failed

A deploy that takes 25 minutes deserves PENDING, not a 4am page. The state machine has to honor that distinction, or the noise this work exists to remove comes back wearing a different shirt. PENDING means: the work is done, the system is alive, the world is just slow. FAILED means: the work is not done, page someone. Conflating them is the single most expensive mistake in unattended automation, because the page fires for a successful night and gets ignored, and the next real failure is the one nobody answers.

PENDING is not a special case. It is the third terminal state next to OK and FAILED, and the catch-up loop, the failover parent, and the deploy settle wait all have to agree on which is which. If any one of them reads PENDING as FAILED, the pipeline pages for a night that succeeded. Independent review of the catch-up code caught exactly that hole before it shipped.

## The BLOCKER independent review caught

The failover parent looked for "Overall STATUS: OK" only. A failover child that published and ended PENDING (page slow, not page broken) was read as "failover also failed" and paged at 4am for a night that had succeeded. The exact noise the change exists to remove, left on the one path the merge had not touched. The fix widened the parent's accept list to OK, PENDING, and the idempotent no-op, the same test the catch-up loop uses. PENDING is now PENDING everywhere it shows up. FAILED stays FAILED.

Three SHOULD-FIX items came out of the same review. `wait_for_release_to_settle` treated an erroring or rate-limited `gh` as settled, which says nothing; it now falls back to the blind wait. `published_dates()` counted a post with `draft=true`, which would have treated a draft as published forever; drafts are excluded; a real post on the same date still covers it. And the catch-up budget is now checked inside each child via the timeout wrapper, not just before the night starts. One canary case covered the whole repair: primary provider 429s, failover publishes, lander returns 13, parent logs "published by claude", exits 0, sends no page.

## Off switches

Three classes of self-healing, three off switches. `BLOG_RECOVERY=0` disables repair and failover together. `BLOG_REPAIR_ROUNDS=0` disables just the repair loop. `BLOG_CATCHUP_DAYS=0` disables the catch-up sweep. When something looks wrong at 4am, the easiest first move is to set the relevant off switch, not to widen the loop. A pipeline that self-heals but cannot be turned off is a pipeline that hides its failures until the off switch is what you actually need.

## What broke on the way

The pipeline sat behind a recovery case on 2026-09-13 where a 4am page was needed because nothing tried to recover. The 2026-09-04 disk-exhaustion incident (the run log landed "100% to 100% silently for three weeks") and the August authentication outage both taught the same lesson: the gap between "ran" and "succeeded" is where unattended systems lose to humans who are asleep. Recovery is the gap made smaller. Catch-up is the gap closed.

## Also shipped

Refactor Phase 1b moved logic from monolithic shims into typed packages: `scripts/blog/blogpipe/contract.py`, `errors.py`, `jsonio.py`, `roles.py`, `transcript.py` (PR 90, 1112 additions across 12 files), then `state.py`, `frontmatter.py`, `publication.py` (PR 91, 921 additions across 15 files). PR 93 added `glossary.json` (22 house terms) and a new advisory lint that checks whether a stranger can follow a post on first read. The deterministic weekly feedback sweep wrote auto-confirms (`57a91bd0`). Yesterday's Hustle P1 Tier 1 post landed today (`0a5144f8`).

## Use this

- Distinguish PENDING from FAILED in every unattended loop's terminal state. A check that is green on one has proved nothing about the other, and the page that fires for a successful night gets ignored, and the next real failure is the one nobody answers.
- Cap repair rounds and failover depth in the code, not in the prompt. A loop that can widen itself is a loop that will.
- Make the catch-up budget a per-child check via `timeout --kill-after=120 <remaining>`, not just a pre-night one. A wedged child holding the lock until 04:00 is the failure mode the cap exists to prevent.

## Related Posts

- [The Pipeline Landed Its Own Output Today](https://startaitools.com/posts/the-pipeline-landed-its-own-output-today/)
- [The BitLocker Helper Lifetime Receipt Pack Ran a Full Day](https://startaitools.com/posts/the-helper-lifetime-receipt-pack-ran-for-a-full-day/)
- [Reachability Is Not Freshness](https://startaitools.com/posts/reachability-is-not-freshness/)
