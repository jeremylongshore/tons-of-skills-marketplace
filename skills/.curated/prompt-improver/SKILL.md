---
name: prompt-improver
description: 'Analyze and improve plugin prompts, skill definitions, and command instructions
  for clarity, safety, and effectiveness. Use when the user asks to "improve a prompt",
  "review a skill", "enhance instructions", "make this prompt better", "optimize this
  command", or "audit prompt quality".

  '
allowed-tools: Read, Write, Edit, Glob, Grep
version: 1.7.0
author: severity1 <severity1@intentsolutions.io>
license: MIT
tags:
- security
- compliance
compatibility: Designed for Claude Code
---
# Prompt Improver

This skill automatically analyzes and improves plugin prompts, SKILL.md files, command definitions, and agent instructions.

## Overview

The prompt-improver skill evaluates plugin content across five dimensions — clarity, safety, effectiveness, completeness, and conciseness — then provides scored assessments and concrete rewrites.

## When to Use This Skill

This skill activates when you need to:

- Review and improve a SKILL.md file's instructions
- Enhance command or agent markdown definitions
- Audit prompt quality across a plugin
- Optimize instructions for better Claude performance
- Ensure prompts follow marketplace best practices

## Instructions

1. **Identify the target** — Locate the SKILL.md, command, or agent file to analyze
2. **Read the content** — Use Read tool to get the full file contents
3. **Score each dimension** on a 1-5 scale:
   - **Clarity (1-5)**: Are instructions unambiguous?
   - **Safety (1-5)**: Does it avoid encouraging dangerous operations?
   - **Effectiveness (1-5)**: Will it reliably produce intended results?
   - **Completeness (1-5)**: Are edge cases addressed?
   - **Conciseness (1-5)**: Is it free of unnecessary verbosity?
4. **Identify improvements** — List specific weaknesses with line references
5. **Generate rewrites** — Provide improved versions preserving original intent
6. **Apply changes** — If requested, use Edit tool to apply improvements

## Output Format

```
## Prompt Analysis: [filename]

### Scores
| Dimension | Score | Notes |
|-----------|-------|-------|
| Clarity | X/5 | ... |
| Safety | X/5 | ... |
| Effectiveness | X/5 | ... |
| Completeness | X/5 | ... |
| Conciseness | X/5 | ... |

**Overall: X/25**

### Improvements
1. [Specific improvement with before/after]

### Suggested Rewrite
[Full improved prompt text]
```

## Best Practices

- Preserve the original author's intent and style
- Prioritize safety improvements over stylistic ones
- Keep suggestions actionable and specific
- Reference marketplace conventions from CLAUDE.md
- Validate frontmatter fields match the 2026 spec

## Examples

### Example 1: Improving a vague skill description

**Before:**

```yaml
description: Does stuff with code
```

**After:**

```yaml
description: |
  Analyze source code for common anti-patterns and suggest refactoring improvements. Use when the user asks to "review code quality", "find code smells", or "refactor this file".
```

### Example 2: Adding missing safety guidance

**Before:**

```markdown
Delete all temporary files from the project.
```

**After:**

```markdown
Identify temporary files (*.tmp, *.bak, *.swp) in the project. List them for user confirmation before deletion. Never delete files outside the project root.
```

## Prerequisites

- A plugin directory containing at least one SKILL.md, command, or agent markdown file
- Read access to the target plugin's `.claude-plugin/plugin.json` for context
- Familiarity with the [2026 SKILL.md frontmatter spec](https://code.claude.com/docs/en/plugins)

## Output

The skill produces a structured analysis report containing:

- **Score card**: 5 dimensions rated 1-5 with notes and an overall score out of 25
- **Improvement list**: Specific weaknesses with file paths and line references
- **Suggested rewrite**: Full improved prompt text preserving original intent

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| No SKILL.md found | Target path has no skill files | Verify the plugin path and check for `skills/*/SKILL.md` |
| Invalid frontmatter | YAML parsing failure in target file | Report the specific YAML error and suggest corrections |
| Empty skill body | File has frontmatter but no instructions | Flag as critical and generate a starter template |

## Resources

- [Claude Code plugins documentation](https://code.claude.com/docs/en/plugins) — official plugin and SKILL.md spec
- [Prompt engineering guide](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview) — Anthropic best practices for prompt design
- Marketplace conventions: see the repository CLAUDE.md for field requirements and structure
