---
title: "Allowed Tools Reference"
description: "Complete reference for all valid tools in the Claude Code plugin system, including tool descriptions, scoped Bash patterns, least-privilege principles, and recommended tool combinations for common skill types."
section: "reference"
order: 4
keywords: ["allowed-tools", "tools", "permissions", "Bash", "Read", "Write", "Edit", "Glob", "Grep", "security", "least privilege"]
officialLinks:
  - title: "Claude Code Skills Documentation"
    url: "https://code.claude.com/docs/en/skills"
  - title: "Claude Code Tool Use"
    url: "https://code.claude.com/docs/en/overview"
relatedDocs:
  - "concepts/skills"
  - "guides/write-a-skill"
  - "reference/skill-frontmatter"
---

## Overview

The `allowed-tools` field in SKILL.md frontmatter controls which tools a skill may invoke at runtime. Claude Code enforces this list strictly -- if a skill attempts to call a tool not in its `allowed-tools`, the call is blocked. This mechanism implements the principle of least privilege: every skill should request only the tools it actually needs to perform its task.

The `allowed-tools` field accepts a comma-separated string of tool names. Tool names are case-sensitive and must match exactly.

```yaml
allowed-tools: Read, Glob, Grep
```

## Complete Tool Reference

The following table lists every valid tool name that can appear in the `allowed-tools` field.

### File System Tools

| Tool | Description | Use When |
|------|-------------|----------|
| `Read` | Read file contents from the filesystem. Returns file content with line numbers. Can read text files, images, PDFs, and Jupyter notebooks. | The skill needs to examine existing files, analyze code, or review documentation. |
| `Write` | Create new files or completely overwrite existing files. | The skill generates new files (scaffolding, templates, configs) or performs complete file rewrites. |
| `Edit` | Perform targeted string replacements within existing files. Finds an exact string and replaces it with a new string. | The skill modifies specific sections of existing files without rewriting the entire file. Preferred over Write for partial updates. |
| `Glob` | Search for files matching glob patterns (e.g., `**/*.ts`, `src/**/*.test.js`). Returns matching file paths sorted by modification time. | The skill needs to discover files by name pattern before reading or processing them. |
| `Grep` | Search file contents using regular expressions. Supports filtering by file type and glob patterns. Built on ripgrep. | The skill needs to find specific patterns, function definitions, imports, or text across a codebase. |

### Execution Tools

| Tool | Description | Use When |
|------|-------------|----------|
| `Bash` | Execute shell commands. Can run any CLI tool, build system, package manager, or script available on the user's system. | The skill needs to run commands (npm, git, docker, make, curl, etc.) or execute scripts. See [Bash Scoping](#bash-scoping) for restricted patterns. |

### Web Tools

| Tool | Description | Use When |
|------|-------------|----------|
| `WebFetch` | Fetch content from a URL. Retrieves web page content, API responses, or remote files. | The skill needs to download documentation, check API endpoints, or fetch remote resources. |
| `WebSearch` | Perform a web search and return results. | The skill needs to look up current information, find documentation, or research solutions not available locally. |

### Agent and Task Tools

| Tool | Description | Use When |
|------|-------------|----------|
| `Task` | Create and manage subagent tasks. Spawns a separate agent instance to handle a portion of work. | The skill needs to delegate complex subtasks or parallelize work across multiple agent instances. |
| `Skill` | Invoke another skill by name. Enables skill composition and chaining. | The skill orchestrates other skills or depends on another skill's output as input. |
| `AskUserQuestion` | Prompt the user for input during skill execution. Pauses execution and waits for a response. | The skill requires user decisions, confirmations, or input that cannot be inferred from context. |

### Workspace Tools

| Tool | Description | Use When |
|------|-------------|----------|
| `TodoWrite` | Create and manage to-do items in the workspace. | The skill tracks pending tasks, generates checklists, or manages work items. |
| `NotebookEdit` | Edit Jupyter notebook cells. Can modify code cells, markdown cells, and cell outputs. | The skill works with `.ipynb` files and needs to create or modify notebook content. |

## Bash Scoping

The `Bash` tool supports scoped patterns that restrict which commands the skill can execute. This provides finer-grained control than a blanket `Bash` permission.

### Syntax

```yaml
allowed-tools: Read, Bash(prefix:*)
```

The pattern `Bash(prefix:*)` allows the skill to run any bash command that starts with the specified prefix. The `*` wildcard matches any characters after the prefix.

### Common Bash Scoping Patterns

| Pattern | Allows | Example Commands |
|---------|--------|-----------------|
| `Bash(npm:*)` | npm commands | `npm install`, `npm run build`, `npm test` |
| `Bash(git:*)` | git commands | `git status`, `git diff`, `git log` |
| `Bash(docker:*)` | Docker commands | `docker build`, `docker run`, `docker ps` |
| `Bash(kubectl:*)` | Kubernetes commands | `kubectl get pods`, `kubectl describe`, `kubectl apply` |
| `Bash(terraform:*)` | Terraform commands | `terraform plan`, `terraform apply`, `terraform validate` |
| `Bash(python3:*)` | Python execution | `python3 script.py`, `python3 -m pytest` |
| `Bash(cargo:*)` | Rust cargo commands | `cargo build`, `cargo test`, `cargo clippy` |
| `Bash(pnpm:*)` | pnpm commands | `pnpm install`, `pnpm build`, `pnpm test` |

### Multiple Bash Scopes

You can include multiple scoped Bash entries to allow several command families:

```yaml
allowed-tools: Read, Write, Bash(npm:*), Bash(git:*), Bash(docker:*)
```

### Unscoped Bash

Using `Bash` without a pattern allows unrestricted command execution:

```yaml
allowed-tools: Read, Bash
```

This grants the skill access to any shell command. Use unscoped `Bash` only when the skill genuinely needs broad command access (e.g., a debugging skill that may need to run arbitrary diagnostic commands).

## Principle of Least Privilege

Every skill should request the minimum set of tools required to accomplish its task. Over-permissioning creates several risks:

- **Accidental side effects.** A skill with `Write` access that only needs to read files could accidentally overwrite data.
- **Security surface.** A skill with unscoped `Bash` could execute any command on the user's system.
- **User trust.** Users reviewing installed plugins can see the `allowed-tools` list. Minimal permissions signal that the skill is well-scoped and safe.

### Permission Levels

Think of tools in terms of ascending permission levels:

| Level | Tools | Risk Profile |
|-------|-------|-------------|
| **Read-only** | `Read`, `Glob`, `Grep` | No modifications to the filesystem or external state. Safest level. |
| **Read + Search** | `Read`, `Glob`, `Grep`, `WebFetch`, `WebSearch` | Adds network access but no local modifications. |
| **Read + Write** | `Read`, `Write`, `Edit`, `Glob`, `Grep` | Can modify local files. Moderate risk. |
| **Full local** | `Read`, `Write`, `Edit`, `Glob`, `Grep`, `Bash` | Full filesystem and command access. Higher risk. |
| **Full + Network** | All tools | Complete access to local system and network. Use only when necessary. |

### Auditing Permissions

When reviewing a plugin before installation, check the `allowed-tools` field in each SKILL.md to understand what the skill can do:

```bash
# Find all SKILL.md files and show their allowed-tools
grep -r "allowed-tools:" plugins/category/plugin-name/skills/
```

## Recommended Tool Combinations

The following sections provide recommended `allowed-tools` configurations for common skill types. These represent best practices and are not exhaustive.

### Read-Only Analysis Skill

Skills that analyze code, review configurations, or audit files without making changes.

```yaml
allowed-tools: Read, Glob, Grep
```

**Examples:** Code complexity analyzer, dependency auditor, license checker, style guide validator.

### Code Generation Skill

Skills that create new files based on templates, specifications, or user input.

```yaml
allowed-tools: Read, Write, Glob, Grep
```

Add `Edit` if the skill also modifies existing files (e.g., updating an index file after generating a component):

```yaml
allowed-tools: Read, Write, Edit, Glob, Grep
```

**Examples:** Component scaffolder, test generator, boilerplate creator, migration generator.

### Code Modification Skill

Skills that refactor, fix, or transform existing code.

```yaml
allowed-tools: Read, Write, Edit, Glob, Grep
```

**Examples:** Refactoring assistant, code formatter, import organizer, deprecation migrator.

### Build and Test Skill

Skills that run build systems, test suites, or validation commands.

```yaml
allowed-tools: Read, Glob, Grep, Bash(npm:*), Bash(git:*)
```

Include `Write` or `Edit` if the skill also fixes issues it discovers:

```yaml
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(npm:*), Bash(git:*)
```

**Examples:** CI pipeline runner, test executor, lint fixer, build optimizer.

### Web Research Skill

Skills that fetch external documentation, check APIs, or research solutions.

```yaml
allowed-tools: Read, Glob, Grep, WebFetch, WebSearch
```

Add file modification tools if the skill also applies what it finds:

```yaml
allowed-tools: Read, Write, Edit, Glob, Grep, WebFetch, WebSearch
```

**Examples:** Documentation fetcher, API compatibility checker, upgrade guide researcher.

### DevOps / Infrastructure Skill

Skills that manage infrastructure, containers, or cloud resources.

```yaml
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(docker:*), Bash(kubectl:*), Bash(terraform:*)
```

**Examples:** Terraform plan reviewer, Kubernetes manifest generator, Docker Compose optimizer.

### Orchestration Skill

Skills that coordinate multiple sub-tasks or invoke other skills.

```yaml
allowed-tools: Read, Glob, Grep, Task, Skill
```

Add `AskUserQuestion` if the skill needs user input at decision points:

```yaml
allowed-tools: Read, Glob, Grep, Task, Skill, AskUserQuestion
```

**Examples:** Multi-step workflow orchestrator, plugin pipeline runner, skill composer.

### Interactive Skill

Skills that require user input or confirmation during execution.

```yaml
allowed-tools: Read, Write, Edit, Glob, Grep, AskUserQuestion
```

**Examples:** Guided setup wizard, interactive migration tool, configuration interviewer.

### Data Science / Notebook Skill

Skills that work with Jupyter notebooks and data analysis workflows.

```yaml
allowed-tools: Read, Write, NotebookEdit, Glob, Grep, Bash(python3:*)
```

**Examples:** Notebook linter, cell executor, data pipeline scaffolder.

## Tool Interaction Patterns

Understanding how tools work together helps you design efficient skills.

### Discovery Pattern

Use `Glob` to find files, then `Read` to examine them, then `Grep` to search across them:

```
1. Glob("**/*.config.ts") → find config files
2. Read(each file) → examine contents
3. Grep("deprecated") → find specific patterns
```

Required tools: `Read, Glob, Grep`

### Find-and-Fix Pattern

Discover issues with read-only tools, then fix them with modification tools:

```
1. Grep("console.log") → find debug statements
2. Read(each file) → verify context
3. Edit(remove statement) → fix each occurrence
```

Required tools: `Read, Edit, Glob, Grep`

### Generate-and-Validate Pattern

Create files, then verify them with build tools:

```
1. Write(new files) → generate code
2. Bash("npm run typecheck") → verify types
3. Bash("npm test") → run tests
4. Edit(fix issues) → address failures
```

Required tools: `Read, Write, Edit, Glob, Grep, Bash(npm:*)`

### Research-and-Apply Pattern

Fetch external information, then apply it locally:

```
1. WebSearch("react 19 breaking changes") → research
2. WebFetch(migration guide URL) → get details
3. Grep("deprecated API") → find usage in codebase
4. Edit(update code) → apply changes
```

Required tools: `Read, Edit, Glob, Grep, WebFetch, WebSearch`

## Validation

The `allowed-tools` field is validated at multiple levels:

1. **YAML parsing.** The field must be a valid string. Syntax errors in YAML prevent the skill from loading.

2. **Tool name validation.** The universal validator (`validate-skills-schema.py`) checks that every tool name in the `allowed-tools` list is a recognized tool. Invalid tool names produce warnings or errors depending on the validation tier.

3. **Enterprise compliance.** The 100-point enterprise rubric scores skills partially based on `allowed-tools` appropriateness. Skills that request excessive permissions receive lower scores.

Run validation locally:

```bash
# Standard validation (checks tool names)
python3 scripts/validate-skills-schema.py --verbose plugins/category/your-plugin/

# Enterprise validation (scores permission appropriateness)
python3 scripts/validate-skills-schema.py --enterprise --verbose plugins/category/your-plugin/
```

## Common Mistakes

| Mistake | Impact | Fix |
|---------|--------|-----|
| Using `bash` (lowercase) instead of `Bash` | Tool name not recognized | Tool names are case-sensitive: use `Bash` |
| Listing tools the skill never uses | Unnecessary permission scope | Audit the skill body and remove unused tools |
| Using unscoped `Bash` when only npm is needed | Over-permissioning | Use `Bash(npm:*)` instead of `Bash` |
| Omitting `Read` when `Edit` is listed | Edit requires reading first | Always include `Read` alongside `Edit` |
| Forgetting `Glob` for file discovery | Skill cannot find files by pattern | Add `Glob` if the skill searches for files |
| Using `WebFetch` without `WebSearch` (or vice versa) for research | Incomplete research capability | Include both if the skill does general web research |
| Typos in tool names (e.g., `Readfile`, `Search`) | Tool not recognized | Check this reference for exact names |
