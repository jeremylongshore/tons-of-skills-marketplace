---
name: cursor-ai-chat
description: 'Master Cursor AI Chat with @-mentions, inline edit, and conversation
  patterns. Triggers on "cursor chat",

  "cursor ai chat", "ask cursor", "cursor conversation", "chat with cursor", "Cmd+L",
  "inline edit".

  '
allowed-tools: Read, Write, Edit, Bash(cmd:*)
version: 1.19.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- cursor
- cursor-ai
compatibility: Designed for Claude Code
---
# Cursor AI Chat

## Overview

Use Chat to reason about a bounded question or planned change while preserving human ownership of decisions, edits, review, and validation.

## Prerequisites

- Approved privacy/model settings and a workspace with sensitive paths excluded.
- A clear question, relevant non-sensitive files, and the project's test/review expectations.

## Instructions

1. Start a topic-scoped chat and attach only the files needed for the question.
2. Ask for assumptions, tradeoffs, and a testable proposal rather than accepting generated code blindly.
3. Verify suggestions against source, tests, security controls, and a human code review.
4. Start a new conversation when context becomes stale or the topic changes.

## Output

- A bounded explanation or proposal with assumptions, affected files, and validation steps.

## Error Handling

| Condition | Safe response |
|---|---|
| Answer contradicts repository facts | Inspect the source and restate the question with the correct files. |
| Conversation loses context | Start a new scoped chat; do not compensate by attaching the entire repository. |
| Prompt includes sensitive material | Remove it and follow the exposure process before continuing. |

## Examples

Ask Chat to compare SSE and WebSockets for the stated service, attaching only the API contract and architecture note. Require it to list assumptions and a rollout/rollback test plan; then review the proposal before authoring any change.

Master the Cursor AI Chat panel and inline edit for code assistance, debugging, and exploration.

## Core Chat Interfaces

### Chat Panel (Cmd+L / Ctrl+L)

The side-panel chat for conversational code assistance:

```
┌─────────────────────────────────┐
│  Chat                     [M]   │  ← Model selector
│─────────────────────────────────│
│  Context Pills:                 │
│  [main.ts] [utils/] [@Web]      │  ← Active context shown as pills
│─────────────────────────────────│
│  User: Explain the auth flow    │
│  in @src/auth/middleware.ts     │
│                                 │
│  AI: The middleware checks...   │
│─────────────────────────────────│
│  [Type message...]    [Send]    │
└─────────────────────────────────┘
```

**Key actions:**

- Select code in editor, then `Cmd+L` to add selection as context
- `Cmd+Shift+L` adds selection to existing chat without clearing
- Click model name in top-right to switch models mid-conversation

### Inline Edit (Cmd+K / Ctrl+K)

Surgical edits within the editor. Select code (or place cursor), press `Cmd+K`, type instruction:

```
Selected: function calculateTotal(items) { ... }

Prompt: "Add TypeScript types and handle empty array edge case"

Result: Cursor shows diff inline -- green for additions, red for removals.
        Press Cmd+Y to accept, Esc to reject.
```

Best for single-function edits, type annotations, refactoring a specific block, adding error handling.

## @-Symbol Reference

Type `@` in chat to access context sources:

| Symbol | Purpose | Example |
|--------|---------|---------|
| `@Files` | Reference specific files | `@src/utils/auth.ts` |
| `@Folders` | Include directory contents | `@src/components/` |
| `@Code` | Reference specific symbols | `@handleSubmit` function |
| `@Docs` | External documentation | `@Docs React Router` |
| `@Git` | Git diff context | `@Git` (uncommitted changes) |
| `@Codebase` | Semantic search full codebase | `@Codebase where is auth handled?` |
| `@Web` | Live web search | `@Web latest Next.js 15 changes` |
| `@Definitions` | Symbol definitions | Jump to type/function definitions |
| `@Cursor Rules` | Active project rules | Show which rules are loaded |
| `@Recent Changes` | Recent file edits | Context from recent modifications |
| `@Lint Errors` | Current lint issues | Fix active linting problems |

### @Docs: Adding Custom Documentation

Register external docs for `@Docs` lookup:

1. `Cursor Settings` > `Features` > `Docs`
2. Click `Add new doc`
3. Enter URL: `https://react.dev/reference/react` (Cursor crawls and indexes it)
4. Reference in chat: `@Docs React` then ask questions

Works with any documentation site. Good for framework APIs, internal wikis, design systems.

## Effective Prompting Patterns

### Pattern 1: Context-First Prompts

```
@src/api/orders.ts @src/types/order.ts

The createOrder function doesn't validate the shipping address.
Add Zod validation that checks: street, city, state (2-letter), zip (5 or 9 digit).
Throw a typed ValidationError if invalid.
```

### Pattern 2: Reference-Based Generation

```
@src/api/users.ts

Create a new file src/api/products.ts following the exact same pattern
as the users API. CRUD endpoints, same error handling, same response format.
Product fields: id, name, price (cents), category, createdAt.
```

### Pattern 3: Debug with Context

```
@src/hooks/useAuth.ts @Lint Errors

The useAuth hook causes an infinite re-render loop when the token expires.
The useEffect fires repeatedly. What's the root cause and how do I fix the
dependency array?
```

### Pattern 4: Architecture Discussion

```
@src/components/ @src/api/

I need to add real-time notifications. The app uses REST APIs currently.
Should I add WebSockets, SSE, or polling? Consider the existing architecture
shown in these directories.
```

## Multi-Turn Conversation Management

**Start new chats for new topics.** Long conversations degrade response quality as context fills up.

**When to start fresh:**

- Switching to a different feature or bug
- After 10+ turns on the same topic
- When responses start repeating or losing accuracy

**When to continue:**

- Iterating on the same code change
- Follow-up questions about the same file
- Asking for tests after generating code

## Model Selection for Chat

Switch models using the dropdown in chat header:

| Task | Recommended Model |
|------|------------------|
| Quick questions, explanations | GPT-4o, Claude Sonnet |
| Complex refactoring, architecture | Claude Opus, GPT-5 |
| Bug hunting, reasoning | o1, o3 reasoning models |
| Speed-critical simple tasks | cursor-small, GPT-4o-mini |
| Auto (let Cursor decide) | Auto mode |

## Chat vs Inline Edit vs Composer

| Feature | Chat (Cmd+L) | Inline (Cmd+K) | Composer (Cmd+I) |
|---------|-------------|----------------|-------------------|
| Scope | Exploration, Q&A | Single block edit | Multi-file changes |
| Context | Conversation history | Selected code | Project-wide |
| Output | Text + code snippets | Inline diff | File-level diffs |
| Best for | Understanding, planning | Quick fixes, types | Features, scaffolding |

## Enterprise Considerations

- **Privacy Mode**: Enable in Cursor Settings > General > Privacy Mode for zero data retention
- **Model governance**: Teams can restrict which models developers access via admin dashboard
- **Audit**: Chat interactions are not logged server-side when Privacy Mode is on
- **Cost control**: Use Auto mode or default to faster models; reserve Opus/GPT-5 for complex tasks

## Resources

- [Cursor Chat Documentation](https://docs.cursor.com/chat/overview)
- [@ Symbols Overview](https://docs.cursor.com/context/@-symbols/overview)
- [Keyboard Shortcuts](https://docs.cursor.com/kbd)
