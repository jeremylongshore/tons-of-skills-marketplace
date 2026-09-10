---
name: windsurf-hello-world
description: 'Create a first Devin Desktop (formerly Windsurf) Cascade and Supercomplete experience.

  Use when starting with Windsurf, testing your setup,

  or learning basic Cascade and Supercomplete workflows.

  Trigger with phrases like "windsurf hello world", "windsurf example",

  "windsurf quick start", "first windsurf project", "try windsurf".

  '
allowed-tools: Read, Write, Edit
argument-hint: "[scope or requirements]"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- windsurf
- cascade
- supercomplete
- quickstart
compatibility: Designed for Claude Code
---
# Devin Desktop Hello World

## Overview

Devin Desktop is the current name for Windsurf. This walkthrough exercises Cascade Code and Chat modes, Supercomplete, and inline Command editing with a disposable example.

## Prerequisites

- Completed `windsurf-install-auth` setup
- Devin Desktop open with a disposable or version-controlled project folder

## Tool Use

- Use `Read` to inspect only the repository files and configuration needed for the request.
- Use `Write` only for a new artifact the user requested; never write credentials or unreviewed production configuration.
- Use `Edit` for bounded, reviewable changes and preserve unrelated user work.

## Instructions

### Step 1: Experience Supercomplete (Tab Completions)

Open any code file and start typing. Supercomplete predicts your intent based on recent edits, cursor movement, and surrounding context.

```typescript
// Type this in a new file: hello.ts
// After typing "function greet", Supercomplete suggests the rest

function greet(name: string): string {
  // Just type "return" and press Tab -- Supercomplete fills the template literal
  return `Hello, ${name}! Welcome to Windsurf.`;
}

// Start typing "const users" -- Supercomplete predicts array based on greet() context
const users = ["Alice", "Bob", "Charlie"];
users.forEach(user => console.log(greet(user)));
```

Key Supercomplete behaviors:

- Press **Tab** to accept a suggestion
- Press **Esc** to dismiss
- Suggestions appear as gray ghost text
- Uses recent editor activity and surrounding context for intent prediction

### Step 2: Use Cascade Code Mode

Open Cascade and select Code mode. Use the visible command or current keybinding because imported editor profiles can change shortcuts.

```
Prompt to try:
"Create a REST API endpoint in src/api.ts using Express that serves
the greet function. Include error handling for missing name parameter."
```

Cascade will:

1. Create `src/api.ts` with Express setup
2. Import the greet function
3. Add error handling
4. Show diffs for your review

**Review and accept/reject each file change before Cascade proceeds.**

### Step 3: Use Cascade Chat Mode

Switch to Chat mode (toggle in Cascade panel) for questions that don't need file edits:

```
Prompt: "Explain the difference between Code and Chat mode in Cascade"

Expected response: Code mode can create/modify files and run terminal commands.
Chat mode answers questions without touching your codebase.
```

### Step 4: Try Inline Command (Cmd/Ctrl+I)

Highlight a block of code in the editor and press Cmd/Ctrl+I to invoke Command mode:

```
Select the greet function, then type:
"Add JSDoc documentation and input validation"
```

Cascade edits the selected code inline and presents a diff for explicit acceptance or rejection.

### Step 5: Use @ Context Mentions

In Cascade chat, use @ to inject specific context:

```
@src/api.ts -- reference a specific file
@src/       -- reference an entire directory
@web        -- search the web for current info
```

Example prompt with context:

```
"@src/api.ts Add rate limiting middleware to all endpoints"
```

## Output

- Working Supercomplete experience with Tab completions
- Cascade Code mode: file creation and modification
- Cascade Chat mode: codebase questions without edits
- Inline Command mode: targeted code editing
- @ context mentions for precise AI context

## Error Handling

| Issue | Cause | Solution |
|-------|-------|----------|
| No Supercomplete suggestions | Extension disabled | Click status bar widget, enable autocomplete |
| Cascade not editing files | In Chat mode | Switch to Code mode in Cascade panel |
| Slow Cascade response | Large workspace | Add `.codeiumignore` for build artifacts |
| @ mention not working | File not indexed | Wait for indexing to complete (status bar) |

## Examples

### Terminal Command Mode

```
Press Cmd/Ctrl+I in the terminal, then type:
"Find all TypeScript files that import express"

Windsurf generates: find src -name "*.ts" -exec grep -l "express" {} \;
```

### Preview Your App

```
Ask Cascade: "Preview the API server in the browser"
Windsurf opens an in-IDE preview tab with your running app.
Click elements in the preview to send them back to Cascade for edits.
```

## Resources

- [Focused first-party references](references/official-docs.md)
- [Windsurf Getting Started](https://docs.devin.ai/desktop)
- [Cascade Overview](https://docs.devin.ai/desktop/cascade/cascade)
- [Autocomplete Tips](https://docs.devin.ai/desktop/autocomplete/tips)

## Related Skill

Continue with `windsurf-local-dev-loop` to turn this disposable exercise into a repeatable, test-gated development workflow for a real repository.
