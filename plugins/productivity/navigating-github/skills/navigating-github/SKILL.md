---
name: navigating-github
description: "First-time GitHub setup and interactive git learning. Walks users from\n\
  zero to a working GitHub repo, then teaches git through 9 hands-on\nlessons on their\
  \ actual project. Adapts language and depth to skill\nlevel \u2014 inferred from\
  \ environment, not questionnaires. Two modes:\nSetup (guided onboarding) and Learn\
  \ (progressive curriculum from\ncommits to CI/CD). Use when the user asks to set\
  \ up GitHub, learn\ngit, or says \"teach me github\". Trigger with \"set up my repo\"\
  ,\n\"help me with github\", \"teach me github\", \"learn git\", \"what are\nbranches\"\
  , \"teach me PRs\", or \"how do I use github\".\n"
allowed-tools: Read, Write, Glob, Grep, Bash(git:*), Bash(gh:*), Bash(ssh:*), Bash(test:*),
  Bash(echo:*), AskUserQuestion
version: 2.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- github
- git
- beginner
- intermediate
- advanced
- vibe-coding
- version-control
- learning
- onboarding
compatibility: Designed for Claude Code
  and Continue
---
# Navigating GitHub

First-time GitHub setup and interactive git learning. Get set up, then learn by doing.

## Table of Contents

1. Overview — 2. Prerequisites — 3. Instructions — 4. Modes — 5. Examples — 6. Output — 7. Resources

## Overview

**Problem:** Getting started with GitHub is the #1 barrier for people building with AI. Beginners stall at setup, don't understand commits vs pushes vs PRs, and have nobody to walk them through it hands-on. AI coding tools can run git commands, but they don't teach you what those commands mean or guide you through setup from scratch.

**Solution:** Walk users through GitHub setup step by step, then teach git and GitHub through 9 progressive hands-on lessons on their actual project. Every lesson uses do-then-explain: run the command, see the result, then understand why. Adapts language and depth to skill level automatically.

## Prerequisites

- Terminal access with `git` installed
- `gh` CLI installed (Setup handles installation if missing)
- GitHub account (Setup handles creation if missing)

## Instructions

### Step 1 — Route

Determine mode from the user's request. Act immediately — no preamble.

1. No `.git/` directory OR `gh auth status` fails → **Setup** (check with `test -d .git` and `gh auth status`)
2. Keywords "teach", "learn", "what are", "how do", "explain", "lesson" → **Learn**
3. Keywords "set up", "new repo", "init", "get started" → **Setup**
4. Generic ("help me with github") → check environment, route to **Setup** if no repo, otherwise offer lesson menu

### Step 2 — Infer Skill Level

Each mode runs `git status` as part of its normal operation. Infer level from those signals — no extra commands:

- Only `main` branch + short/vague commit messages → **Beginner**
- A few branches + descriptive commits → **Intermediate**
- Branch naming conventions + conventional commits → **Advanced**
- Complex history, multiple remotes, CI configured → **Expert**

Only ask via `AskUserQuestion` when signals are genuinely ambiguous. Read [`references/skill-assessment-guide.md`](references/skill-assessment-guide.md) for the full adaptive behavior matrix. Apply:

| Level | Language | Depth | Autonomy |
|-------|----------|-------|----------|
| Beginner | Analogies, zero jargon | Explain everything | Execute and teach along the way |
| Intermediate | Light jargon, define terms | Explain the why | Execute, ask to confirm |
| Advanced | Standard vocabulary | Brief rationale only | Suggest, let user decide |
| Expert | Terse, technical | None unless asked | Assist only |

## Modes

### Setup — Guided Onboarding

The core experience for first-time users. Walk through each step interactively, skipping anything already done. Run each check, explain what it means, fix what's missing.

**Sequence:** Check `gh auth status` → install `gh` if missing (detect OS, give command) → run `gh auth login` (walk through browser OAuth) → check `git config user.name` and `user.email` (set if missing) → check for `.git/` (run `git init` if missing) → generate `.gitignore` by detected project type → create first commit → run `gh repo create` (let user choose public/private) → push → show the repo URL.

Skip completed steps. Explain each step at the inferred level. After completion, offer the lesson menu: "Repo is set up. Say 'teach me github' or run `/github-learn` to start learning."

### Learn — Interactive Curriculum

Hands-on lessons using real commands on the user's actual project. Every lesson follows **do-then-explain**: run a real command, observe the result, THEN explain what happened. Verify understanding after each step before proceeding.

Read [`references/learning-curriculum.md`](references/learning-curriculum.md) for the full curriculum. Route by trigger:

**Beginner track:**

- "teach me github" / "learn github" → **GitHub 101** — commits, push, the basics
- "what are branches" / "teach me branches" → **Branching Basics** — create, switch, see the difference
- "teach me PRs" → **Your First PR** — branch, push, create PR, merge

**Intermediate track:**

- "teach me branching strategies" → **Branch Workflows** — naming, feature branches, staying current
- "teach me code review" → **PR Review Flow** — review, comment, approve
- "how do I collaborate" → **Team Git** — forks, upstream sync, co-authoring

**Advanced track:**

- "teach me rebase" → **Rebase vs Merge** — interactive rebase, squash, clean history
- "teach me CI/CD" / "github actions" → **GitHub Actions** — write a workflow, watch it run
- "how do code review apps work" → **Review Ecosystem** — CodeRabbit, Copilot Review, and the ecosystem (read [`references/github-review-apps.md`](references/github-review-apps.md))

After each lesson: summarize what was learned (2-3 bullets), give a small challenge to try solo, suggest the next lesson.

**Teaching rules:**

- Run commands one at a time, explain after each result
- If the user makes a mistake, fix it together — mistakes are learning moments
- If the user already knows something, skip ahead
- If the user seems confused, slow down and simplify
- Create a safe practice branch before exercises that modify the repo
- Never push to `main`/`master` during lessons — always branch first
- Never commit secrets — check for `.env`, API keys before staging

## Examples

**Setup** (no .git, no auth):

```
User: "help me with github"
Agent: [checks — no .git, gh not authenticated]
Agent: "Starting from scratch. First, connect to GitHub..."
Agent: [walks through gh auth login, git config, git init, gh repo create]
Agent: "Repo is live at github.com/user/project. Run /github-learn to
       start learning commits and branches."
```

**Learn** (beginner, GitHub 101):

```
User: "teach me github"
Agent: "Make a small change to any file — add a comment, fix a typo."
User: [edits a file]
Agent: "Now save that change: git add README.md"
Agent: "That moved the change to the staging area — like putting a letter
       in an envelope. Now seal it: git commit -m 'Update README'"
Agent: [verifies understanding before moving to next step]
```

**Learn** (advanced, rebase):

```
User: "/github-learn rebase"
Agent: "Create a branch with 3 small commits, then we'll squash them."
Agent: [guides through git rebase -i, explains pick/squash/fixup]
```

## Output

Calibrate all output to the inferred skill level. Beginner: plain English with analogies, explain every command. Intermediate: concise summaries, explain rationale. Advanced: minimal commentary. Expert: raw output only. Read [`references/git-concepts-glossary.md`](references/git-concepts-glossary.md) when a term definition is needed.

## Error Handling

- **`gh` not installed**: Detect missing CLI, provide platform-specific install instructions (`brew install gh`, `apt install gh`, `winget install GitHub.cli`), then resume setup.
- **Authentication failure**: If `gh auth status` fails, walk through `gh auth login` with browser OAuth flow. If token is expired, run `gh auth refresh`.
- **No git remote**: If `git remote -v` returns empty, guide through `gh repo create` or `git remote add origin <url>`.
- **Merge conflict during lesson**: Explain what a conflict is at the user's level, show the conflict markers, and walk through resolution step by step.
- **Detached HEAD**: Detect with `git status`, explain in plain language, and recover with `git checkout <branch>`.

## Resources

- [`references/learning-curriculum.md`](references/learning-curriculum.md) — 9 progressive lesson plans from beginner through advanced
- [`references/git-concepts-glossary.md`](references/git-concepts-glossary.md) — term definitions at beginner and technical levels
- [`references/skill-assessment-guide.md`](references/skill-assessment-guide.md) — adaptive behavior matrix with level-up and level-down signals
- [`references/safety-rules.md`](references/safety-rules.md) — branch protection, secret detection, destructive operation guards
- [`references/error-recovery-playbook.md`](references/error-recovery-playbook.md) — conflict resolution, auth repair, detached HEAD, rebase recovery
- [`references/github-review-apps.md`](references/github-review-apps.md) — CodeRabbit, Copilot Review, Greptile, CodeQL, Qodo
- [`references/claude-github-platforms.md`](references/claude-github-platforms.md) — platform capabilities across Claude Code, Cursor, Windsurf, and others
