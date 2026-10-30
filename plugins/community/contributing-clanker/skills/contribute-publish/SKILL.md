---
name: contribute-publish
description: |
  Publish one prepared OSS contribution action to GitHub after a fresh human
  approval boundary. Shows the exact target, content, command, commit, and test
  evidence before any mutation. Use when local preparation is complete and
  the user explicitly asks to post a claim, create a Design Issue, comment, push
  a branch, or open a pull request. Trigger with "/contribute-publish" or
  "publish this prepared contribution".
allowed-tools:
  - Read
  - Bash(gh:*)
  - Bash(git:*)
version: "0.11.0"
author: "Jeremy Longshore <jeremy@intentsolutions.io>"
license: "MIT"
compatibility: "Model-agnostic; requires git and an authenticated GitHub CLI with permission for the approved action"
tags: [oss, contributions, github, publishing, human-approval]
argument-hint: "[prepared-review-packet]"
model: inherit
effort: high
---

# Contribute Publish

## Overview

Perform exactly one approved GitHub mutation from a completed local preparation
packet. This skill has no authority to discover unrelated work, create persistent
state, install dependencies, or expand the approved scope.

## Prerequisites

- A completed `contribute-prepare` review packet with final content, target,
  commit SHA, changed files, and passing evidence.
- GitHub CLI authenticated through the user's existing credential store.
- A clean understanding of the upstream's contribution, disclosure, CLA/DCO,
  branch, and review policies.

## Mandatory approval boundary

Before any external action, show all of the following:

1. GitHub repository and issue or pull-request target.
2. Exact action and command category (`issue comment`, `issue create`, `pr create`,
   `pr comment`, or `git push`).
3. Complete content that will be posted, or the exact branch/ref that will be
   pushed.
4. Exact prepared commit SHA and changed-file list when code is involved.
5. Test and lint evidence.
6. Any warnings, overrides, AI-use disclosure, CLA, or DCO requirement.

Then ask for explicit approval for that exact action. Approval must appear in the
current conversation after the review packet. Earlier blanket permission,
installation, authentication, repository ownership, or approval of a different
target does not count.

## Instructions

1. Use Read only to inspect the final prepared packet and approved body file.
2. Present the mandatory approval boundary below.
3. Wait for fresh approval for the exact action.
4. Execute once, read back the resulting GitHub object, and stop.

- Execute only the approved action and target.
- Use the user's existing `gh` authentication; never request, read, or print a
  token.
- Do not merge, force-push, approve reviews, bypass repository rules, close an
  issue, or delete a branch unless that exact operation received its own review
  packet and explicit approval.
- If content or the target changes after approval, present the revised packet and
  ask again.
- After execution, read back the resulting GitHub object and report its URL and
  authoritative state.
- On failure, report the error and stop. Do not broaden permissions or retry with
  a more powerful command.

## Supported actions

```bash
gh issue comment "$ISSUE_NUMBER" --repo "$REPOSITORY" --body-file "$APPROVED_FILE"
gh issue create --repo "$REPOSITORY" --title "$APPROVED_TITLE" --body-file "$APPROVED_FILE"
git -C "$APPROVED_WORKTREE" push "$APPROVED_REMOTE" "$APPROVED_REFSPEC"
gh pr create --repo "$REPOSITORY" --head "$APPROVED_HEAD" --base "$APPROVED_BASE" \
  --title "$APPROVED_TITLE" --body-file "$APPROVED_FILE"
```

These are examples, not permission to run them. Never combine multiple mutations
under one approval unless the review packet explicitly lists each one.

## Examples

- `publish this approved claim comment` — show the final comment and target,
  obtain fresh approval, post once, then read back the issue comment URL.
- `open the prepared pull request` — verify the prepared SHA and checks, show the
  exact base/head/title/body, obtain fresh approval, create once, and read back
  the pull request state.
- `push this prepared branch` — show the exact worktree, remote, commit, and
  refspec; approval applies only to that push.

## Output

Return the action performed, repository and target, resulting URL, resulting
state read back from GitHub, and any remaining local-only follow-up.

## Error handling

| Condition | Response |
|---|---|
| No fresh explicit approval | Stop without mutation |
| Packet lacks tests, SHA, target, or final content | Return to `contribute-prepare` |
| GitHub rejects the action | Report the error; do not bypass controls |
| Target/content changed | Invalidate approval and present a new packet |

## Resources

- [Approval contract](references/approval-contract.md)
- [GitHub CLI authentication](https://cli.github.com/manual/gh_auth_status)
