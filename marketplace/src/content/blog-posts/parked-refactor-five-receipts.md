---
title: "Park a Refactor with Five Receipts"
description: "A parked refactor stays recoverable when it leaves five named artifacts: atomic push, draft PR, decision doc, full bundle, and a successor repo. Each is verifiable."
date: "2026-10-09"
tags: ["refactoring", "migration", "deployment", "devops", "decision-records", "publish-and-park"]
featured: false
canonical: "https://startaitools.com/posts/parked-refactor-five-receipts/"
---
A refactor that reached the default branch with a green badge hides a second decision inside it. The build converged. The deploy did not. The honest options are cut over today, in a week, or ever, and welding the build to the deploy forces that second decision into rollback theater even when the right answer is to wait months. Parking the refactor removes the deploy pressure. Parking it without five named receipts turns the work into abandonment the moment attention moves.

Yesterday the Flask to Django refactor on `catalyst-onboarding` reached that exact fork. The forensic audit it had lived under for weeks said the second application was not converging on production. About 26,000 lines of Django code sat next to about 24,200 lines of the Flask release, reachable only through a console script and seventeen management commands that nothing in `deploy/compose.yaml` started. The audit's recommendation B was salvage into a clean Django v2 branch. The owner chose to publish and park the work as it stood, then start forward planning in a separate repository rather than carry the code or history.

## The five receipts

A parked refactor stays recoverable when its day leaves five named artifacts. Each one is small to produce and fast to verify. If any one is missing, recoverability is a story you are telling yourself.

**Atomic push to origin.** All unpushed work lands as a single, fast-forward update to a feature branch. `git push origin <branch>` succeeds once. The receiving repository holds every commit that the local checkout holds. No rebases happen after the push. Anything split into multiple pushes or pushed after a rebase leaves the repository telling a different story than the local checkout, and that gap is the kind of thing that only surfaces during rollback.

**Draft PR against the default branch.** A pull request exists, set to draft, pointing at the branch the production release still reads from. The draft flag says the owner is not asking for review yet. The PR title and body carry the parking intent so a future reader does not have to reconstruct it from commit messages. Yesterday the Django work pushed to `catalyst-onboarding` opened PR #120 in draft state and stayed there.

**Dated decision document.** A short record names the parked refactor, the date it was parked, and the conditions under which un-parking makes sense. The document is committed to the repository, not floating in chat or in a ticket. A future reader who reaches the default branch can answer three questions without asking anyone: what was parked, when, and what would change the call.

**Full bundle of the parked state.** A self-contained backup of the repository as it stood at parking time, including the audit, the SHA256SUMS, the bundle file, and the tracked-tree patch. The bundle lives outside any single host and is reproducible from the SHA sums. The catalyst-onboarding parking event generated one at `~/backups/catalyst-onboarding-preserve-2026-10-09` the night before, holding the forensic audit (111 KB), the audit addendum (31 KB), the bundle file (4.5 MB), and the patch (641 KB).

**Successor repo.** A separate, public repository where the replacement is designed against the live service's behavior, not carried as code or history. Creating the successor is the receipt that says forward planning starts somewhere, not nowhere. The catalyst-onboarding-v2 repository opened at commit d0f6719 with governance, planning docs under `000-docs` (each repo's numbered folder of dated records), beads (a tracked task record in the repo's issue database) initialized under the prefix `catalyst-v2`, and a single planning epic (a parent task that groups related work items). No code. The receipt is the empty code, deliberately chosen.

Each one is a folder or a flag a stranger can check in under a minute.

## Why a bundle, not a tag

A tag on the parked commit sounds like enough. Two reasons it is not. A tag stays in the same hosting account that may be the one you are moving away from, and recovery depends on that account still being reachable. A bundle is a file you can copy onto three different hosts before the parking event closes. The SHA256SUMS file inside the bundle lets the next reader verify the parked tree byte-for-byte without trusting the host. The audit, the addendum, and the tracked-tree patch travel with the bundle so the reader does not need the live repository to understand the state. A tag gives you a pointer. A bundle gives you the thing itself.

## The path forward

Parking does not close the refactor. It defers the cutover call. The parking event opens `catalyst-onboarding-v2` with a planning-phase foundation and decision 22 in the original repo explaining when un-parking is the right move. The Flask release keeps running. The Django code stays reachable as reference, not as a deployment target, until a future planning cycle re-affirms the rebuild against the live service's actual behavior. That re-affirmation is a separate decision the parked artifacts make possible to make deliberately, instead of by drift.

## Use this

- Before you call a parked refactor done, write down the five receipts and check each one. Atomic push, draft PR, dated decision document, full bundle, successor repo. If any is missing, the parking is abandonment.
- Generate the bundle the night before the parking event, not the morning of. The bundle captures the state you actually decided on, not the state you were still editing when the commit happened.
- Open the successor repo in the same parking event, even if it starts empty. The empty commit at d0f6719 is the receipt that forward planning has somewhere to land. Forward planning without a home is just a wish.

Forward planning for the Django rebuild lives at [github.com/intent-solutions-io/catalyst-onboarding-v2](https://github.com/intent-solutions-io/catalyst-onboarding-v2).

## Related Posts

- [park-the-cutover-keep-the-work](https://startaitools.com/posts/park-the-cutover-keep-the-work/): The publish-and-park pattern, day 1: five invariants that turn parking from abandonment into a recoverable refactor decision.
- [git-plumbing-unattended-cron-shared-checkout](https://startaitools.com/posts/git-plumbing-unattended-cron-shared-checkout/): Atomic fast-forwards let a daily cron run against the shared checkout without clobbering other work.
