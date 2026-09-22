---
name: windsurf-local-dev-loop
description: 'Configure Devin Desktop (formerly Windsurf) local development workflow with Cascade, Previews,
  and terminal integration.

  Use when setting up a development environment, configuring Turbo mode,

  or establishing a fast iteration cycle with Windsurf AI.

  Trigger with phrases like "windsurf dev setup", "windsurf local development",

  "windsurf dev environment", "windsurf workflow", "develop with windsurf".

  '
allowed-tools: Read, Write, Edit, Bash(npm:*), Bash(pnpm:*), Grep
argument-hint: "[scope or requirements]"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- windsurf
- workflow
- development
- turbo-mode
compatibility: Designed for Claude Code
---
# Windsurf Local Dev Loop

## Overview

Set up a fast, AI-augmented local development workflow using Windsurf's Cascade, Turbo mode, Previews, and terminal integration. The goal is a tight loop: edit with Cascade, preview in-IDE, iterate, test, commit.

## Prerequisites

- Windsurf authenticated and project open
- Node.js 18+ or Python 3.10+
- Git initialized in project

## Tool Use

- Use `Read` to inspect only the repository files and configuration needed for the request.
- Use `Grep` to locate relevant settings, rules, logs, or code without broad collection.
- Use `Write` only for a new artifact the user requested; never write credentials or unreviewed production configuration.
- Use `Edit` for bounded, reviewable changes and preserve unrelated user work.
- Use only the command-scoped `Bash` entries declared in frontmatter, with non-destructive checks before mutations.

## Instructions

### Step 1: Create .devin/rules/project.md for Project Context

```markdown
<!-- .devin/rules/project.md - placed at project root, committed to git -->

# Project: my-app

## Stack
- Language: TypeScript (strict mode)
- Framework: Next.js 14 (App Router)
- Styling: Tailwind CSS v3
- Testing: Vitest + Testing Library
- Package manager: pnpm

## Architecture
- Server Components by default
- Client Components only when state/interactivity needed
- API routes in app/api/
- Business logic in lib/services/
- Types in lib/types/

## Conventions
- Named exports, never default
- async/await, never raw .then()
- zod for all runtime validation
- Error handling: Result pattern in services
```

### Step 2: Configure .codeiumignore

```gitignore
# .codeiumignore - exclude from AI indexing (same syntax as .gitignore)
node_modules/
.next/
dist/
build/
coverage/
*.min.js
*.map
.env
.env.*
```

### Step 3: Set Up Turbo Mode for Fast Terminal Execution

Turbo mode lets Cascade auto-execute terminal commands without asking permission for each one.

**Enable:** Windsurf Settings > Cascade > Terminal Execution Level > Turbo

**Configure safety lists:**

```json
// Settings (JSON) — search "cascadeCommands"
{
  "windsurf.cascadeCommandsAllowList": [
    "npm", "pnpm", "npx", "node", "tsc",
    "vitest", "jest", "eslint", "prettier",
    "git status", "git diff", "git log", "git add"
  ],
  "windsurf.cascadeCommandsDenyList": [
    "rm -rf", "sudo", "git push --force",
    "git reset --hard", "DROP TABLE", "shutdown"
  ]
}
```

### Step 4: Use Previews for UI Development

Ask Cascade to preview your web app:

```
"Start the dev server and preview the app"
```

Cascade starts the server and opens an in-IDE Preview tab. From the Preview:

- Click **"Send element"** (bottom-right) to select a UI element and send it to Cascade
- Console errors are automatically forwarded to Cascade for debugging
- Iterate by describing changes: "Make the header sticky and add a dark mode toggle"

### Step 5: The Dev Loop

```
1. Open Cascade (Cmd/Ctrl+L)
2. Describe the feature or fix
3. Cascade edits files and runs commands (Turbo mode)
4. Preview updates in-IDE (hot reload)
5. Click broken elements → send to Cascade
6. Cascade fixes → repeat until correct
7. Run tests: "Run vitest for the files you changed"
8. Commit: "Commit these changes with message: add dark mode toggle"
```

### Step 6: Terminal Integration

Use Cmd/Ctrl+I in the terminal for natural language commands:

```
Type: "find all files importing the Button component"
Windsurf generates: grep -rl "import.*Button" src/

Type: "run tests for auth module only"
Windsurf generates: npx vitest run src/auth/
```

Highlight terminal errors and press Cmd/Ctrl+L to send to Cascade for diagnosis.

## Output

Produce a repository-local development recipe with setup commands, durable Rules or `AGENTS.md`, ignore boundaries, test and lint gates, preview instructions, and a definition of done. Keep environment-specific secrets out of committed customization files.

## Error Handling

| Issue | Cause | Solution |
|-------|-------|----------|
| Cascade not seeing project context | No `.devin/rules/project.md` | Create rules file at project root |
| Slow AI suggestions | Large repo indexed | Add `.codeiumignore` |
| Turbo mode running dangerous commands | Missing deny list | Configure `cascadeCommandsDenyList` |
| Preview not loading | Dev server not started | Ask Cascade to start it first |
| Hot reload not working | Preview disconnected | Close and re-open Preview tab |

## Examples

### Quick Project Bootstrap

```
Cascade prompt: "Initialize a new Next.js 14 project with TypeScript,
Tailwind CSS, and Vitest. Set up the folder structure matching
our .devin/rules/project.md conventions."
```

### Debug-Fix Loop

```
1. See error in terminal or Preview console
2. Highlight error text → Cmd/Ctrl+L → "Fix this error"
3. Cascade reads error, finds root cause, applies fix
4. Preview auto-reloads → verify fix
```

## Resources

- [Focused first-party references](references/official-docs.md)
- [Windsurf Terminal Docs](https://docs.devin.ai/desktop/terminal)
- [Windsurf Previews](https://docs.devin.ai/desktop/previews)
- [Cascade Overview](https://docs.devin.ai/desktop/cascade/cascade)

## Related Skill

Continue with `windsurf-sdk-patterns` to formalize the working loop as reviewed workspace Rules, MCP configuration, and reusable team guidance.
