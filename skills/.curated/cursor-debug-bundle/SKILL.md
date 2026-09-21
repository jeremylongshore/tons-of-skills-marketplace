---
name: cursor-debug-bundle
description: 'Debug AI suggestion quality, context issues, and code generation problems
  in Cursor. Triggers on

  "debug cursor ai", "cursor suggestions wrong", "bad cursor completion", "cursor
  ai debug",

  "cursor hallucination".

  '
allowed-tools: Read, Write, Edit, Bash(cmd:*)
version: 1.19.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- cursor
- debugging
compatibility: Designed for Claude Code
---
# Cursor Debug Bundle

## Overview

Collect a minimal, redacted reproduction for a Cursor issue involving context, rules, indexing, model behavior, or extensions. Debug material may contain proprietary code or prompts, so scope and retention matter as much as reproducibility.

## Prerequisites

- A named issue owner, Cursor version, affected workspace, and approved bug-report destination.
- Permission to inspect logs and settings, plus redaction rules for code, prompts, paths, tokens, and user data.
- A minimal reproducer that does not require customer data or production credentials.

## Instructions

1. Start with the smallest reproducible prompt, file set, rule set, and model configuration.
2. Record versions, active context, indexing state, extensions, and redacted console errors.
3. Remove proprietary code, credentials, identifiers, and full prompt/output text before sharing externally.
4. Test the proposed resolution in a non-sensitive workspace and document its result before closing the issue.

Diagnose and fix AI suggestion quality issues in Cursor. Covers why AI generates wrong code, how to improve context, and systematic debugging workflows.

## Diagnostic Framework

When AI suggestions are wrong, the cause is almost always one of these:

```
┌─ Context Problems (80% of issues) ───────────────────────┐
│  1. Missing context: AI doesn't have the relevant code   │
│  2. Wrong context: AI has stale or irrelevant files      │
│  3. Too much context: context window overflow            │
│  4. No project rules: AI doesn't know your conventions   │
└──────────────────────────────────────────────────────────┘
┌─ Model Problems (15% of issues) ─────────────────────────┐
│  5. Wrong model for the task                             │
│  6. Model hallucinating APIs or patterns                 │
└──────────────────────────────────────────────────────────┘
┌─ Prompt Problems (5% of issues) ─────────────────────────┐
│  7. Ambiguous or vague instructions                      │
│  8. Conflicting requirements in prompt                   │
└──────────────────────────────────────────────────────────┘
```

## Debugging by Symptom

### AI Uses Wrong API or Library Version

**Symptom:** Generated code uses `React.createClass`, old Express syntax, or deprecated patterns.

**Root cause:** Model training data includes old code. No project rules specifying versions.

**Fix:**

```yaml
# .cursor/rules/stack-versions.mdc
---
description: "Tech stack version pinning"
globs: ""
alwaysApply: true
---
# Stack Versions (ALWAYS use these)
- React 19 with Server Components (NOT class components)
- Next.js 15 App Router (NOT Pages Router)
- TypeScript 5.7 strict mode
- Prisma 6 (NOT Sequelize or TypeORM)
- Tailwind CSS 4 (NOT styled-components)
- Node.js 22 (ESM, NOT CommonJS require())
```

### AI Generates Code That Doesn't Match Your Patterns

**Symptom:** Generated code uses different naming, structure, or patterns than your codebase.

**Root cause:** AI does not have your existing code as context.

**Fix:** Reference your existing patterns explicitly:

```
@src/api/users/route.ts

Create src/api/products/route.ts following the EXACT same patterns:
same error handling, same response format, same validation approach.
```

### AI Hallucinates Non-Existent Functions

**Symptom:** AI calls functions or uses imports that do not exist in your project or in the library.

**Root cause:** Model confuses similar libraries or invents plausible-sounding APIs.

**Fix:**

1. Add `@Docs` context: `@Docs Prisma` gives the AI real API documentation
2. Verify generated imports: run `npm run build` immediately after applying
3. Use `@Files` to show the actual module interface: `@src/lib/database.ts`

### AI Ignores Your Instructions

**Symptom:** You ask for one thing, AI does something different.

**Root cause:** Context window overflow -- your instructions get pushed out by file contents.

**Fix:**

1. Start a **new chat** (Cmd+N) -- conversation history may be using too much context
2. Use fewer `@` references -- each consumes context budget
3. Put instructions at the **end** of the prompt (models attend more to recent text)
4. Use `@Files` instead of `@Codebase` to reduce context volume

### Tab Completion is Repetitive or Wrong

**Symptom:** Tab keeps suggesting the same wrong pattern.

**Root cause:** Tab has limited context compared to Chat/Composer.

**Fix:**

1. Open related files in editor tabs (Tab reads open tabs)
2. Add a comment above your cursor describing what you want
3. Reject bad suggestions with `Esc` (trains the model)
4. If persistently wrong, use Cmd+K inline edit instead

## Systematic Debug Workflow

When AI output is consistently wrong:

```
Step 1: Check context
  - Open Chat, look at context pills at top
  - Are the right files included?
  - Are stale files adding noise?

Step 2: Check rules
  - @Cursor Rules in chat -- what rules are active?
  - Do rules conflict with each other?
  - Are glob patterns matching the right files?

Step 3: Test with minimal context
  - Start new chat
  - Add ONLY the most relevant file: @src/the-file.ts
  - Ask your question with explicit constraints
  - If this works, the issue was context pollution

Step 4: Test with different model
  - Switch from Sonnet to Opus or GPT-5
  - If better model gives better results, the task needs more reasoning power

Step 5: Check indexing
  - Is the codebase indexed? (status bar shows "Indexed")
  - Is the relevant file excluded by .cursorignore?
  - Run Cmd+Shift+P > "Cursor: Resync Index"
```

## Logs and Diagnostics

### Opening Developer Tools

`Cmd+Shift+P` > `Developer: Toggle Developer Tools`

Check the Console tab for:

- API request errors (red)
- Context assembly logs
- Extension errors

### Verbose Logging

Enable verbose output: `Cursor Settings` > search "log level" > set to "Debug"

Logs location:

- macOS: `~/Library/Application Support/Cursor/logs/`
- Linux: `~/.config/Cursor/logs/`

### Reproducing Issues for Bug Reports

```
1. Note Cursor version: Help > About
2. Note model used (from Chat/Composer header)
3. Copy the exact prompt that produced wrong output
4. Copy the wrong output
5. List active extensions: Cmd+Shift+P > "Extensions: Show Installed"
6. Note if Privacy Mode is on (affects model behavior)
7. Report at forum.cursor.com or github.com/getcursor/cursor/issues
```

## Enterprise Considerations

- **Quality baselines**: Track AI suggestion accuracy over time per team/project
- **Model pinning**: If a model update degrades quality, temporarily switch to a different model while reporting
- **Rule audits**: Periodically review `.cursor/rules/` for outdated or conflicting rules
- **Training**: Ensure team knows the difference between context, model, and prompt issues

## Output

- A redacted reproduction bundle containing versions, minimal steps, active configuration, and observed/expected behavior.
- A disposition: resolved with evidence, vendor escalation, or internal policy/configuration change.

## Error Handling

| Condition | Safe response |
|---|---|
| Bundle contains proprietary code or credentials | Stop distribution, remove the material, rotate exposed secrets, and recreate a minimal redacted reproducer. |
| Issue cannot reproduce | Record the exact environment delta and keep the issue open for additional evidence. |
| Debugging changes global settings | Revert after the test or use a disposable profile. |

## Examples

For a bad-context report, create a new chat with one sanitized file and a short non-sensitive request. Record the Cursor version, active rules, selected model, expected and observed behavior, then attach only redacted material approved for the support channel.

## Resources

- Cursor Forum - Troubleshooting
- [Cursor GitHub Issues](https://github.com/getcursor/cursor/issues)
- [Context Management Docs](https://docs.cursor.com/context/@-symbols/overview)
