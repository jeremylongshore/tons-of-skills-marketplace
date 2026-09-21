---
title: "Slash Commands and Hooks"
description: "How to define slash commands in Claude Code plugins using commands/*.md files, and how to configure lifecycle hooks (pre-tool-call, post-tool-call) in SKILL.md frontmatter for automated behaviors."
section: "concepts"
order: 4
keywords:
  - "Claude Code commands"
  - "slash commands"
  - "Claude Code hooks"
  - "pre-tool-call"
  - "post-tool-call"
  - "lifecycle hooks"
  - "commands/*.md"
  - "CLAUDE_PLUGIN_ROOT"
officialLinks:
  - title: "Claude Code Custom Slash Commands"
    url: "https://code.claude.com/docs/en/slash-commands"
  - title: "Claude Code Hooks"
    url: "https://code.claude.com/docs/en/hooks"
  - title: "Claude Code Plugins Overview"
    url: "https://code.claude.com/docs/en/plugins"
relatedDocs:
  - "concepts/plugins"
  - "concepts/skills"
  - "concepts/agents"
  - "reference/skill-frontmatter"
---

Slash commands and hooks are two complementary mechanisms for controlling Claude Code behavior. Commands give users explicit control -- type `/deploy` and Claude runs your deployment workflow. Hooks give developers automated control -- every time Claude calls a specific tool, your hook runs before or after it without any user intervention. Together, they cover both ends of the interaction spectrum: deliberate user actions and invisible guardrails.

## Slash Commands

### What They Are

A slash command is a markdown file in a plugin's `commands/` directory that defines an action users can invoke by typing `/command-name` in Claude Code. Unlike skills (which activate automatically based on context), commands require explicit invocation. This makes them ideal for workflows that should only run when the user specifically requests them.

**Common use cases for commands:**

- Deployment workflows (`/deploy`, `/rollback`)
- Code generation from templates (`/scaffold`, `/generate-api`)
- Analysis and reporting (`/audit`, `/coverage-report`)
- Repository maintenance (`/clean`, `/update-deps`)
- Documentation generation (`/generate-docs`, `/api-docs`)

### Command File Structure

Command files live in the `commands/` directory of a plugin:

```
my-plugin/
└── commands/
    ├── deploy.md
    ├── scaffold.md
    ├── audit.md
    └── update-deps.md
```

Each file name (minus the `.md` extension) becomes the command name. A file named `deploy.md` creates the `/deploy` command. Use kebab-case for multi-word commands: `update-deps.md` creates `/update-deps`.

### Command Frontmatter

Every command file begins with YAML frontmatter that defines its metadata:

```yaml
---
name: deploy
description: "Deploy the current branch to staging or production with pre-flight checks"
user-invocable: true
argument-hint: "<environment>"
---
```

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `name` | Yes | string | Command identifier (must match filename) |
| `description` | Yes | string | One-line summary shown in the `/` menu |
| `user-invocable` | No | boolean | Whether the command appears in the `/` menu (default: `true`) |
| `argument-hint` | No | string | Hint text shown after the command name in the menu |

#### The description Field

The description serves double duty: it is displayed in the Claude Code `/` menu as help text, and it helps Claude understand when to suggest the command. Write descriptions that are concise but informative:

```yaml
# Good: tells the user what it does and when to use it
description: "Run security audit on all source files and generate a SARIF report"

# Too vague
description: "Security stuff"

# Too long for a menu item
description: "This command performs a comprehensive security audit of the entire codebase including static analysis, dependency checking, secret scanning, and generates a detailed SARIF format report suitable for GitHub Advanced Security integration"
```

Aim for 50-100 characters. The description should answer "what does this do?" in one glance.

#### The argument-hint Field

When a command accepts arguments, the `argument-hint` field tells users what to provide:

```yaml
# Single argument
argument-hint: "<environment>"       # /deploy staging
argument-hint: "<file-path>"         # /analyze src/index.ts
argument-hint: "<component-name>"    # /scaffold UserProfile

# Multiple arguments
argument-hint: "<source> <target>"   # /migrate users orders
```

Inside the command body, arguments are accessible through substitution variables:

| Variable | Value |
|----------|-------|
| `$ARGUMENTS` | The full argument string |
| `$0` | First argument |
| `$1` | Second argument |
| `$2` through `$9` | Subsequent arguments |

#### Hidden Commands

Setting `user-invocable: false` hides a command from the `/` menu while keeping it available for programmatic invocation by other commands, skills, or agents:

```yaml
---
name: internal-validate
description: "Internal validation step used by the deploy command"
user-invocable: false
---
```

This is useful for building multi-step workflows where a top-level command delegates to hidden helper commands.

### Command Body

The body of a command file contains the instructions Claude follows when the command is invoked. Write it in the same directive style as skill bodies -- clear, specific, and structured.

**Example: A complete deploy command**

```markdown
---
name: deploy
description: "Deploy current branch to staging or production with pre-flight checks"
argument-hint: "<environment>"
---

## Pre-Flight Checks

Before deploying to `$0`, verify all of the following:

1. **Clean working tree.** Run `git status` and confirm no uncommitted changes.
   If there are uncommitted changes, stop and ask the user to commit or stash.

2. **Tests passing.** Run `npm test` and confirm all tests pass. If any test
   fails, stop and report the failures. Do not deploy with failing tests.

3. **Build succeeds.** Run `npm run build` and confirm it completes without
   errors. Check that the `dist/` directory is populated.

4. **Environment validation.** Confirm the target environment is valid:
   - `staging` — deploys to staging.example.com
   - `production` — deploys to example.com (requires confirmation)
   - Any other value — reject with an error message

## Deployment

If all pre-flight checks pass:

### Staging

```bash
npm run deploy:staging
```

Verify the deployment by checking https://staging.example.com/health.

### Production

**Production deployments require explicit user confirmation.** Before running
the deploy command, ask the user: "This will deploy to production. Continue?"

```bash
npm run deploy:production
```

After deployment:

1. Check https://example.com/health
2. Verify the deployed version matches the current git SHA
3. Monitor error rates for 2 minutes using `npm run monitor`

## Post-Deploy

Report the deployment status:

- Environment deployed to
- Git SHA deployed
- Health check result
- Any warnings from the build or deploy process

```

### Command Design Patterns

#### The Workflow Command

Orchestrates a multi-step process with checkpoints:

```markdown
---
name: release
description: "Prepare and publish a new release with changelog and tags"
argument-hint: "<version>"
---

## Steps

1. Validate that `$0` is a valid semver version
2. Update version in package.json
3. Generate changelog from commits since last tag
4. Create git tag v$0
5. Push tag and trigger CI pipeline
6. Wait for CI to pass, then publish to npm
```

### The Analysis Command

Gathers data and produces a report:

```markdown
---
name: coverage-report
description: "Generate test coverage report with gap analysis"
---

## Analysis

1. Run test suite with coverage: `npm run test -- --coverage`
2. Parse the coverage report from `coverage/lcov-report/index.html`
3. Identify files below 80% line coverage
4. For each under-covered file, identify the specific untested code paths
5. Produce a prioritized list of files needing additional tests
```

#### The Generator Command

Creates files from templates or specifications:

```markdown
---
name: scaffold
description: "Generate a new feature module with tests, types, and documentation"
argument-hint: "<feature-name>"
---

Create the following files for the `$0` feature:

1. `src/features/$0/index.ts` — barrel export
2. `src/features/$0/$0.ts` — main implementation
3. `src/features/$0/$0.test.ts` — test file with basic structure
4. `src/features/$0/$0.types.ts` — TypeScript interfaces
5. `src/features/$0/README.md` — feature documentation

Follow the patterns established in `src/features/auth/` as a reference
implementation.
```

## Hooks

### What They Are

Hooks are lifecycle callbacks that execute automatically when Claude uses specific tools. They are configured in a skill's YAML frontmatter and run shell commands before or after a tool call, without any user interaction.

Hooks are conceptually similar to Git hooks or CI pipeline hooks: they are invisible guardrails that enforce policies, validate actions, or perform side effects automatically.

**Common use cases for hooks:**

- Linting files before they are written
- Running tests after code is edited
- Validating configuration files before they are saved
- Logging tool usage for audit trails
- Formatting code after generation

### Hook Types

Two hook types are available:

| Hook | Timing | Use Case |
|------|--------|----------|
| `pre-tool-call` | Before the tool executes | Validation, permission checks, input sanitization |
| `post-tool-call` | After the tool executes | Formatting, testing, logging, verification |

### Hook Configuration

Hooks are defined in the `hooks` field of a SKILL.md's frontmatter:

```yaml
---
name: safe-writer
description: |
  When writing TypeScript files. Automatically formats and lints
  all written files.
allowed-tools: Read, Write, Edit, Bash(npm:*), Glob
version: 1.0.0
author: Dev Team
license: MIT
hooks:
  pre-tool-call:
    - tool: Write
      command: "echo 'Writing file: ${CLAUDE_TOOL_INPUT_FILE}'"
  post-tool-call:
    - tool: Write
      command: "${CLAUDE_PLUGIN_ROOT}/scripts/format-and-lint.sh ${CLAUDE_TOOL_INPUT_FILE}"
    - tool: Edit
      command: "${CLAUDE_PLUGIN_ROOT}/scripts/format-and-lint.sh ${CLAUDE_TOOL_INPUT_FILE}"
---
```

### Hook Structure

Each hook entry specifies:

| Field | Description |
|-------|-------------|
| `tool` | The tool name this hook applies to (e.g., `Write`, `Edit`, `Bash`) |
| `command` | Shell command to execute |

### Path Variables in Hooks

Hooks support the same path variables as skill bodies, plus tool-specific variables:

| Variable | Description |
|----------|-------------|
| `${CLAUDE_PLUGIN_ROOT}` | Root directory of the plugin |
| `${CLAUDE_SKILL_DIR}` | Directory containing the SKILL.md |
| `${CLAUDE_TOOL_INPUT_FILE}` | File path argument passed to the tool |

**Always use `${CLAUDE_PLUGIN_ROOT}`** to reference scripts and resources within your plugin. This ensures hooks work correctly regardless of where the plugin is installed:

```yaml
# Correct: portable path
command: "${CLAUDE_PLUGIN_ROOT}/scripts/validate.sh"

# Wrong: hardcoded path
command: "/home/user/.claude/plugins/my-plugin/scripts/validate.sh"
```

### Hook Examples

#### Auto-Format on Write

Format every file Claude writes using Prettier:

```yaml
hooks:
  post-tool-call:
    - tool: Write
      command: "npx prettier --write ${CLAUDE_TOOL_INPUT_FILE} 2>/dev/null || true"
    - tool: Edit
      command: "npx prettier --write ${CLAUDE_TOOL_INPUT_FILE} 2>/dev/null || true"
```

The `|| true` suffix prevents hook failures from blocking Claude's workflow. Formatting is nice to have but should not stop execution.

#### Test After Edit

Run relevant tests whenever Claude edits a source file:

```yaml
hooks:
  post-tool-call:
    - tool: Edit
      command: "${CLAUDE_PLUGIN_ROOT}/scripts/run-related-tests.sh ${CLAUDE_TOOL_INPUT_FILE}"
```

The helper script (`run-related-tests.sh`) might look like:

```bash
#!/bin/bash
# Find and run test file corresponding to the edited source file
SOURCE_FILE="$1"
TEST_FILE="${SOURCE_FILE%.ts}.test.ts"

if [ -f "$TEST_FILE" ]; then
  npx vitest run "$TEST_FILE" --reporter=verbose 2>&1 | tail -20
fi
```

#### Validation Gate

Prevent Claude from writing invalid configuration:

```yaml
hooks:
  pre-tool-call:
    - tool: Write
      command: "${CLAUDE_PLUGIN_ROOT}/scripts/validate-config.sh ${CLAUDE_TOOL_INPUT_FILE}"
```

If the pre-tool-call hook exits with a non-zero status, the tool call is blocked. This creates a hard gate that prevents invalid files from being written.

#### Audit Logging

Log every Bash command Claude executes for compliance:

```yaml
hooks:
  pre-tool-call:
    - tool: Bash
      command: "echo \"$(date -Iseconds) BASH: ${CLAUDE_TOOL_INPUT_FILE}\" >> ${CLAUDE_PLUGIN_ROOT}/audit.log"
```

### Hook Design Principles

**Keep hooks fast.** Hooks run synchronously -- Claude waits for them to complete before proceeding. A hook that takes 30 seconds to run will make Claude feel sluggish. If you need long-running validation, consider running it asynchronously or only on specific file patterns.

**Make hooks resilient.** Add `2>/dev/null`, `|| true`, or explicit error handling to prevent hook failures from crashing Claude's workflow. A formatting hook should not prevent Claude from completing a task because Prettier is not installed.

**Scope hooks narrowly.** Apply hooks to specific tools rather than all tools. A formatting hook should apply to `Write` and `Edit`, not to `Read` or `Glob`.

**Use hooks for policies, not features.** Hooks are best for enforcing invariants (code is always formatted, configs are always valid, actions are always logged). If the behavior is the primary purpose of the skill, put it in the skill body instructions instead.

## Commands vs Skills vs Hooks: Choosing the Right Mechanism

Understanding when to use each mechanism avoids confusion and produces cleaner plugin designs:

| Mechanism | Trigger | Visibility | Best For |
|-----------|---------|------------|----------|
| Command | User types `/name` | Explicit, in menu | One-off workflows, generators, reports |
| Skill | Claude auto-detects relevance | Invisible to user | Domain expertise, coding patterns |
| Hook | Tool call occurs | Invisible to user | Validation, formatting, logging |

**Practical example:** Consider a plugin for a Go project.

- **Command** (`/go-bench`): User explicitly requests a benchmark run with specific parameters.
- **Skill** (`go-patterns/SKILL.md`): Automatically activates when Claude writes Go code, guiding it to follow idiomatic patterns.
- **Hook** (`post-tool-call` on `Write`): Runs `gofmt` on every `.go` file Claude writes, ensuring consistent formatting without the user asking.

All three can coexist in the same plugin, each handling a different aspect of the Go development workflow.

## Building Reusable Commands

### Commands That Call Other Commands

Commands can reference other commands in their instructions:

```markdown
---
name: full-release
description: "Run the complete release pipeline"
argument-hint: "<version>"
---

Execute these steps in order:

1. Run `/lint-check` to ensure code quality
2. Run `/test-all` to verify all tests pass
3. Run `/changelog $0` to generate the changelog
4. Run `/deploy production` to deploy the release
```

### Commands That Delegate to Agents

Commands can delegate work to specialized agents:

```markdown
---
name: security-review
description: "Comprehensive security audit of the current codebase"
---

Delegate this work to the security-auditor agent. Pass all findings back
as a structured report with severity ratings.
```

### Commands with Dynamic Context

Commands can use DCI to adapt behavior based on the current environment:

```markdown
---
name: setup
description: "Initialize development environment based on project type"
---

## Detected Environment

!`[ -f package.json ] && echo 'Node.js project' || echo 'Not a Node.js project'`
!`[ -f requirements.txt ] && echo 'Python project' || echo 'Not a Python project'`
!`[ -f go.mod ] && echo 'Go project' || echo 'Not a Go project'`

Based on the detected project type above, run the appropriate setup sequence.
```

## Script Conventions

When plugins include shell scripts referenced by hooks or commands, follow these conventions:

1. **Make scripts executable.** All `.sh` files must have `chmod +x` set. CI validation enforces this.

2. **Use portable paths.** Always reference scripts via `${CLAUDE_PLUGIN_ROOT}`:

```yaml
command: "${CLAUDE_PLUGIN_ROOT}/scripts/my-hook.sh"
```

1. **Include shebangs.** Every script should start with `#!/bin/bash` or `#!/usr/bin/env bash`.

2. **Handle missing dependencies.** Scripts should check for required tools and fail gracefully:

```bash
#!/bin/bash
if ! command -v prettier &> /dev/null; then
  echo "prettier not found, skipping formatting"
  exit 0
fi
prettier --write "$1"
```

## Next Steps

- Learn about the plugin structure that contains commands and hooks: [What Are Claude Code Plugins?](/docs/concepts/plugins)
- Understand auto-activating skills: [Understanding Agent Skills (SKILL.md)](/docs/concepts/skills)
- Explore how agents handle autonomous workflows: [Claude Code Agents and Subagents](/docs/concepts/agents)
- See how MCP servers expose external tools: [MCP Servers in Claude Code Plugins](/docs/concepts/mcp-servers)
