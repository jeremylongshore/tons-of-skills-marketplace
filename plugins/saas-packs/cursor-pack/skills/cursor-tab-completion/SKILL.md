---
name: cursor-tab-completion
description: 'Master Cursor Tab autocomplete, ghost text, and AI code suggestions.
  Triggers on "cursor completion",

  "cursor tab", "cursor suggestions", "cursor autocomplete", "cursor ghost text",
  "cursor copilot".

  '
allowed-tools: Read, Write, Edit, Bash(cmd:*)
version: 1.19.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- cursor
- cursor-tab
compatibility: Designed for Claude Code
---
# Cursor Tab Completion

## Overview

Use Tab for small, local code completions; it predicts text and does not establish correctness, security, or repository policy compliance.

## Prerequisites

- An approved Cursor privacy setting and a workspace that excludes secrets and sensitive paths from context.
- Existing project rules, formatter, and focused tests for the code being changed.

## Instructions

1. Write the function signature, types, and a concise intent comment before considering a suggestion.
2. Accept only the scoped portion you understand, then inspect the diff and run the focused check.
3. Reject suggestions that add unrelated behavior, dependencies, credentials, or policy exceptions.

## Output

- A small reviewed completion with source-control visibility and test evidence.

## Error Handling

| Condition | Safe response |
|---|---|
| Completion is incorrect or insecure | Reject it and implement or request a narrower change. |
| Multiple completion providers conflict | Disable the duplicate provider using approved editor configuration. |
| Sensitive file is in context | Stop, update ignore rules, and follow the data-handling procedure. |

## Examples

For a CSV parser, write the return type and validation constraints first. Accept only the parser body, inspect the resulting diff, and run its unit test. If Tab adds filesystem access or changes another file, reject it rather than editing around the suggestion.

Master Cursor's AI-powered Tab completion system. Tab uses a specialized Cursor model trained for inline code prediction -- it learns from your accept/reject behavior to improve over time.

## How Tab Works

1. You type code in the editor
2. Cursor's model predicts what comes next based on: current file, open tabs, recent edits, project rules
3. Ghost text (gray text) appears inline
4. You decide: **Tab** to accept, **Esc** to dismiss

```
// You type:
function validateEmail(email: string)

// Ghost text appears:
function validateEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;    ← gray ghost text
  return emailRegex.test(email);
}
```

## Key Bindings

| Action | macOS | Windows/Linux |
|--------|-------|---------------|
| Accept full suggestion | `Tab` | `Tab` |
| Accept word-by-word | `Cmd+→` | `Ctrl+→` |
| Dismiss suggestion | `Esc` | `Esc` |
| Force trigger | `Ctrl+Space` | `Ctrl+Space` |

**Word-by-word acceptance** (`Cmd+→`) is powerful for partial suggestions. If the AI suggests a complete function but you only want the signature, accept word-by-word until you have what you need, then type your own body.

## Tab Completion Settings

Access via `Cursor Settings` > `Tab`:

| Setting | Purpose | Recommendation |
|---------|---------|----------------|
| Tab Completion | Master on/off toggle | Keep enabled |
| Trigger in comments | Generate comment text | Disable for less noise |
| Accept suggestion keybinding | Remap Tab to another key | Default (Tab) works best |
| Suggestion delay | Time before ghost text appears | Lower = faster but more flicker |

### Disabling Tab for Comments

If Tab suggestions in comments are distracting:

`Cursor Settings` > `Tab Completion` > uncheck `Trigger in comments`

## Context That Improves Completions

Tab quality depends heavily on available context:

1. **Current file**: The model reads the full file you are editing
2. **Open editor tabs**: Files open in other tabs provide pattern context
3. **Recent edits**: Changes you have made in the last few minutes
4. **Project rules**: `.cursor/rules/*.mdc` or `.cursorrules` content
5. **Codebase index**: If indexed, the model uses semantic code search

### Tips for Better Suggestions

```
// BAD: Tab has no context about what you want
function process(data) {

// GOOD: Type signature gives Tab strong signal
function processPayment(
  amount: number,
  currency: 'USD' | 'EUR',
  paymentMethod: PaymentMethod
): Promise<PaymentResult> {
```

**Write descriptive function names and type signatures first.** Tab uses these as strong signals for generating the body.

### Using Comments as Prompts

```typescript
// Parse CSV file, skip header row, return array of objects with typed fields
function parseCSV(filepath: string): Promise<Record<string, string>[]> {
  // Tab will generate the full implementation based on the comment above
}
```

## Tab vs Other AI Features

| Feature | Trigger | Scope | Speed |
|---------|---------|-------|-------|
| **Tab** | Automatic while typing | Single completion | Instant (~100ms) |
| **Inline Edit (Cmd+K)** | Manual selection + prompt | Selected code block | ~2-5 seconds |
| **Chat (Cmd+L)** | Manual prompt | Conversational | ~3-10 seconds |
| **Composer (Cmd+I)** | Manual prompt | Multi-file | ~5-30 seconds |

Tab is the only feature that runs continuously as you type. It is optimized for speed over capability -- simple completions, not complex reasoning.

## Important Limitations

- **No custom models for Tab**: Even with BYOK (Bring Your Own Key), Tab always uses Cursor's proprietary model. Custom API keys apply to Chat and Composer only.
- **No reasoning**: Tab predicts the next tokens; it does not reason about correctness. Always review suggestions.
- **Context window**: Tab sees less context than Chat or Composer. For complex logic, use Cmd+K or Cmd+L instead.

## Conflict Resolution

If Tab conflicts with other extensions:

1. **Disable GitHub Copilot**: `Extensions` > search "Copilot" > Disable. Running both causes duplicate ghost text.
2. **Disable TabNine / Codeium**: Same issue -- only one inline completion provider should be active.
3. **VS Code IntelliSense**: Tab and IntelliSense coexist. IntelliSense handles imports/completions, Tab handles multi-line generation.

Remap if needed: `Cmd+K Cmd+S` > search `acceptCursorTabSuggestion` > assign new key.

## Measuring Tab Effectiveness

Tab gets better with usage. The model learns from:

- **Accepts** (Tab): Reinforces the pattern
- **Rejects** (Esc): Discourages similar suggestions
- **Partial accepts** (Cmd+→): Signals which parts were useful

After a few days on a project, Tab suggestions become noticeably more aligned with your coding style.

## Enterprise Considerations

- Tab suggestions are generated using Cursor's proprietary model -- not configurable via API keys
- Privacy Mode applies to Tab: with Privacy Mode on, code sent for Tab predictions has zero data retention
- Tab is included in all Cursor plans (Free tier has limited daily uses)
- No audit logging for individual Tab completions

## Resources

- [Cursor Tab Documentation](https://docs.cursor.com/tab/overview)
- [Keyboard Shortcuts](https://docs.cursor.com/kbd)
- [Privacy and Data Use](https://cursor.com/data-use)
