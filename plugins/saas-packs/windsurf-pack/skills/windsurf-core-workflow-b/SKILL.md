---
name: windsurf-core-workflow-b
description: 'Choose and create Devin Desktop customizations: Rules, AGENTS.md,
  Workflows, Skills, and Memories. Use when making Cascade behavior reusable or
  deciding how a procedure should activate. Trigger with "windsurf workflow",
  "Cascade skill", "windsurf rule", "AGENTS.md", or "Cascade memory".'
allowed-tools: Read, Write, Edit, Bash(npm:*), Grep
argument-hint: "[scope or requirements]"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- windsurf
- workflows
- skills
- rules
compatibility: Designed for Claude Code
---

# Devin Desktop Customizations

## Overview

Devin Desktop is the current name for Windsurf. Select the smallest customization that matches the task instead of treating Workflows and Memories as interchangeable automation.

## Prerequisites

- Devin Desktop with Cascade enabled
- A version-controlled workspace for shared customizations
- A concrete behavior or procedure to encode

## Authentication

Rules, `AGENTS.md`, Workflows, and Skills require no separate authentication. MCP-backed steps use provider OAuth or environment-backed secrets; never embed tokens in customization files.

## Tool Use

- Use `Read` to inspect only the repository files and configuration needed for the request.
- Use `Grep` to locate relevant settings, rules, logs, or code without broad collection.
- Use `Write` only for a new artifact the user requested; never write credentials or unreviewed production configuration.
- Use `Edit` for bounded, reviewable changes and preserve unrelated user work.
- Use only the command-scoped `Bash` entries declared in frontmatter, with non-destructive checks before mutations.

## Instructions

### Step 1: Choose the mechanism

| Mechanism | Activation | Use for |
|---|---|---|
| Rule | `always_on`, `glob`, `model_decision`, or `manual` | Short behavioral constraints |
| `AGENTS.md` | Root always-on; subdirectory location-scoped | Repository conventions without frontmatter |
| Workflow | Manual only through `/workflow-name` | Repeatable prompt sequences |
| Skill | Dynamic model invocation or `@mention` | Multi-step procedures with supporting files |
| Memory | Automatic local retrieval | Ephemeral facts; not durable team knowledge |

Prefer `.devin/rules/*.md` for Rules. Legacy `.windsurf/rules/` remains a fallback. Keep durable team knowledge in version control rather than relying on local auto-generated Memories.

### Step 2: Create a Rule or `AGENTS.md`

Use a Rule for controlled activation:

```markdown
---
trigger: glob
globs: "src/api/**/*.ts"
---

# API constraints
- Validate external input at the route boundary.
- Return the repository's standard error envelope.
```

Use a root or directory-level `AGENTS.md` when location alone should determine scope.

### Step 3: Create a Workflow

Save manual procedures under `.windsurf/workflows/<name>.md`, within the documented 12,000-character limit:

```markdown
# Review current pull request

1. Read the diff against the target branch.
2. Run the repository's required tests.
3. Report correctness, security, and regression findings with file locations.
4. Stop and ask for clarification when a finding cannot be resolved safely.
```

Invoke it explicitly as `/review-current-pr`. Workflows are Cascade-specific and are not automatically selected.

### Step 4: Create a Skill

Use `.windsurf/skills/<name>/SKILL.md` when the procedure needs scripts, templates, or reference files. Devin Desktop also discovers cross-agent skills under `.agents/skills/`; use that location when portability is intentional.

### Step 5: Verify activation

Test one matching and one non-matching request. Confirm a Rule's trigger, a Workflow's slash command, or a Skill's dynamic/explicit invocation. Record the file location and visible outcome.

## Output

Create the selected customization in its documented location, explain why it is a Rule, `AGENTS.md`, Workflow, Skill, or Memory, state its activation behavior and scope, and provide matching and non-matching verification evidence.

## Error Handling

| Issue | Response |
|---|---|
| Workflow is not listed | Confirm `.windsurf/workflows/*.md`, discovery scope, and character limit |
| Skill is not invoked | Improve `name`/`description`, then test with `@mention` |
| Rule applies too broadly | Replace `always_on` with a narrower glob, model decision, or `AGENTS.md` scope |
| Memory is stale | Remove it through Customizations and encode durable knowledge as a Rule |

## Examples

"Use a Workflow for a release checklist that a human must start; use a Skill for test-and-fix guidance Cascade should select automatically with bundled scripts."

## Resources

- [Focused first-party references](references/official-docs.md)
- [Rules, `AGENTS.md`, and Memories](https://docs.devin.ai/desktop/cascade/memories)
- [Workflows](https://docs.devin.ai/desktop/cascade/workflows)
- [Skills](https://docs.devin.ai/desktop/cascade/skills)

## Related Skill

Use `windsurf-policy-guardrails` when the customization must be enforced through Hooks, CI, repository protection, or an organization-wide administrative policy.
