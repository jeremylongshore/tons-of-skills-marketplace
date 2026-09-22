---
title: "How to Write a Claude Code Skill"
description: "Step-by-step guide to writing a SKILL.md file for Claude Code. Learn how to plan, structure, and test auto-activating skills with proper frontmatter, allowed-tools, dynamic context injection, and supporting files."
section: "guides"
order: 1
keywords:
  - "skill"
  - "SKILL.md"
  - "auto-activating"
  - "frontmatter"
  - "allowed-tools"
  - "dynamic context injection"
  - "DCI"
  - "Claude Code plugin development"
officialLinks:
  - title: "Anthropic Claude Code Documentation"
    url: "https://code.claude.com/docs/en/"
  - title: "Anthropic Skills Reference"
    url: "https://code.claude.com/docs/en/skills"
relatedDocs:
  - "concepts/skills"
  - "reference/skill-frontmatter"
  - "reference/allowed-tools"
---

## What Is a Skill?

A skill is an auto-activating instruction file that Claude Code loads when its trigger conditions are met. Unlike slash commands (which the user must explicitly invoke) or agents (which run as autonomous sub-agents), skills activate automatically based on context. They live at `skills/[skill-name]/SKILL.md` inside a plugin directory and contain YAML frontmatter followed by Markdown instructions.

Skills are the most common building block in the Tons of Skills ecosystem. Of the 2,834 skills available on the [marketplace](/explore), the vast majority are SKILL.md files that enhance Claude Code's behavior for specific tasks: code review, deployment, API integration, testing, and more.

This guide walks you through building a skill from scratch, covering every decision you need to make along the way.

## Step 1: Plan Your Skill

Before writing any Markdown, answer these questions:

**What problem does this skill solve?** A good skill addresses a repeatable task that benefits from structured instructions. "Help me write unit tests for React components" is a good scope. "Do everything related to my project" is too broad.

**When should this skill activate?** Claude Code reads the `description` field to decide when to load your skill. Think about the exact phrases a developer would say or the context that should trigger activation.

**What tools does Claude need?** Every tool you grant is a permission. Grant only what the skill actually requires. A skill that reads configuration files needs `Read` and `Glob` but probably not `Write` or `Bash`.

**What is the expected output?** Define what success looks like. A code review skill should produce structured feedback. A deployment skill should produce a checklist with pass/fail status.

### Planning Checklist

Write down:

1. A one-sentence purpose statement
2. Three to five trigger phrases users might say
3. The minimum set of tools required
4. The expected output format
5. Any prerequisites (runtime, language, framework)

## Step 2: Create the Directory Structure

Skills live inside a plugin at `skills/[skill-name]/SKILL.md`. The skill name must be lowercase kebab-case.

```
my-plugin/
├── .claude-plugin/
│   └── plugin.json
├── README.md
└── skills/
    └── react-test-writer/
        ├── SKILL.md
        ├── patterns.md          # Optional supporting file
        └── examples/
            └── component.test.tsx  # Optional example file
```

Create the directory:

```bash
mkdir -p skills/react-test-writer
touch skills/react-test-writer/SKILL.md
```

## Step 3: Write the Frontmatter

The YAML frontmatter block at the top of SKILL.md configures how Claude Code discovers and loads your skill. Here is the complete set of fields:

```yaml
---
name: react-test-writer
description: |
  Write comprehensive unit tests for React components using Testing Library
  and Vitest. Trigger phrases: "write tests for this component", "add unit
  tests", "test this React component", "generate component tests".
allowed-tools: Read, Write, Edit, Bash(npx vitest:*), Glob, Grep
version: 1.0.0
author: Your Name <you@example.com>
license: MIT
compatible-with: claude-code
tags: [testing, react, vitest, unit-tests]
---
```

### Required Fields

| Field | Purpose |
|-------|---------|
| `name` | Unique identifier in kebab-case. Must match the directory name. |
| `description` | Tells Claude Code when to activate this skill. Include trigger phrases. This is the single most important field for discoverability. |
| `allowed-tools` | Comma-separated list of tools the skill may use. |
| `version` | Semantic version string. |
| `author` | Name and optional email. |
| `license` | SPDX license identifier. |

### Optional Fields

| Field | Purpose | Example |
|-------|---------|---------|
| `model` | Override the LLM model. | `sonnet`, `haiku`, `opus` |
| `context` | Run in a forked sub-agent. | `fork` |
| `agent` | Sub-agent type when context is fork. | `Explore` |
| `user-invocable` | Set to `false` to hide from the slash menu. | `false` |
| `argument-hint` | Autocomplete hint shown in the slash menu. | `"<component-path>"` |
| `hooks` | Lifecycle hooks for pre/post tool calls. | `{ pre-tool-call: ... }` |
| `compatibility` | Runtime requirements. | `"Node.js >= 18"` |
| `compatible-with` | Platform compatibility. | `claude-code, cursor` |
| `tags` | Discovery tags for search and categorization. | `[testing, react]` |

### Writing a Strong Description

The `description` field is a paragraph, not a sentence. Claude Code uses it as the primary signal for auto-activation. Follow these rules:

1. Start with a verb phrase: "Write", "Analyze", "Deploy", "Generate"
2. Describe the specific task clearly
3. List three to five trigger phrases users might say
4. Mention key technologies or frameworks

**Good description:**

```yaml
description: |
  Write comprehensive unit tests for React components using React Testing
  Library and Vitest. Covers render tests, user interaction tests, async
  behavior, and snapshot tests. Trigger phrases: "write tests for this
  component", "add unit tests", "test this React component".
```

**Bad description:**

```yaml
description: "Helps with testing"
```

## Step 4: Choose Your Allowed Tools

The `allowed-tools` field implements the principle of least privilege. Only grant the tools your skill actually needs.

### Available Tools

| Tool | Purpose | When to Include |
|------|---------|-----------------|
| `Read` | Read files from disk | Almost always needed |
| `Write` | Create new files | When generating new files |
| `Edit` | Modify existing files | When updating existing files |
| `Bash` | Execute shell commands | When running CLI tools |
| `Glob` | Find files by pattern | When searching for files by name |
| `Grep` | Search file contents | When searching inside files |
| `WebFetch` | Fetch URLs | When pulling remote data |
| `WebSearch` | Search the web | When looking up documentation |
| `Task` | Create sub-tasks | For complex multi-step workflows |
| `TodoWrite` | Write to the todo list | For tracking work items |
| `NotebookEdit` | Edit Jupyter notebooks | For data science workflows |
| `AskUserQuestion` | Prompt the user | When user input is needed |
| `Skill` | Invoke other skills | For skill composition |

### Scoping Bash Commands

You can restrict `Bash` to specific commands using a prefix pattern:

```yaml
# Allow only npm and npx commands
allowed-tools: Read, Bash(npm:*), Bash(npx:*), Glob

# Allow only git commands
allowed-tools: Read, Bash(git:*), Glob, Grep

# Allow only python3
allowed-tools: Read, Write, Bash(python3:*), Glob
```

This prevents the skill from running arbitrary shell commands while still enabling the specific CLI tools it needs.

## Step 5: Write the Skill Body

The body of SKILL.md is Markdown that instructs Claude Code how to perform the task. Think of it as a detailed playbook that a skilled developer would follow.

### Recommended Sections

```markdown
# Skill Name

Brief one-sentence overview of what this skill does.

## Overview

A paragraph explaining the skill's purpose, approach, and scope.

## Prerequisites

- Runtime requirements
- Required packages or tools
- Expected project structure

## Instructions

Step-by-step instructions Claude Code will follow:

1. First, do this
2. Then do that
3. Finally, verify the result

## Output

Describe the expected output format. Use a template if the output
should be structured.

## Error Handling

- If X happens, do Y
- If Z is missing, report it and stop

## Examples

Show concrete examples of input and expected output.
```

### Writing Effective Instructions

**Be specific, not vague.** Instead of "write good tests", say "write a test file that imports the component, renders it with default props, asserts the presence of key elements, simulates user interactions with `userEvent`, and verifies state changes."

**Use numbered steps.** Claude Code follows numbered instructions more reliably than prose paragraphs.

**Include code templates.** Show the exact structure you want in the output:

```markdown
## Output Format

Generate a test file with this structure:

\```typescript
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect } from 'vitest';
import { ComponentName } from './ComponentName';

describe('ComponentName', () => {
  it('renders without crashing', () => {
    render(<ComponentName />);
    expect(screen.getByRole('...')).toBeInTheDocument();
  });

  it('handles user interaction', async () => {
    const user = userEvent.setup();
    render(<ComponentName />);
    await user.click(screen.getByRole('button'));
    expect(screen.getByText('...')).toBeVisible();
  });
});
\```
```

**Specify error handling.** Tell Claude what to do when things go wrong: missing files, failed tests, unsupported configurations.

## Step 6: Add Supporting Files

Skills can reference additional files using relative Markdown links. Claude Code follows these links with the Read tool when it needs the content.

```markdown
For API patterns, see API Reference.
For working examples, see Examples.
```

### Common Supporting Files

| File | Purpose |
|------|---------|
| `reference.md` | API documentation, configuration options |
| `patterns.md` | Code patterns and anti-patterns |
| `checklist.md` | Validation checklist |
| `examples/*.ts` | Working code examples |

The `${CLAUDE_SKILL_DIR}` variable resolves to the skill's directory at runtime. Use it in bash commands within the skill body:

```markdown
Read the configuration template:
\```bash
cat ${CLAUDE_SKILL_DIR}/templates/config.yaml
\```
```

## Step 7: Dynamic Context Injection (DCI)

DCI lets you inject runtime data into the skill body before Claude processes it. This eliminates tool call round-trips for discovery data like git status, installed versions, or environment details.

### Syntax

Place a shell command on its own line using backtick syntax:

```markdown
## Current Environment

!`node --version 2>/dev/null || echo 'Node.js not installed'`

!`git branch --show-current 2>/dev/null || echo 'not a git repo'`

!`cat package.json | jq -r '.dependencies | keys[]' 2>/dev/null || echo 'no package.json'`
```

When the skill activates, Claude Code runs these commands and replaces them with their stdout output. The skill then sees the actual data instead of the commands.

### DCI Best Practices

1. **Always add fallbacks.** Use `|| echo 'fallback message'` to handle missing tools or files.
2. **Keep injections small.** Inject summaries, not full file contents. A list of dependency names is useful; the entire `node_modules` tree is not.
3. **Use `2>/dev/null`** to suppress stderr noise.
4. **Avoid side effects.** DCI commands run at activation time. Never modify files or state in a DCI command.

## Step 8: Test Your Skill

### Manual Testing

1. Install the plugin in a test project:

   ```bash
   claude /plugin add /path/to/your/plugin
   ```

2. Say one of your trigger phrases and verify the skill activates.

3. Check that the output matches your expected format.

4. Test edge cases: missing files, wrong project type, empty input.

### Validation

Run the universal validator against your skill:

```bash
# Standard validation (Anthropic minimum requirements)
python3 scripts/validate-skills-schema.py --verbose skills/react-test-writer/SKILL.md

# Enterprise validation (100-point rubric)
python3 scripts/validate-skills-schema.py --enterprise --verbose skills/react-test-writer/SKILL.md
```

The enterprise validator scores your skill on a 100-point rubric covering frontmatter completeness, body structure, code examples, error handling, and documentation quality. Aim for a score of 70 or higher (B grade) for marketplace submission.

### Common Validation Errors

| Error | Fix |
|-------|-----|
| Missing `name` field | Add `name` matching the directory name |
| Invalid `allowed-tools` | Check spelling; use exact tool names from the valid list |
| Description too short | Write at least 2-3 sentences with trigger phrases |
| No `version` field | Add `version: 1.0.0` |
| Body too short | Add sections: Overview, Instructions, Output, Examples |

## Full Working Example

Here is a complete SKILL.md for a React test writer skill:

```yaml
---
name: react-test-writer
description: |
  Write comprehensive unit tests for React components using React Testing
  Library and Vitest. Analyzes component props, state, effects, and user
  interactions to generate thorough test coverage. Trigger phrases: "write
  tests for this component", "add unit tests", "test this React component",
  "generate component tests".
allowed-tools: Read, Write, Bash(npx vitest:*), Bash(npx tsc:*), Glob, Grep
version: 1.0.0
author: Your Name <you@example.com>
license: MIT
compatibility: "Node.js >= 18, React >= 18"
compatible-with: claude-code
tags: [testing, react, vitest, unit-tests, testing-library]
---

# React Test Writer

Generate comprehensive unit tests for React components with full coverage
of rendering, interactions, and edge cases.

## Overview

This skill analyzes a React component's source code, identifies its props
interface, state management, side effects, and user interaction handlers,
then generates a complete test file using React Testing Library and Vitest.

## Prerequisites

- Project uses React 18+ with TypeScript
- Vitest and @testing-library/react installed
- @testing-library/user-event installed

## Current Project State

!`cat package.json | jq '{react: .dependencies.react, vitest: .devDependencies.vitest, testingLibrary: .devDependencies["@testing-library/react"]}' 2>/dev/null || echo 'Could not read package.json'`

## Instructions

1. Read the target component file using the Read tool
2. Identify the component's props interface (TypeScript types or PropTypes)
3. List all state variables (useState, useReducer)
4. List all side effects (useEffect, useLayoutEffect)
5. List all event handlers and user interaction points
6. Check for conditional rendering branches
7. Generate a test file following the output format below
8. Run the tests with `npx vitest run <test-file> --reporter=verbose`
9. If tests fail, read the error output and fix the test file
10. Report the final test results

## Output

Generate a test file at `[component-dir]/[ComponentName].test.tsx`:

- One `describe` block per component
- Render tests for default props and each significant prop combination
- Interaction tests using `userEvent` for every click, type, and submit handler
- Async tests for any data fetching or effects
- Edge case tests for empty states, error states, and boundary values

## Error Handling

- If the component file does not exist, report the error and stop
- If testing dependencies are missing, list the install commands needed
- If tests fail after generation, analyze the failure and fix (up to 3 attempts)
- If the component uses unsupported patterns, document them and skip those tests

## Examples

**Input:** "Write tests for src/components/SearchBar.tsx"

**Expected output:** A file `src/components/SearchBar.test.tsx` containing
tests for rendering, typing in the input, submitting the form, clearing
the input, and handling empty search terms.
```

## Next Steps

Once your skill is working, you can package it into a full plugin with a `plugin.json`, `README.md`, and optional commands and agents. See [How to Build a Claude Code Plugin](/docs/guides/build-a-plugin) for the complete plugin creation workflow, or [Publish to the Marketplace](/docs/guides/publish-to-marketplace) to share your skill with the community.
