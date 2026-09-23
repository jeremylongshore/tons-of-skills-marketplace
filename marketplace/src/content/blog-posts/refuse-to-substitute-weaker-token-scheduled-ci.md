---
title: "Refuse to Substitute a Weaker Token in Scheduled CI"
description: "A scheduled CI workflow that falls back to a weaker token opens PRs that re-trigger no required checks. PR #1563 closes that fallback in update-npm-stats.yml."
date: "2026-09-22"
tags: ["ci-cd", "github-actions", "security", "automation", "devops"]
featured: false
canonical: "https://startaitools.com/posts/refuse-to-substitute-weaker-token-scheduled-ci/"
---
A scheduled CI workflow can exit 0 and show green in the action log while never running the required checks that branch protection is supposed to enforce. I shipped a one-line fix in PR #1563 that turns that silent failure mode into a red workflow that refuses to start.

The scheduled workflow is `update-npm-stats.yml` in `claude-code-plugins`. It opens a daily PR carrying the npm download stats diff for every plugin. A fine-grained PAT was added to that workflow for one reason: PRs opened with `GITHUB_TOKEN` cannot re-trigger required checks (the anti-recursion rule, by design), so any required check that depends on the PR's own diff will skip itself. The PAT bypasses that rule because it counts as a different actor.

When `BOT_PR_TOKEN` expired or was unset, the workflow silently fell back to `GITHUB_TOKEN`. Three things were true at once. Workflow exited 0. Action log printed green. The opened PR carried the stats diff. And the PR's checks list stayed empty or stale, because every required check on that workflow was either suppressed by the `GITHUB_TOKEN` recursion rule or skipped entirely. Branch protection rules said checks required while no required check ever ran. The protection's promise was structurally vacuous, and it looked exactly like a passing build.

The 2026-08 audit caught it. The fix this week is the absence of a fallback path:

```yaml
# update-npm-stats.yml
- name: Require BOT_PR_TOKEN (no silent fallback)
  env:
    BOT_PR_TOKEN: ${{ secrets.BOT_PR_TOKEN }}
  run: |
    if [ -z "$BOT_PR_TOKEN" ]; then
      echo "::error::BOT_PR_TOKEN is absent or empty (expired, revoked, or never set). This workflow refuses to fall back to GITHUB_TOKEN because its PRs cannot re-trigger required checks. Rotate the fine-grained PAT (contents:write + pull-requests:write) and re-run."
      exit 1
    fi
    echo "BOT_PR_TOKEN present."
```

`::error::` fails the step red on GitHub. `exit 1` aborts before any push happens. The comment block in the YAML names the why so the next person to look at it does not relitigate the decision. There is no longer a path that silently substitutes a less-capable token.

The same PR also added `scripts/regenerate-after-bump.mjs`, a dependency-ordered projection regenerator that runs the projection pipeline in dep order and stops at the first upstream failure ("Never generate downstream projections from a failed upstream output"). Same shape, applied to projection drift.

## Also shipped

- PR #1564 "docs(marketplace): align onboarding with repository Node floor". Pinned the documented Node version in `installation.md` and added `check-node-version.test.mjs` so the docs claim and the runtime claim stay matched.
- PR #1476 "feat(sources): register reviewed HOL Guard source baseline". Narrowed HOL Guard external source to non-executable surface and withheld the verification badge until maintainer review, preserving projections.
- searchcarriers-tools PR #4 (separate repo, v0.2.0). Rebuilt SearchCarriers skills around verified carrier workflows. The npm-stats PR is partly what keeps download counts visible for plugins like these.

## Use this

- Add a "no silent fallback" step to any scheduled CI workflow that opens PRs and depends on required checks re-running. Test it by deleting the secret in a sandbox repo and confirming the workflow fails red before push.
- Audit every `||` in your scheduled workflows that resolves to a default token. If either operand reduces capability in a way that affects required-check recursion, treat the line as a bug.
- When a step says "fall back gracefully", ask what the graceful path hides. Silent substitution is the failure mode; loud refusal is the gate.

## Related Posts

- [Reachability Is Not Freshness](https://startaitools.com/posts/reachability-is-not-freshness/) (2026-09-17): a status page that 200'd while serving two-month-old data.
- [Wrong-Mode Green Is Not a Gate](https://startaitools.com/posts/wrong-mode-green-is-not-a-gate/) (2026-07-22): a freshness gate that accepted the wrong mode flag and printed all-green.
- [Git Plumbing for an Unattended Cron on a Shared Checkout](https://startaitools.com/posts/git-plumbing-unattended-cron-shared-checkout/) (2026-09-21): same unattended-pipeline theme, different failure mode.
