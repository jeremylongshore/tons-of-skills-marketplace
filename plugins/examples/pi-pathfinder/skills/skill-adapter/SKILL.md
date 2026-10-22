---
name: skill-adapter
description: 'Execute analyzes existing plugins to extract their capabilities, then
  adapts and applies those skills to the current task. Acts as a universal skill chameleon
  that learns from other plugins. Activates when you request "skill adapter" functionality.
  Use when appropriate context detected. Trigger with relevant phrases based on skill
  purpose.

  '
allowed-tools: Read, Grep, Glob, Bash(cmd:*)
version: 1.25.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- example
- adapter
compatibility: Designed for Claude Code
---
# Skill Adapter

## Overview

Analyzes existing plugins in the repository to extract their capabilities, then synthesizes and applies those learned patterns to the current task. Functions as a universal skill chameleon that discovers relevant plugins, extracts their approaches and methodologies, and adapts them to novel requests.

## Prerequisites

- Read access to the `plugins/` directory tree (community, packages, examples categories)
- `grep` and `find` available on PATH for plugin discovery
- Familiarity with the plugin structure: `commands/*.md`, `agents/*.md`, `skills/*/SKILL.md`, and `scripts/`

## Instructions

1. Analyze the user's task to identify the core capability needed, the domain (security, devops, testing, documentation, etc.), and key requirements or constraints (see [`references/how-it-works.md`](references/how-it-works.md)).
2. Search existing plugins for relevant capabilities using file globbing across `plugins/community/`, `plugins/packages/`, and `plugins/examples/` directories. Match on `plugin.json` descriptions and keyword fields.
3. For each relevant plugin discovered, extract capabilities from its components:
   - **Commands** (`commands/*.md`): read content, extract approach and input/output patterns.
   - **Agents** (`agents/*.md`): understand roles, decision-making patterns, expertise areas.
   - **Skills** (`skills/*/SKILL.md`): read instructions, extract core capability and tool usage.
   - **Scripts** (`scripts/*.sh`, `*.py`): analyze logic, identify reusable patterns and error handling.
4. Synthesize extracted patterns by merging complementary approaches, simplifying where possible, and ensuring compatibility with the current environment.
5. Apply the adapted skill to the user's task, following the learned methodology while adjusting syntax, tools, and output format to match the current context.
6. Report which plugins were consulted, what patterns were extracted, and how they were adapted for the current task.

## Output

A structured adaptation report containing:

- List of plugins analyzed and capabilities extracted from each
- The synthesized approach combining relevant patterns
- The direct application of that approach to the user's task
- Any caveats or limitations of the adapted skill

## Error Handling

| Error | Cause | Solution |
|---|---|---|
| No matching plugins found | Search terms too narrow or domain not represented | Broaden search keywords; check alternative categories; fall back to general-purpose approach |
| Plugin directory inaccessible | Missing read permissions or incorrect path | Verify `plugins/` directory exists and permissions allow traversal |
| Incompatible patterns | Extracted approaches conflict with current environment | Prioritize the most relevant plugin's approach; discard conflicting elements |
| Empty skill/command files | Plugin has stub content without real instructions | Skip that plugin and note it as incomplete; rely on other sources |

## Examples

**Learning code analysis from security plugins:**
Task: "Analyze this codebase for issues."
Process: Discover `owasp-top-10-scanner`, `code-quality-enforcer`, and `security-audit-agent`. Extract OWASP vulnerability checks, complexity/duplication metrics, and dependency scanning patterns. Synthesize a multi-layer analysis covering security, quality, and dependencies. Apply to the target codebase (see [`references/example-workflows.md`](references/example-workflows.md)).

**Adopting documentation skills:**
Task: "Generate API documentation."
Process: Find `api-documenter`, `openapi-generator`, `readme-builder`. Extract code parsing, OpenAPI spec generation, and hierarchical documentation structuring. Combine into an end-to-end pipeline: parse endpoints, generate spec, create interactive docs, build README.

**Learning automation from DevOps plugins:**
Task: "Automate deployment process."
Process: Search DevOps category for deployment, CI/CD, and Docker plugins. Extract build-test-deploy-verify workflows, parallel job patterns, and service orchestration. Adapt to the user's specific tech stack and infrastructure.

## Resources

- [`references/how-it-works.md`](references/how-it-works.md) -- detailed five-phase adaptation process
- [`references/example-workflows.md`](references/example-workflows.md) -- end-to-end workflow examples
- [`references/errors.md`](references/errors.md) -- error handling patterns
