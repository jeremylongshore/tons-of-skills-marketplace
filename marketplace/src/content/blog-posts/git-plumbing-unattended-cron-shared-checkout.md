---
title: "Git Plumbing for an Unattended Cron on a Shared Checkout"
description: "When an unattended cron has to commit to a shared, often-dirty checkout, git plumbing beats porcelain: hash-object + commit-tree + push survives concurrent sessions, behind-branch state, and push races."
date: "2026-09-21"
tags: ["automation", "ci-cd", "git", "devops", "ai-agents"]
featured: false
canonical: "https://startaitools.com/posts/git-plumbing-unattended-cron-shared-checkout/"
---
When an unattended cron job has to commit to a shared git checkout that other sessions may also touch, the safest move is plumbing, not porcelain. Plain `git add && git commit && git push` from inside the repo will fail the moment someone else's working tree is dirty, the local main is behind origin, or a push race lands between your fetch and your push. The mechanism below commits a single file to a remote branch without ever opening the working tree, so concurrent sessions and stale local state cannot reach it.

This is the mechanism that keeps this blog's daily posts mirroring to a sister site at 4am, and it generalizes to any cron that has to land a single file on a repo it does not own.

Porcelain fails in three ways on a shared checkout. A concurrent session can have uncommitted changes in the tree, so `git add` either pulls in someone else's file or refuses to commit. Local `main` can be behind origin by several commits, so `git push` rejects as non-fast-forward. And a push race between your fetch and your push can lose a commit silently. Each of these is recoverable in an interactive session, and each of them is unrecoverable at 4am when nobody is watching.

The mechanism is `publish_file_to_repo`, defined in `scripts/blog/lib-cron-common.sh`. It does five things with plumbing commands and no shell state on the working tree:

```bash
blob=$(git -C "$top" hash-object -w "$src" 2>>"$log_file") || return 1
tmpidx=$(mktemp)
if ! GIT_INDEX_FILE="$tmpidx" git -C "$top" read-tree "$base" 2>>"$log_file"; then rm -f "$tmpidx"; return 1; fi
GIT_INDEX_FILE="$tmpidx" git -C "$top" update-index --add --cacheinfo "100644,$blob,$rel" 2>>"$log_file"
tree=$(GIT_INDEX_FILE="$tmpidx" git -C "$top" write-tree 2>>"$log_file"); rm -f "$tmpidx"
[ -n "$tree" ] || return 1
commit=$(git -C "$top" commit-tree "$tree" -p "$base" -m "$msg" 2>>"$log_file") || return 1
if git -C "$top" push origin "$commit:$branch" >>"$log_file" 2>&1; then
  _log "$log_file" "published $rel -> origin/$branch"
  return 0
fi
```

`hash-object -w` writes the new file as a blob into the object database. `read-tree $base` builds a fresh index from the remote tip (re-fetched inside the loop, so `$base` is always current). `update-index --add --cacheinfo` adds the new blob to the index without touching the working tree. `write-tree` produces a tree object. `commit-tree` produces a commit object parented on the fresh remote tip. `push origin $commit:$branch` then pushes a specific SHA directly to a branch ref. The working tree was never opened. The local index was never touched. The only thing that hit the disk was the new blob in the object database, and that is overwritten harmlessly the next time anyone writes the same content.

Three guards keep this honest on the unattended path:

1. Always re-fetch `$base` inside the retry loop. Stale tip is the most common failure mode and the easiest to eliminate.
2. Retry the push up to three times. Push races between concurrent fetchers on the same remote resolve themselves in a few seconds.
3. Fail loud on exit, never silently. If the third push fails, the function returns non-zero, the caller (the daily `blog-land.sh`, the deterministic commit and push step this pipeline calls the `lander`) refuses to mark the post as published, and the post lands in `quarantine` (set aside with its evidence retained, the day's owner checkout preserved). Nothing gets half-published.

This is also why the rest of the pipeline uses a `bead` (a tracked task under Dolt version control, the durable queue a sleep writes to so the next interactive session can pick up exactly where it stopped) rather than a markdown TODO. A sleep's bead, a sleep's run, and a sleep's quarantine all stay attached to the day's evidence.

The full function plus its log and contract notes live at `scripts/blog/lib-cron-common.sh` lines ~715 to ~786. Any cron with the same shape (single file to land, shared checkout, no operator watching) can lift it as-is.

## Use this

- Replace `cd repo && git add . && git commit && git push` in any unattended pipeline that commits to a shared checkout with the five plumbing calls: `hash-object -w`, `read-tree`, `update-index --cacheinfo`, `write-tree`, `commit-tree`, then `push <sha>:branch`. The working tree is never touched.
- Always re-fetch the remote tip inside the retry loop and base the new commit on that fresh SHA. A stale local main is the most common reason porcelain pushes fail and plumbing ignores it entirely.
- Fail loud on the third push retry. Returning non-zero and quarantining the day is recoverable. Silently dropping a push is not.

## Also shipped

- Slice two of code work on the self-healing daily blog pipeline (PR #96): catch-up plus patience for missed runs.
- Worktree rebuild of PR #1470, the standalone E2E harness; force-pushed with the old head preserved on origin.
- Governance doc add for `rfisch` as a maintainer on the plugins marketplace (CODEOWNERS plus the epic-1 scorecard).
- Automated journal land for the `comehomealabama` project via `scripts/journal/mandy-land.sh`.
- The comehomealabama journal itself for 2026-09-21 (separate blog, automated, not engineering).

## Related

- [Three Self-Healing Classes for an Unattended AI Pipeline](https://startaitools.com/posts/three-classes-of-self-healing-and-slow-is-not-failed/) (2026-09-20): the dual-publish is one mechanism in the same unattended-pipeline system; that post names the three classes the daily cron sits inside.
- [The Pipeline Landed Its Own Output Today](https://startaitools.com/posts/the-pipeline-landed-its-own-output-today/) (2026-09-15): earlier post about the blog pipeline producing and landing its own output.
