---
name: windsurf-core-workflow-a
description: 'Execute Devin Desktop''s primary workflow: Cascade Code mode for multi-file
  agentic coding.

  Use when building features, refactoring across files, or performing complex code
  tasks.

  Trigger with phrases like "windsurf cascade write", "windsurf agentic coding",

  "windsurf multi-file edit", "cascade code mode", "windsurf build feature".

  '
allowed-tools: Read, Write, Edit, Bash(npm:*), Grep
argument-hint: "[scope or requirements]"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- windsurf
- cascade
- code-mode
- agentic
compatibility: Designed for Claude Code
---
# Windsurf Core Workflow A — Cascade Code Mode

## Overview

Devin Desktop is the current name for Windsurf. Cascade Code mode is its agentic editing workflow: it can create and modify files, call tools, run approved terminal commands, inspect diagnostics, and iterate on failures.

## Prerequisites

- Devin Desktop with Cascade enabled
- `.devin/rules/project.md` configured (see `windsurf-sdk-patterns`)
- Git initialized with clean working tree

## Tool Use

- Use `Read` to inspect only the repository files and configuration needed for the request.
- Use `Grep` to locate relevant settings, rules, logs, or code without broad collection.
- Use `Write` only for a new artifact the user requested; never write credentials or unreviewed production configuration.
- Use `Edit` for bounded, reviewable changes and preserve unrelated user work.
- Use only the command-scoped `Bash` entries declared in frontmatter, with non-destructive checks before mutations.

## Instructions

### Step 1: Create a Git Checkpoint

Always commit or stash before a Cascade session. Cascade writes directly to your files.

```bash
git add -A && git commit -m "checkpoint: before cascade session"
# Or for uncommitted work:
git stash push -m "pre-cascade stash"
```

### Step 2: Open Cascade in Code Mode

Open the Cascade panel and select **Code** rather than **Chat**. Keyboard shortcuts can vary by imported profile, so use the visible command or confirm the current binding before documenting it.

- Create and modify files
- Run terminal commands (with Turbo or per-command approval)
- Install dependencies
- Read terminal output for debugging
- Open browser previews

### Step 3: Write an Effective Prompt

Structure your prompt with scope, specifics, and constraints:

```
"In src/services/, create a NotificationService that:
1. Sends email via Resend API (already in package.json)
2. Sends Slack messages via webhook URL from env
3. Uses the Result<T,E> pattern from src/types/result.ts
4. Includes retry logic with exponential backoff (max 3 retries)
5. Add unit tests in tests/services/notification.test.ts
Don't modify any existing files except to add exports."
```

### Step 4: Review Cascade's Plan and Execution

Cascade shows its reasoning and plan before executing:

```
Cascade output flow:
1. "I'll create the notification service with email and Slack support..."
2. Creates src/services/notification.ts (shows diff)
3. Creates tests/services/notification.test.ts (shows diff)
4. Runs: npm install resend (if needed)
5. Runs: npx vitest run tests/services/notification.test.ts
6. Reports results
```

**Review each file diff in the Cascade output.** Then:

- **Revert** individual steps by hovering over a step and clicking the revert arrow
- **Revert all** to return to the state before the Cascade session
- Create named **checkpoints** for complex multi-step sessions

### Step 5: Iterate on Errors

If tests fail, Cascade retains context about what it just did:

```
"The test for sendSlack is failing with 'fetch is not defined'.
Fix it by using the node:test built-in fetch mock."
```

Cascade reads the error, understands its own recent changes, and applies targeted fixes.

### Step 6: Use @ Mentions for Precision

```
@src/types/result.ts — force Cascade to read this file for the Result pattern
@src/services/       — reference the entire services directory for consistency
@web resend API docs  — search the web for current Resend documentation
```

## Output

- Multi-file code changes applied by Cascade
- Terminal commands executed (installs, tests, builds)
- Test results confirming implementation correctness
- Reviewable diffs for every file change

## Error Handling

| Issue | Cause | Solution |
|-------|-------|----------|
| Cascade modifies wrong files | Vague prompt | Specify exact file paths and constraints |
| Changes break existing tests | No constraint on existing code | Add "don't modify existing files" to prompt |
| Cascade loops on error | Insufficient context | Paste the full error message, reference relevant files |
| Code mode is unavailable | Account, policy, or quota restriction | Check the visible account and organization state |
| Cascade ignores `.devin/rules/project.md` | Wrong path, trigger, or file over 12,000 characters | Validate frontmatter and split the workspace rule |

## Examples

### Full-Stack Feature

```
"Add a user profile page:
1. Create app/profile/page.tsx as a Server Component
2. Create app/profile/edit/page.tsx as a Client Component with form
3. Add GET /api/profile and PUT /api/profile route handlers
4. Use the existing UserSchema from lib/types/user.ts for validation
5. Style with Tailwind matching the existing design system
6. Add tests for both API routes"
```

### Refactoring Task

```
"Extract the authentication logic from src/middleware/auth.ts into:
- src/services/auth.ts (JWT validation, token refresh)
- src/services/session.ts (session management)
Update all imports across the codebase. Run tests after."
```

## Resources

- [Focused first-party references](references/official-docs.md)
- [Cascade Code and Chat modes](https://docs.devin.ai/desktop/cascade/cascade)
- [Cascade Checkpoints](https://docs.devin.ai/desktop/cascade/cascade)

## Related Skill

Continue with `windsurf-core-workflow-b` to convert repeated session guidance into the appropriate Rules, Skills, Workflows, or Memories layer.
