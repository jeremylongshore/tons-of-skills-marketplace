---
name: cursor-hello-world
description: 'Create your first project using Cursor AI features: Tab, Chat, Composer,
  and Inline Edit.

  Triggers on "cursor hello world", "first cursor project", "cursor getting started",
  "try cursor ai",

  "cursor basics", "cursor tutorial".

  '
allowed-tools: Read, Write, Edit, Bash(cmd:*)
version: 1.19.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- cursor
- cursor-hello
compatibility: Designed for Claude Code
---
# Cursor Hello World

## Overview

Practice Tab, Chat, Inline Edit, and Composer in a disposable sample project before using them on production code. Every proposed diff remains subject to normal review, tests, security checks, and repository rules.

## Instructions

1. Create a non-sensitive example project and enable the approved privacy setting.
2. Use one feature at a time, give clear constraints, and inspect every generated diff before accepting it.
3. Run focused tests/formatting after applying a change; reject or revert unexpected edits.
4. Move to real repositories only after rules, indexing exclusions, and review expectations are configured.

A hands-on 10-minute walkthrough of Cursor's four core AI features: Tab Completion, Chat, Inline Edit, and Composer.

## Setup

```bash
mkdir cursor-hello && cd cursor-hello
npm init -y
npm install typescript tsx @types/node --save-dev
npx tsc --init
```

Open the project in Cursor: `cursor .` (or File > Open Folder).

## Exercise 1: Tab Completion

Create `src/utils.ts`. Start typing and let Tab complete:

```typescript
// Type this much:
export function formatCurrency(amount: number, currency: string

// Tab suggests:
export function formatCurrency(amount: number, currency: string = 'USD'): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
  }).format(amount);
}
```

Press **Tab** to accept the full suggestion, or **Cmd+Right Arrow** to accept word-by-word.

### Try These Prompts for Tab

Type a comment describing what you want, then start the function:

```typescript
// Validate an email address using regex
export function validateEmail(

// Sort an array of objects by a key
export function sortBy<T>(

// Calculate the distance between two lat/lng points in km
export function haversineDistance(
```

Tab reads your comment and generates the implementation.

## Exercise 2: Chat (Cmd+L)

Open Chat with `Cmd+L`. Try these prompts:

**Ask about your code:**

```
@src/utils.ts
What does the formatCurrency function do? Does it handle edge cases
like negative numbers or very large values?
```

**Generate new code:**

```
Write a TypeScript function that converts a nested object
to a flat key-value map with dot-separated keys.
Example: { a: { b: 1 } } → { "a.b": 1 }
```

**Debug a concept:**

```
Explain the difference between Promise.all() and Promise.allSettled()
with code examples showing when to use each.
```

Chat responds with explanations and code snippets. Click **Apply** on any code block to insert it into your editor.

## Exercise 3: Inline Edit (Cmd+K)

Open `src/utils.ts`. Select the `formatCurrency` function body. Press `Cmd+K`.

Type your instruction:

```
Add support for locale parameter with default 'en-US'.
Handle NaN input by returning '$0.00'.
```

Cursor shows the diff inline:

- Green = added lines
- Red = removed lines

Press `Cmd+Y` to accept, `Esc` to reject.

### Inline Edit Quick Tasks

Select any code and press `Cmd+K` with instructions like:

- `"Add TypeScript types"`
- `"Refactor to use early returns"`
- `"Add error handling"`
- `"Convert to async/await"`
- `"Add JSDoc documentation"`

## Exercise 4: Composer (Cmd+I)

Press `Cmd+I` to open Composer. Ask it to create a complete feature:

```
Create a simple task manager module:

1. src/types/task.ts - Task interface with id, title, completed, createdAt
2. src/services/task-service.ts - TaskService class with:
   - addTask(title: string): Task
   - completeTask(id: string): Task
   - listTasks(): Task[]
   - deleteTask(id: string): void
3. src/index.ts - Demo script that creates 3 tasks, completes one, lists all

Use in-memory storage (Map). Include TypeScript types throughout.
```

Composer shows all files it will create/modify. Review each diff, then click **Apply All**.

### Run the Result

```bash
npx tsx src/index.ts
```

## Feature Comparison Summary

| Feature | Shortcut | Use For | Scope |
|---------|----------|---------|-------|
| **Tab** | Automatic | Line/block completions while typing | Current cursor position |
| **Chat** | `Cmd+L` | Questions, explanations, code snippets | Conversation-based |
| **Inline Edit** | `Cmd+K` | Edit selected code with instructions | Selected code block |
| **Composer** | `Cmd+I` | Multi-file generation and refactoring | Multiple files |

## Next Steps After Hello World

1. **Add project rules**: Create `.cursor/rules/` with coding standards (see cursor-rules-config skill)
2. **Index your codebase**: Open a real project and wait for indexing (see cursor-codebase-indexing skill)
3. **Learn @-mentions**: Use `@Files`, `@Codebase`, `@Docs` in Chat (see cursor-context-management skill)
4. **Configure your model**: Try different models for different tasks (see cursor-model-selection skill)

## Enterprise Considerations

- Hello World exercises do not send sensitive code to AI providers -- safe for evaluation
- Enable Privacy Mode before using Cursor with production codebases
- Tab completions work immediately; Chat and Composer require active subscription or BYOK API key

## Output

- A small runnable sample change created through reviewed Cursor interactions.
- A demonstrated review loop: inspect diff, test, accept or revert, and retain source-control history.

## Error Handling

| Condition | Safe response |
|---|---|
| Generated diff touches unrelated files | Reject it, start a scoped request, and inspect active context/rules. |
| Output includes insecure or untested code | Do not accept it; request a constrained revision and use normal review/testing. |
| Sensitive material is included in context | Stop the session, remove the context, and follow the exposure procedure. |

## Examples

Ask Inline Edit to add a type to one selected function, inspect the proposed diff, then run the focused test. If it touches other files or violates project rules, reject it and restate the task with the exact file and acceptance condition.

## Resources

- [Cursor Getting Started](https://docs.cursor.com/get-started/overview)
- [Cursor Keyboard Shortcuts](https://docs.cursor.com/kbd)
- [Cursor Feature Overview](https://cursor.com/features)
