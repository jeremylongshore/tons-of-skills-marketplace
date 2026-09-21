---
name: cursor-git-integration
description: 'Integrate Git workflows with Cursor IDE: AI commit messages, @Git context,
  diff review, and conflict

  resolution. Triggers on "cursor git", "git in cursor", "cursor version control",
  "cursor commit",

  "cursor branch", "@Git".

  '
allowed-tools: Read, Write, Edit, Bash(cmd:*)
version: 1.19.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- cursor
- git
- workflow
compatibility: Designed for Claude Code
---
# Cursor Git Integration

## Overview

Use Cursor's Git features as a view and drafting aid while preserving repository branch protection, reviews, signed checks, and human ownership of commits/merges.

## Prerequisites

- A clean or recoverable working tree, repository contribution rules, and correct remote identity.
- Required checks and reviewer/approval expectations for the target branch.

## Instructions

1. Inspect status and diff before staging; stage only reviewed, intended files.
2. Draft but verify commit messages and never include secrets or unrelated changes.
3. Run required local checks, push through the normal branch/PR workflow, and resolve feedback with evidence.
4. Use revert or a new corrective commit for mistakes rather than rewriting shared history.

## Output

- A scoped, reviewable Git change with validation evidence and a normal revert path.

## Error Handling

| Condition | Safe response |
|---|---|
| Working tree has unrelated changes | Separate/stash them before staging. |
| Generated commit message misstates work | Edit it to match the actual diff. |
| Protected branch rejects push | Use the approved PR/check process; do not weaken controls. |

## Examples

Review a Cursor-generated diff, stage only its intended files, run the focused suite, and push a topic branch for review. If an accidental file is staged, unstage it and recheck the diff before committing.

Leverage Cursor's AI features within Git workflows: AI-generated commit messages, `@Git` context for code review, merge conflict resolution, and branch management.

## Source Control Panel

Access with `Cmd+Shift+G` / `Ctrl+Shift+G`:

```
┌─ SOURCE CONTROL ────────────────────────────────┐
│  main ← current branch                         │
│                                                 │
│  Changes (3)                                    │
│    M  src/api/users.ts                         │
│    A  src/api/products.ts                      │
│    M  prisma/schema.prisma                     │
│                                                 │
│  Commit message: [✨ Generate with AI]          │
│  [Commit]  [Commit & Push]                      │
└─────────────────────────────────────────────────┘
```

## AI-Generated Commit Messages

Click the sparkle/AI icon next to the commit message input. Cursor reads the staged diff and generates a message:

**Example output:**

```
feat: add product catalog CRUD API with Prisma model

- Add Product model to Prisma schema with name, price, category fields
- Create GET/POST/PUT/DELETE endpoints in src/api/products.ts
- Add Zod validation for product creation and update inputs
```

**Tips for better commit messages:**

- Stage related changes together (not unrelated edits)
- The AI reads the diff, so clean diffs produce better messages
- Edit the generated message before committing if needed
- Configure Conventional Commits in project rules:

```yaml
# .cursor/rules/git-conventions.mdc
---
description: "Git commit conventions"
globs: ""
alwaysApply: true
---
Use Conventional Commits format:
- feat: new feature
- fix: bug fix
- refactor: code restructure without behavior change
- docs: documentation only
- test: adding or updating tests
- chore: maintenance tasks

Keep subject line under 72 characters.
Body explains WHY, not WHAT (the diff shows what).
```

## @Git Context in Chat

Use `@Git` in Chat or Composer to include git context:

### @Git (Working State)

```
@Git

Review my uncommitted changes. Check for:
- Any debugging code left in (console.log, debugger)
- Missing error handling
- Type safety issues
- Potential performance problems
```

`@Git` includes the diff of all uncommitted changes (staged + unstaged).

### @Git (Branch Diff)

```
@Git

Summarize all changes in this branch compared to main.
What features/fixes were implemented?
Are there any breaking changes?
```

When on a feature branch, `@Git` shows the cumulative diff between your branch and main.

## Merge Conflict Resolution

When a merge conflict occurs, use Chat for AI assistance:

```
@src/api/users.ts

I have a merge conflict in this file. The markers show:
<<<<<<< HEAD (my changes)
  Added email validation with Zod
=======
  Added phone number field to user schema
>>>>>>> feature/phone-support

Help me resolve this to keep both changes:
- Keep the Zod email validation from my branch
- Add the phone number field from the other branch
- Ensure the Zod schema includes phone validation too
```

### Systematic Conflict Resolution Workflow

```bash
# 1. Start the merge
git merge feature/other-branch

# 2. List conflicted files
git diff --name-only --diff-filter=U

# 3. For each conflicted file, open in Cursor and use Chat:
#    @the-conflicted-file.ts
#    "Resolve the merge conflict. Keep both sets of changes where possible."

# 4. After resolving, stage and commit
git add .
git commit -m "merge: resolve conflicts between feature branches"
```

## Code Review with AI

### Reviewing a PR Before Pushing

```
@Git

I'm about to push this branch for code review. Act as a senior
reviewer and identify:
1. Code smells or anti-patterns
2. Missing test coverage
3. Security vulnerabilities
4. Performance concerns
5. Documentation gaps
```

### Reviewing Specific Commits

```
# In terminal, get the diff for a specific commit:
git show abc1234 > /tmp/commit-diff.txt

# In Chat:
@/tmp/commit-diff.txt
Review this commit for correctness and best practices.
```

## Branch Management Workflows

### Feature Branch Setup

```bash
# Create and switch to feature branch
git checkout -b feature/add-favorites

# Open Cursor, use Chat to plan:
# Cmd+L:
# "@Codebase I need to add a favorites feature.
#  What existing patterns should I follow?"

# Work with Composer/Tab...
# When ready:
git add .
# Use AI commit message via Source Control panel
git push -u origin feature/add-favorites
```

### Pre-Push Review

```
@Git

Before I push, check this branch for:
[ ] No .env or secret files staged
[ ] No TODO/FIXME comments that should be addressed
[ ] All new functions have type annotations
[ ] No commented-out code blocks
```

## Git-Aware Project Rules

Create rules that leverage git context:

```yaml
# .cursor/rules/pr-standards.mdc
---
description: "Standards for AI-assisted code review"
globs: ""
alwaysApply: false
---
When reviewing code changes (@Git):
- Flag any function without error handling
- Flag any API endpoint without input validation
- Flag any database query without parameterization
- Suggest test cases for untested code paths
- Check for proper HTTP status codes (not always 200)
```

## Integrations

### GitLens Extension

GitLens works in Cursor and enhances git features:

- Inline blame annotations
- File history and line history
- Interactive rebase editor
- Commit graph visualization

Install from Open VSX: `Cmd+Shift+X` > search "GitLens"

### Cursor Blame

Cursor has built-in `Cursor Blame` that attributes code to the AI agent that generated it, helping teams track which code was AI-generated vs human-written.

## Enterprise Considerations

- **Commit signing**: Configure `git commit -S` for GPG/SSH signed commits (works normally in Cursor's terminal)
- **Protected branches**: AI-generated commit messages still go through normal branch protection rules
- **Audit trail**: AI-generated code is committed under the developer's name, not the AI's
- **Pre-commit hooks**: Enforce linting, testing, and secret scanning via git hooks -- AI-generated code must pass all checks

## Resources

- [Cursor @Git Documentation](https://docs.cursor.com/context/@-symbols/@-git)
- [Git Documentation](https://git-scm.com/doc)
- [Conventional Commits](https://www.conventionalcommits.org)
