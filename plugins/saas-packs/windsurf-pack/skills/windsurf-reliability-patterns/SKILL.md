---
name: windsurf-reliability-patterns
description: 'Implement reliable Devin Desktop (formerly Windsurf) Cascade workflows with checkpoints, rollback, and
  incremental editing.

  Use when building fault-tolerant AI coding workflows, preventing Cascade from breaking
  builds,

  or establishing safe practices for multi-file AI edits.

  Trigger with phrases like "windsurf reliability", "cascade safety",

  "windsurf rollback", "cascade checkpoint", "safe cascade workflow".

  '
allowed-tools: Read, Write, Edit, Bash(git:*)
argument-hint: "[scope or requirements]"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- windsurf
- reliability
- safety
- git-workflow
compatibility: Designed for Claude Code
---
# Windsurf Reliability Patterns

## Overview

Reliability patterns for safe Cascade usage: Git checkpointing, incremental task scoping, validation gates, and rollback strategies. Cascade's multi-file editing is powerful but requires discipline to avoid breaking your codebase.

## Prerequisites

- Windsurf with Cascade enabled
- Git repository initialized
- Test suite available
- Understanding of Cascade Code mode

## Tool Use

- Use `Read` to inspect only the repository files and configuration needed for the request.
- Use `Write` only for a new artifact the user requested; never write credentials or unreviewed production configuration.
- Use `Edit` for bounded, reviewable changes and preserve unrelated user work.
- Use only the command-scoped `Bash` entries declared in frontmatter, with non-destructive checks before mutations.

## Instructions

### Step 1: Always Commit Before Cascade

The most important reliability pattern: create a clean Git checkpoint before every Cascade session.

```bash
# Before starting a Cascade task
git add -A && git commit -m "checkpoint: before cascade session"

# After Cascade completes:
git diff                                    # Review all changes
npm test && npm run typecheck               # Validate

# If good:
git add -A && git commit -m "[cascade] add notification service"

# If bad:
git checkout -- .                           # Revert everything
# Or selectively:
git checkout -- src/problem-file.ts         # Revert one file
```

### Step 2: Use Feature Branches for Cascade Work

```bash
# Create dedicated branch for each Cascade task
git checkout -b cascade/add-notification-service

# Do Cascade work on this branch
# ...

# If results are good:
git checkout main && git merge cascade/add-notification-service

# If results are bad:
git checkout main && git branch -D cascade/add-notification-service
# Clean slate, main branch untouched
```

### Step 3: Scope Tasks Incrementally

Large tasks cause Cascade to make sweeping changes that are hard to review. Break into steps.

```
BAD (too broad):
"Refactor the authentication system to use JWT instead of sessions"
→ Cascade may modify 30+ files, hard to review, likely has bugs

GOOD (incremental):
Step 1: "Create src/services/jwt.ts with functions: generateToken,
         validateToken, refreshToken. Use the jose library."
Step 2: "Create tests/services/jwt.test.ts with tests for all three functions"
Step 3: "Run the tests and fix any failures"
Step 4: "Update src/middleware/auth.ts to use jwt.ts instead of
         express-session. Keep the old code commented out."
Step 5: "Run the full test suite and fix any failures"
Step 6: "Remove commented-out session code from auth.ts"

Each step: review diff → test → commit → next step
```

### Step 4: Validate After Every Cascade Edit

```bash
#!/bin/bash
# scripts/cascade-validate.sh — run after every Cascade edit
set -euo pipefail

echo "=== Post-Cascade Validation ==="

# Type check
echo "1/4 TypeScript..."
npm run typecheck || { echo "FAIL: Type errors. Ask Cascade to fix."; exit 1; }

# Lint
echo "2/4 Lint..."
npm run lint || { echo "FAIL: Lint errors. Ask Cascade to fix."; exit 1; }

# Tests
echo "3/4 Tests..."
npm test || { echo "FAIL: Test failures. Ask Cascade to fix."; exit 1; }

# Build
echo "4/4 Build..."
npm run build || { echo "FAIL: Build errors. Ask Cascade to fix."; exit 1; }

echo "ALL PASSED. Safe to commit."
```

### Step 5: Use Cascade Checkpoints

Cascade supports named checkpoints within a conversation:

```
1. Start Cascade task
2. After each significant step, Cascade shows a revert button
3. Hover over any previous step → click revert arrow → rolls back to that point
4. WARNING: Reverts are irreversible (can't undo a revert)
5. For complex tasks, commit to Git between Cascade steps for a safer safety net
```

### Step 6: Cascade Constraint Patterns

Add constraints to prompts to prevent Cascade from going too wide:

```
Scope constraints:
"Only modify files in src/services/"
"Don't change any existing tests"
"Don't modify any files except src/services/auth.ts"
"Don't install new dependencies"

Quality constraints:
"Follow the Result<T,E> pattern used in other services"
"Match the coding style in @src/services/payment.ts"
"Include error handling for all edge cases"
"Add JSDoc comments on all public functions"

Safety constraints:
"Don't modify the database schema"
"Don't change any API response formats"
"Don't remove any existing functionality"
"Keep backward compatibility with existing callers"
```

### Step 7: Team Safety Policy

```markdown
# Team Cascade Usage Policy

1. **Git checkpoint before Cascade** — non-negotiable
2. **One task per Cascade session** — don't mix refactor + feature
3. **Review every file diff** — never "accept all" without reading
4. **Run tests after accepting** — `npm test` before committing
5. **Tag AI commits** — use `[cascade]` prefix for traceability
6. **Feature branches only** — never use Cascade on main/develop
7. **Start fresh for new tasks** — close old Cascade sessions
8. **Narrow scope** — specific files > vague descriptions
```

## Output

Return a safe execution record containing the scoped task, checkpoint or branch, tests run, diff review, failure recovery, final evidence, and unresolved risks. Route changes through the repository's normal review and protected-branch workflow.

## Error Handling

| Issue | Cause | Solution |
|-------|-------|----------|
| Cascade broke the build | Accepted without testing | Git revert, add post-Cascade validation |
| Modified wrong files | Ambiguous instruction | Specify exact file paths in prompt |
| Lost good changes in revert | Reverted too broadly | Use feature branches, commit incrementally |
| Cascade contradicts earlier edit | Long conversation | Start fresh session for new tasks |
| Tests pass but logic wrong | AI-specific bug pattern | Manual code review of all Cascade changes |

## Examples

### Safe Cascade Workflow (Complete)

```bash
set -euo pipefail
# 1. Branch
git checkout -b cascade/feature-name

# 2. Checkpoint
git add -A && git commit -m "checkpoint: pre-cascade" --allow-empty

# 3. Cascade task (in Windsurf)
# ... Cascade edits files ...

# 4. Validate
npm run typecheck && npm test && npm run lint

# 5. Commit
git add -A && git commit -m "[cascade] implement feature-name"

# 6. Merge (after review)
git checkout main && git merge cascade/feature-name
git branch -d cascade/feature-name
```

### Recover from Bad Cascade Edit

```text
# Option 1: Revert all changes since checkpoint
git checkout -- .

# Option 2: Revert specific file
git checkout -- src/broken-file.ts

# Option 3: Reset to last commit
git reset --hard HEAD

# Option 4: Cherry-pick good commits from bad branch
git log cascade/feature-name --oneline  # Find good commits
git cherry-pick <good-commit-hash>
```

## Resources

- [Focused first-party references](references/official-docs.md)
- [Windsurf Cascade](https://docs.devin.ai/desktop/cascade/cascade)
- [Git Workflows](https://git-scm.com/book/en/v2/Git-Branching-Branching-Workflows)

## Related Skill

Continue with `windsurf-policy-guardrails` to convert these operator habits into enforceable terminal, repository, review, and organization controls.
