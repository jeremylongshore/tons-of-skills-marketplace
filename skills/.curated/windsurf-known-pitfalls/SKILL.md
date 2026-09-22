---
name: windsurf-known-pitfalls
description: 'Identify and avoid Devin Desktop (formerly Windsurf) anti-patterns and common mistakes.

  Use when onboarding new developers to Windsurf, reviewing AI workflow practices,

  or auditing Windsurf configuration for issues.

  Trigger with phrases like "windsurf mistakes", "windsurf anti-patterns",

  "windsurf pitfalls", "windsurf what not to do", "windsurf gotchas".

  '
allowed-tools: Read, Grep
argument-hint: "[scope or requirements]"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- windsurf
- anti-patterns
- gotchas
- best-practices
compatibility: Designed for Claude Code
---
# Windsurf Known Pitfalls

## Overview

Avoid common failure modes involving Cascade, Supercomplete, workspace indexing, Rules, review, checkpoints, secrets, and terminal auto-execution. Verify mutable limits and labels against current first-party documentation.

## Prerequisites

- Windsurf installed and configured
- Understanding of Cascade vs Supercomplete
- Awareness of workspace indexing behavior

## Tool Use

- Use `Read` to inspect only the repository files and configuration needed for the request.
- Use `Grep` to locate relevant settings, rules, logs, or code without broad collection.

## Instructions

### Step 1: Avoid Using Cascade for Simple Tasks

**The mistake:** Opening Cascade (Cmd+L) to complete a single line of code.

```
BAD: Opening Cascade to write "add a console.log"
→ Cascade spins up full agent context, reads multiple files = slow and expensive

GOOD: Use Supercomplete (Tab) for inline completions
→ Instant; verify the current model's usage label before assuming no quota charge

RULE OF THUMB:
- Single line / simple completion → Tab (Supercomplete)
- Inline edit of selection → Cmd+I (Command)
- Multi-file task / complex reasoning → Cmd+L (Cascade)
```

### Step 2: Avoid Opening a Monorepo Root

**The mistake:** Opening a 100K+ file monorepo as a single workspace.

```
BAD:  windsurf ~/company-monorepo/
→ Cascade indexes everything, slow context, vague suggestions

GOOD: windsurf ~/company-monorepo/services/payments/
→ Focused context, fast indexing, precise suggestions

WHY: Cascade's context window is limited. More files = more noise.
A focused workspace with 5K files gives better suggestions than
a bloated workspace with 100K files.
```

### Step 3: Replace Vague Cascade Prompts

**The mistake:** Giving Cascade broad, unscoped instructions.

```
BAD: "Refactor the codebase to use TypeScript"
→ Cascade may try to convert EVERY file at once, breaking everything

BAD: "Add validation to the API"
→ Which API? Which endpoints? What validation rules?

GOOD: "Convert src/utils/api.js to TypeScript. Add proper types for
all function parameters and return values. Don't change other files."

GOOD: "In src/routes/users.ts, add zod validation for the POST /users
endpoint. Validate email format, name length (2-50 chars), and role
must be 'admin' or 'user'. Return 400 with field-level errors."
```

### Step 4: Review Every Proposed Change

**The mistake:** Accepting all Cascade changes without reading the diffs.

```
BAD: Cascade modifies 12 files → "Accept All" → broken tests
→ Cascade may have changed shared utilities, removed error handling,
  or introduced dependencies on APIs that don't exist

GOOD:
1. Read Cascade's explanation of what it changed
2. Review each file diff in the Cascade output
3. Check for: removed error handling, new imports, changed signatures
4. Run tests BEFORE committing
5. Use revert button if any file looks wrong
```

### Step 5: Create a Checkpoint Before Cascade

**The mistake:** Running Cascade on a dirty working tree without a Git checkpoint.

```
BAD: Uncomitted changes + Cascade edits = impossible to separate
→ Can't tell what was your work vs what Cascade changed
→ Can't revert Cascade changes without losing your work

GOOD: git add -A && git commit -m "checkpoint: before cascade"
→ Clean separation between your work and Cascade's
→ Easy revert: git checkout -- .
```

### Step 6: Isolate Conflicting AI Extensions

**The mistake:** Running GitHub Copilot alongside Windsurf.

```
KNOWN CONFLICTS:
- GitHub Copilot — conflicts with Supercomplete
  Symptoms: duplicate suggestions, wrong completions, slow editor

- TabNine — conflicts with Supercomplete
  Symptoms: competing inline suggestions

- Cody (Sourcegraph) — conflicts with Cascade
  Symptoms: multiple AI panels, context confusion

FIX: Disable competing extensions
Settings > Extensions > search "copilot" > Disable
```

### Step 7: Respect Rule Character Limits

**The mistake:** Writing an oversized `.devin/rules/project.md` file.

LIMITS:

- Workspace Rules under `.devin/rules/*.md`: 12,000 characters each (current documented per-rule limit)
- Global rules (`global_rules.md`): 6,000 characters (current documented global limit)

WHAT HAPPENS WHEN EXCEEDED:

- Oversized rules are outside the documented contract and may not load as intended
- Re-check the live rules documentation before relying on boundary behavior

FIX: Keep .devin/rules/project.md concise (stack, patterns, don'ts)
Move detailed rules to .devin/rules/ with trigger modes

### Step 8: Bound Cascade Conversations

**The mistake:** Using a single Cascade conversation for hours of work.

```
BAD: 50-message Cascade conversation spanning multiple topics
→ Context window fills up, Cascade "forgets" early context
→ Suggestions become inconsistent or contradictory

GOOD: One task per Cascade session
→ Click + icon to start new conversation for each new task
→ Clean context = better suggestions
→ Use Memories for facts that should persist across sessions
```

### Step 9: Keep Secrets Out of Cascade

**The mistake:** Sharing API keys or credentials in Cascade chat.

```
BAD: "My API key is sk-abc123def456, why isn't auth working?"
→ Secret is now in Cascade's context, may appear in suggestions later

GOOD: "I'm getting auth errors with the API key from .env. The error
message is 'Invalid API key'. What should I check?"
→ Cascade can help without seeing the actual secret
```

### Step 10: Configure Turbo Mode Safely

**The mistake:** Enabling Turbo mode without configuring deny lists.

```
BAD: Turbo mode ON + no deny list
→ Cascade auto-runs `rm -rf`, `git push --force`, etc.

GOOD: Turbo mode ON + configured deny list
→ Fast auto-execution for safe commands (npm test, git status)
→ Manual approval for dangerous commands (rm, sudo, push --force)

CONFIGURE:
Settings > cascadeCommandsDenyList > add destructive commands
```

## Output

Return a prioritized audit table with each observed pitfall, evidence location, risk, recommended correction, and verification step. Distinguish current Devin Desktop behavior from legacy Windsurf behavior so teams do not institutionalize obsolete settings.

## Error Handling

| Pitfall | Symptom | Prevention |
|---------|---------|------------|
| Wrong tool for task | Slow response for simple task | Tab for completions, Cmd+L for complex |
| Giant workspace | Slow indexing, vague AI | Open service directory, not root |
| Vague prompts | Wrong files modified | Specify paths, constraints, expected output |
| No review | Broken build after Cascade | Always review diffs, run tests |
| No checkpoint | Can't undo Cascade work | Always commit before Cascade |
| AI conflicts | Duplicate/wrong suggestions | Disable competing extensions |
| Over-limit rules | Silently truncated | Check char counts, use workspace rules |
| Long conversations | Context degradation | New session per task |
| Secrets in chat | Potential data exposure | Never paste actual credentials |
| Unsafe Turbo | Destructive commands auto-run | Configure deny list |

## Examples

### Pre-Cascade Checklist

```bash
set -euo pipefail
echo "=== Pre-Cascade Checklist ==="
readonly WORKSPACE_RULE_LIMIT=12000 # Current documented maximum for one workspace rule.
echo "Git clean: $(git status --porcelain | wc -l | xargs) uncommitted files"
echo "On branch: $(git branch --show-current)"
echo "Rules: $(wc -c < .devin/rules/project.md 2>/dev/null || echo 0) chars (max $WORKSPACE_RULE_LIMIT)"
echo "Conflicting exts: $(windsurf --list-extensions 2>/dev/null | grep -ci 'copilot\|tabnine\|cody' || echo 0)"
```

### Common Prompt Templates

```
Feature: "In [file], add [feature] that [behavior]. Follow the pattern
in @[reference-file]. Include error handling for [edge cases]. Don't
modify [protected files]."

Bug fix: "@[file] The function [name] fails when [condition]. The error
is [error message]. Fix it and add a test for this edge case."

Refactor: "Extract [logic] from [file] into a new [file]. Update all
imports. Run tests after. Don't change public API signatures."
```

## Resources

- [Focused first-party references](references/official-docs.md)
- [Windsurf Documentation](https://docs.devin.ai/desktop)
- [Cascade Best Practices](https://docs.devin.ai/desktop/cascade/cascade)
- [Windsurf Rules Directory](https://windsurf.com/editor/directory)

## Related Skills

Start with `windsurf-install-auth` for a new workstation, or use `windsurf-reference-architecture` to establish a reviewed team configuration baseline.
