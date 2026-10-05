---
title: "Git Rebase Conflict: Verify Post-Push HEAD, Not Exit 0"
description: "On a shared checkout, the post-push HEAD, not the exit code, is what tomorrow's cron inherits. When a rebase conflicts mid-push, exit 0 hides a wedged tree."
date: "2026-10-03"
tags: ["git", "ci-cd", "debugging", "automation", "devops"]
featured: false
canonical: "https://startaitools.com/posts/exit-zero-is-not-push-ok/"
---
A cron job that prints "OK" has not proven anything if it pushed onto a working tree still mid-rebase. Exit code, in the shape most wrappers report it, only answers one narrow question: did the last command in the pipeline return zero. It does not say what tomorrow's run will inherit: whether the working tree the next run sees is actually clean.

A scheduled job on this site answered that question wrong for six days, and the answer hid in plain sight. The September monthly calibration and the September retro never produced. Every nightly wrapper that touched the same checkout kept logging success.

## How the lie surfaced

A 90-day attribution audit kicked off the morning of 2026-10-03 and dispatched six read-only investigators in parallel. The first finding came back from the automation investigator, not the skill investigator. The primary checkout (the one every daily wrapper runs from) had been stuck in a half-finished rebase since the 2026-09-27 weekly feedback sweep. Local HEAD was a few commits behind origin/master, and the conflict sat in a tracked file. Six days of "OK" runs had been operating on that wedged tree.

When the rebase conflicted, the job did not abort it. The push step returned exit 1, the wrapper caught that, the wrapper then returned 0, and the next morning's run inherited a working tree with a rebase in progress and unmerged paths. The daily wrapper that depends on a clean tree kept running against a tree that was not clean. Nothing else in the chain noticed.

The 09-27 weekly feedback sweep is the cron that wrote the colliding row. Two writers append to the same JSONL tail every week, the sweep rebase-conflicted on a tail the other writer had also extended, and the wrapper did not abort. Every run since then found the same half-staged state and either no-op'd or quietly layered more work on top of it.

## Why a side investigation, not the cron, found this

Every wrapper that touched the checkout logged OK. The push log, the feedback sweep log, the monthly calibrate log, and every nightly script that inherited the tree printed the same green word and exited zero. Six days of unbroken OK, on every dashboard a team member might have looked at. The cron was the wrong place to look for the failure, because the cron's job was to print OK, and the cron's view of itself was unchanged.

The reason the attribution audit caught it is that [the audit does not trust a green dashboard](https://startaitools.com/posts/a-green-result-only-covers-what-it-ran/). The audit does not ask the cron whether it ran. It asks for the artifact the cron was supposed to produce, and looks for the file in the place the cron was supposed to put it. The September retro should have been in `content/monthly-recaps/` on a specific date, and there was no file. The September calibration should have been in `.claude/skills/blog-backfill/methodology/calibration-2026-09.md`, and there was no file. Two missing artifacts, on two different schedules, on the same checkout, are a fingerprint that one shadowed crash can wear.

A wrapper-level green is the absence of an error message. An attribution audit is the presence of an artifact. The first is cheap to log and easy to fake. The second is expensive to skip and hard to fake. Cron authors should not rely on the first. Cron consumers should not trust the first as proof of work. The lie lives in the gap between those two ideas.

## The broken path

The function that needed the fix lives in `scripts/blog/lib-cron-common.sh` and is called `push_with_rebase` (the same plumbing the prior piece on [Git plumbing for an unattended cron on a shared checkout](https://startaitools.com/posts/git-plumbing-unattended-cron-shared-checkout/) walks through). Its job is straightforward: try the push, fall back to `git pull --rebase --autostash` if rejected, retry, give up after a bounded number of attempts. The version that shipped to 2026-09-27 looked like this, with the relevant slice:

```bash
for ((i = 1; i <= attempts; i++)); do
  if git push origin "$branch" >> "$log_file" 2>&1; then
    return 0
  fi
  if [ "$i" -eq "$attempts" ]; then
    _log "$log_file" "push still rejected after $attempts attempt(s)"
    return 1
  fi
  _log "$log_file" "push rejected, rebasing onto origin/$branch (attempt $i/$attempts, autostash on)"
  if ! git pull --rebase --autostash origin "$branch" >> "$log_file" 2>&1; then
    _log "$log_file" "rebase onto origin/$branch FAILED (conflict, or a rebase is already in progress)"
    return 1
  fi
done
return 1
```

Two things are wrong. First, when the `git pull --rebase` failed, the function returned 1 without ever running `git rebase --abort`. That left `rebase-merge/` (or `rebase-apply/`) on disk, which is what a rebase-in-progress looks like to the next command. Second, the wrapper around `push_with_rebase` had its own final check whose exit zero the log reported. The log said OK. The tree said something else.

## The fix

The new path runs `git rebase --abort` whenever the rebase directory exists, and only returns 1 after the abort succeeds. A failed abort is logged as FATAL because the only safe next step is for a human to look at the checkout.

```bash
if ! git pull --rebase --autostash origin "$branch" >> "$log_file" 2>&1; then
  _log "$log_file" "rebase onto origin/$branch FAILED"
  if [ -d "$(git rev-parse --git-path rebase-merge)" ] || [ -d "$(git rev-parse --git-path rebase-apply)" ]; then
    if git rebase --abort >> "$log_file" 2>&1; then
      _log "$log_file" "aborted the failed rebase; checkout restored"
    else
      _log "$log_file" "FATAL: could not abort the failed rebase; checkout needs manual repair"
    fi
  fi
  return 1
fi
```

The local commit survives the abort. `--autostash` only re-applies the unstaged work after a successful rebase, and a failed rebase leaves the autostash in place, which is what we want here. The next run finds a tree with a clean staging area and one local commit waiting.

## Why not the obvious approach

The tempting fix is `git pull --rebase` paired with `--ff-only`, or a wrapper-level guard that refuses to run if `rebase-merge/` exists. Both fail in the same way. The wrapper deliberately stages work before pushing (a post file, an image, the production-side metadata), so the local commit ahead of origin is the desired state, and `--ff-only` will refuse to advance. The original design chose rebase because the canonical state is on origin, and the wrapper's job is to put the local commit on top of the latest tip. There is no clean tree to fast-forward into. There is a working tree mid-publish.

A wrapper-level guard helps the next run, but the run that returned 1 inside the rebase would still have left the tree wedged, and the wrapper around it would still have reported 0. A guard at the wrapper level hides the problem from later wrappers. It does not fix the function that caused it. The function itself has to leave a clean tree when it returns 1.

Another tempting move is a pre-flight check at the top of the wrapper itself: refuse to run if `rebase-merge/` is on disk. That guard would have caught the next six days of wrappers, and it is the kind of thing that reads clean in review. It is also a guard against the symptom, not against the function that produces it. The next wrapper the team writes for a different schedule would not copy it. The next time the push function is refactored, the function would still return 1 mid-rebase and still leave the tree wedged. The pre-flight guard is portable to other wrappers only if the team remembers to copy it into every wrapper, and the team that wrote the function is the team that forgot the abort. Putting the fix where the bug lives, the function itself, means one place to maintain and one place to test.

## The test that fails on the old code

The regression lives in `tests/test_blog_pipeline.py` and reproduces the 2026-09-27 collision: two clones of the same bare repo, a base commit, one side appends "theirs" and pushes, the other side appends "ours" and tries to push. The pull --rebase conflicts, the function returns 1, the test asserts the rebase directory is gone and the local commit is still on disk.

```python
def test_push_with_rebase_aborts_conflicting_rebase(tmp_path):
    """A conflicting pull --rebase must not leave the shared checkout mid-rebase.

    Reproduces the 2026-09-27 weekly feedback-sweep failure: two writers append
    to the same JSONL tail, the push is rejected, the rebase conflicts, and the
    primary checkout stayed stuck in a rebase that every later wrapper inherited.
    """
    lib = Path(__file__).resolve().parents[1] / "scripts/blog/lib-cron-common.sh"
    env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.invalid",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.invalid",
           "INTENT_RUNTIME": "/nonexistent", "HOME": str(tmp_path)}
    env.pop("BLOG_RUN_MANIFEST", None)
    script = f"""
set -e
cd "{tmp_path}"
git init -q --bare -b master remote.git
git clone -q remote.git a 2>/dev/null; cd a
echo base > f.jsonl; git add f.jsonl; git commit -qm base; git push -q origin master
cd ..; git clone -q remote.git b; cd b
echo theirs >> f.jsonl; git commit -qam theirs; git push -q origin master
cd ../a; echo ours >> f.jsonl; git commit -qam ours
. "{lib}"
set +e
push_with_rebase master "{tmp_path}/log" 3; echo "rc=$?"
test -d "$(git rev-parse --git-path rebase-merge)" && echo STUCK || echo CLEAN
git log -1 --format=%s
"""
    out = subprocess.run(["bash", "-c", script], env=env, capture_output=True, text=True)
    assert "rc=1" in out.stdout, out.stdout + out.stderr
    assert "CLEAN" in out.stdout, out.stdout + out.stderr
    assert out.stdout.strip().endswith("ours"), "local commit must survive the abort"
```

Three assertions, in order: the function returns 1 (the push did not succeed), the rebase directory is gone (the checkout is not wedged), the local commit titled "ours" is still on the tip of the branch (the autostash survived). Run against the old code, the first assertion would pass and the second would fail. Run against the new code, all three pass. The full local suite stays green (976 passed, 1 skipped), and CI goes green on PR #109.

## Also shipped

- bobs-big-brain-umbrella #107: filed the K8 cross-organization scope note and exported the bead closures for 2026-10-03/04
- intent-outreach 0.3.0: gated `save_run` like `runCampaign`, validated CLI flags, recorded prompt provenance, single-sourced the version, re-pinned the audit harness
- whiteglove-pdf 1.0.0: gated render, mechanical QA receipts, themes as data
- claude-code-plugins #1603 and #1604: sanitized three example plugin logs and resolved CodeQL medium alerts in the podium, databricks-workspace-mcp, and analytics packages
- claude-code-plugins CI #1602: cancel superseded PR runs, stop the publisher taking a runner on every PR

## What the regression test catches that the wrapper can't

The test runs in 0.6 seconds and reproduces the six-day collision. The test is structural, not a smoke test: it asserts the rebase directory is gone, the local commit is still on the tip, and the function returns non-zero. Against the old code, the first assertion would have passed and the second would have failed, and the test would have said so. Against the new code, all three pass. The function is tested where the bug lived, and a future reordering of the function body that drops the abort would fail this same test the same way.

A wrapper-level pre-flight check is harder to write this way. The wrapper has nothing to assert on until a previous run left a half-finished rebase. A test against a pre-flight check would have to seed that rebase from outside the function, which is fixture plumbing the cron path does not own. The test against the function seeds the half-finished rebase inside the test script, the function runs once, and the test asserts on the function's actual output. The function is a black box, the wrapper is a chain, and a chain is harder to test in isolation than a box.

Operationally, the test means a rebase conflict on any schedule that uses `push_with_rebase` is caught before the next push returns, not six days later when a side investigation notices the missing artifact. That is the difference between a one-cycle blip on a dashboard and a monthly retro that never produced.

## How do I make a git push function safe on a shared checkout?

A safe push function on a shared checkout treats the post-push HEAD, not the exit code, as the receipt. When `git pull --rebase` conflicts, run `git rebase --abort` before returning, because `--autostash` only re-applies the local commit after a successful rebase. The next scheduled run inherits the tree the function actually left, not the one it claimed to leave.

## Use this

- Verify the post-push HEAD matches the working tree, not the exit code. A push that returned 0 is a necessary but not sufficient condition. The check is `git rev-parse HEAD` against the remote tip, and on a shared checkout the check belongs inside the push function, not the wrapper.
- On any failed rebase inside a push function, run `git rebase --abort` before returning. The autostash survives an aborted rebase, so the local commit is not lost, and the next scheduled run inherits a tree that is not wedged. A failed abort is the only case where the function should refuse to return a code and instead page.
- [Write the regression test first](https://startaitools.com/posts/working-is-not-proven/). The test reproduces the exact collision (two clones, one shared file, conflicting appends) and asserts the rebase directory is gone, the local commit is still on the tip, and the function returns non-zero. Without that test, the next wrapper that reorders the function body will reintroduce the same silent six-day outage.

## Related posts

- [Git Plumbing for an Unattended Cron on a Shared Checkout](https://startaitools.com/posts/git-plumbing-unattended-cron-shared-checkout/)
- [Every Verdict Carries the Scope It Actually Ran](https://startaitools.com/posts/a-green-result-only-covers-what-it-ran/)
- [Every Claim Needs a Shipped Source and an Executable Proof](https://startaitools.com/posts/working-is-not-proven/)
