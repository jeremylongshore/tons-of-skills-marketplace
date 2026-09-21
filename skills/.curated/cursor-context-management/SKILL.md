---
name: cursor-context-management
description: 'Optimize context window usage in Cursor with @-mentions, context pills,
  and conversation strategy.

  Triggers on "cursor context", "context window", "context limit", "cursor memory",
  "context management",

  "@-mentions", "context pills".

  '
allowed-tools: Read, Write, Edit, Bash(cmd:*)
version: 1.19.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- cursor
- cursor-context
compatibility: Designed for Claude Code
---
# Cursor Context Management

## Overview

Control what Cursor sees so each conversation has the minimum relevant, policy-permitted context required for a reliable answer or edit.

## Prerequisites

- A task scope, approved privacy setting, data classification, and working ignore configuration.
- Relevant files/interfaces that can be shared without credentials, customer data, or unrelated repositories.

## Instructions

1. Start with the exact files, symbols, and constraints needed; avoid indiscriminate `@Codebase` use.
2. Inspect context pills/attachments before submitting and remove stale or sensitive material.
3. Start a new chat when topic or repository boundary changes.
4. Verify generated output against the source and tests; context relevance never replaces validation.

## Output

- A minimal documented context set and a scoped result that can be independently reviewed.

## Error Handling

| Condition | Safe response |
|---|---|
| Context is stale or contradictory | Start a new topic-scoped chat with current files. |
| Sensitive path appears | Stop, remove it, repair exclusions, and follow exposure procedure. |
| Model misses key fact | Attach the authoritative file/interface rather than expanding the whole codebase. |

## Examples

For a bug in one service, attach its handler, interface, and focused test, state the failing behavior, and ask for a minimal fix. If the conversation starts discussing a different service, open a new chat instead of piling on more context.

Optimize how Cursor AI uses context to produce accurate, relevant responses. Context is everything the model sees when generating a response -- managing it well is the single biggest lever for output quality.

## Context Sources

Cursor assembles context from multiple sources before each AI request:

```
┌─ Always Included ─────────────────────────────────────┐
│  System prompt (Cursor internal)                      │
│  Active .cursor/rules/*.mdc with alwaysApply: true    │
│  Current file (for Tab, Inline Edit)                  │
└───────────────────────────────────────────────────────┘
┌─ Conditionally Included ──────────────────────────────┐
│  Selected code (highlighted before Cmd+L/Cmd+K)       │
│  @-mention targets (@Files, @Folders, @Code)          │
│  Glob-matched rules (.mdc with matching globs)        │
│  Conversation history (prior turns in chat)           │
│  Open editor tabs (lightweight reference)             │
└───────────────────────────────────────────────────────┘
┌─ On-Demand (explicit @-mention) ──────────────────────┐
│  @Codebase  → semantic search across indexed files    │
│  @Docs      → crawled external documentation          │
│  @Web       → live web search results                 │
│  @Git       → uncommitted diff or branch diff         │
│  @Lint Errors → current file lint diagnostics         │
└───────────────────────────────────────────────────────┘
```

## Context Pills

Active context appears as pills at the top of the Chat/Composer panel:

```
[main.ts] [src/utils/] [@Web: next.js 15] [Rule: typescript-standards]
```

- Click a pill to expand and see its contents
- Click `x` on a pill to remove it from context
- Adding too many pills fills the context window, degrading response quality

## @-Mention Strategy by Task

### Code Understanding

```
@src/auth/middleware.ts @src/types/user.ts
Explain how the JWT validation works and what happens when a token expires.
```

Use `@Files` for specific files. Avoid `@Folders` unless you need the full directory -- it consumes a lot of context.

### Bug Investigation

```
@src/hooks/useCart.ts @Lint Errors @Recent Changes
The cart total is NaN after the latest changes. What broke?
```

`@Recent Changes` + `@Lint Errors` gives the model forensic context.

### Architecture Questions

```
@Codebase where are database queries made?
```

`@Codebase` triggers semantic search across the indexed codebase. Good for discovery when you do not know which files are relevant. Costs more context than targeted `@Files` mentions.

### Using External Knowledge

```
@Docs Prisma @Web prisma client extensions 2025
How do I add soft-delete as a Prisma Client extension?
```

`@Docs` uses pre-indexed documentation. `@Web` does a live search. Combine both for comprehensive answers about third-party tools.

## Context Budget Management

Each model has a context limit. Overloading it causes the model to drop information silently:

| Model | Context Window | Practical Limit |
|-------|---------------|-----------------|
| GPT-4o | 128K tokens | ~80K usable |
| Claude Sonnet | 200K tokens | ~150K usable |
| Claude Opus | 200K tokens | ~150K usable |
| cursor-small | 8K tokens | ~5K usable |

### Signs of Context Overflow

- Model forgets instructions from earlier in the conversation
- Responses become generic or repetitive
- Model contradicts what it said 3 turns ago
- Suggested code ignores file context you provided

### Mitigation Strategies

1. **Start new conversations frequently.** One topic per conversation.
2. **Use specific @Files, not @Folders.** `@src/api/users.ts` is better than `@src/api/`.
3. **Remove context pills you no longer need.** Click `x` to drop stale files.
4. **Avoid @Codebase for narrow questions.** It pulls in many code chunks. Use `@Files` when you know the location.
5. **Break large tasks into steps.** Ask for the type definitions first, then the implementation, then the tests -- in separate turns or chats.

## Automatic vs Manual Context

Cursor automatically includes context in some cases:

| Feature | Automatic Context |
|---------|------------------|
| Tab Completion | Current file + open tabs + recent edits |
| Inline Edit (Cmd+K) | Selected code + surrounding file |
| Chat (Cmd+L) | Conversation history + explicitly added context |
| Composer (Cmd+I) | Referenced files + codebase search |

For Chat and Composer, you control context through @-mentions. Tab and Inline Edit manage their own context automatically.

## .cursorignore for Context Control

Prevent files from ever being included in AI context:

```gitignore
# .cursorignore (project root)

# Secrets and credentials
.env
.env.*
**/secrets/
**/credentials/

# Large generated files
dist/
build/
node_modules/
*.min.js
*.bundle.js

# Data files that consume context budget
*.csv
*.sql
*.sqlite
fixtures/
```

**Note:** `.cursorignore` is best-effort. It prevents files from appearing in indexing and AI features, but is not a security boundary for protecting secrets. Use `.gitignore` and environment variables for actual secret management.

## Advanced: Scoped Rules as Context

Project rules automatically inject context when relevant files are opened:

```yaml
# .cursor/rules/database-patterns.mdc
---
description: "Database query patterns and conventions"
globs: "src/db/**/*.ts,src/repositories/**/*.ts"
alwaysApply: false
---
# Database Conventions
- Use parameterized queries exclusively
- All queries go through repository pattern
- Wrap multi-table operations in transactions
- Use connection pooling (pool size: 10)
```

This rule automatically loads when editing database files, giving the AI the right conventions without you manually adding context each time.

## Enterprise Considerations

- **Data sensitivity**: Use `.cursorignore` to exclude files with PII, credentials, or regulated data
- **Privacy Mode**: Ensures code sent as context has zero data retention at model providers
- **Conversation hygiene**: Train teams to start new chats per task to avoid context bleed
- **Cost awareness**: Larger context = more tokens = higher API costs when using BYOK

## Resources

- [@ Symbols Overview](https://docs.cursor.com/context/@-symbols/overview)
- [Codebase Indexing](https://docs.cursor.com/context/codebase-indexing)
- [Ignore Files](https://docs.cursor.com/context/ignore-files)
