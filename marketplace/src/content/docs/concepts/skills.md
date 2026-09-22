---
title: "Understanding Agent Skills (SKILL.md)"
description: "Deep dive into SKILL.md files — the auto-activating instruction sets that give Claude Code domain expertise. Learn frontmatter fields, body structure, dynamic context injection, and path variables."
section: "concepts"
order: 2
keywords:
  - "SKILL.md"
  - "Claude Code skills"
  - "agent skills"
  - "auto-activating skills"
  - "allowed-tools"
  - "dynamic context injection"
  - "skill frontmatter"
  - "Claude Code plugin skills"
officialLinks:
  - title: "Claude Code Skills Documentation"
    url: "https://code.claude.com/docs/en/skills"
  - title: "AgentSkills.io Specification"
    url: "https://agentskills.io"
  - title: "Claude Code Plugins Overview"
    url: "https://code.claude.com/docs/en/plugins"
relatedDocs:
  - "concepts/plugins"
  - "concepts/agents"
  - "concepts/commands-and-hooks"
  - "reference/skill-frontmatter"
---

Skills are the most important building block in the Claude Code plugin ecosystem. A skill is a `SKILL.md` file that contains structured instructions telling Claude how to perform a specific task, follow a particular methodology, or apply domain-specific knowledge. Unlike slash commands (which users invoke explicitly), skills activate automatically when Claude determines they are relevant to the current conversation.

The [Tons of Skills marketplace](/) contains over 2,834 individual skills across 418 plugins, covering everything from Terraform module patterns to React component testing to database migration workflows.

## What Makes Skills Special

Skills differ from other forms of AI instruction (system prompts, CLAUDE.md files, ad-hoc instructions) in several important ways:

**Auto-activation.** Skills do not require the user to remember and type a command. Claude reads the skill's `description` field and activates it when the description matches the user's current intent. This makes skills feel like built-in capabilities rather than add-ons.

**Tool scoping.** Each skill declares exactly which tools it needs via the `allowed-tools` field. This provides a security boundary -- a documentation-only skill cannot accidentally execute shell commands, and a code generation skill cannot read files it should not access.

**Composability.** Skills can reference supporting files, inject dynamic context from the environment, and delegate work to agents. This makes it possible to build complex, multi-step workflows from focused, single-purpose skill definitions.

**Versioning and metadata.** Skills carry version numbers, author information, license declarations, and compatibility tags. This metadata enables the marketplace to track quality, attribute contributions, and ensure compatibility.

## Anatomy of a SKILL.md File

Every SKILL.md file has two parts: YAML frontmatter (delimited by `---`) and a markdown body containing the actual instructions.

```markdown
---
name: react-testing
description: |
  When writing or reviewing React component tests.
  Activates for Jest, React Testing Library, and Vitest test files.
  Trigger phrases: "write tests", "test this component", "add test coverage".
allowed-tools: Read, Write, Edit, Bash(npm:*), Glob, Grep
version: 1.0.0
author: Jane Developer <jane@example.com>
license: MIT
tags: [react, testing, jest, vitest]
---

## Testing Philosophy

Write tests that verify behavior, not implementation details. Every test should
answer the question: "Does this component do what users expect?"

## File Naming

Place test files adjacent to the component they test:

- `Button.tsx` -> `Button.test.tsx`
- `useAuth.ts` -> `useAuth.test.ts`

## Test Structure

Use the Arrange-Act-Assert pattern:

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from './Button';

describe('Button', () => {
  it('calls onClick handler when clicked', () => {
    // Arrange
    const handleClick = vi.fn();
    render(<Button onClick={handleClick}>Submit</Button>);

    // Act
    fireEvent.click(screen.getByRole('button', { name: /submit/i }));

    // Assert
    expect(handleClick).toHaveBeenCalledOnce();
  });
});
```

## Coverage Requirements

- All exported components must have at least one test
- Event handlers must be tested with user interaction simulation
- Error states and loading states must be covered
- Accessibility: test with `screen.getByRole` over `getByTestId`

```

## Frontmatter Fields

The frontmatter section defines the skill's metadata and behavioral constraints. Fields fall into two categories: required (for marketplace compliance) and optional (for advanced behavior).

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Unique skill identifier within the plugin (kebab-case) |
| `description` | string | When Claude should activate this skill. Include trigger phrases |
| `allowed-tools` | string | Comma-separated list of tools this skill may use |
| `version` | string | Semantic version of the skill |
| `author` | string | Author name, optionally with email in angle brackets |
| `license` | string | SPDX license identifier |

### Optional Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `model` | string | (default model) | LLM model override: `sonnet`, `haiku`, or `opus` |
| `context` | string | (inline) | Set to `fork` to run the skill in a subagent |
| `agent` | string | (none) | Subagent type to use when `context: fork` |
| `user-invocable` | boolean | true | Set to `false` to hide from the `/` menu |
| `argument-hint` | string | (none) | Autocomplete hint shown in the `/` menu (e.g., `"<file-path>"`) |
| `hooks` | object | (none) | Lifecycle hooks (`pre-tool-call`, `post-tool-call`) |
| `compatibility` | string | (none) | Environment requirements (e.g., `"Node.js >= 18"`) |
| `compatible-with` | string | (none) | Platform compatibility (e.g., `claude-code, cursor`) |
| `tags` | array | [] | Discovery tags for categorization and search |

### The Description Field

The `description` field is the most important field in the entire frontmatter. It controls when Claude activates the skill. Write it as a conditional statement that describes the situations where this skill applies, and include specific trigger phrases that users are likely to say.

**Good description:**

```yaml
description: |
  When writing or modifying Dockerfile or docker-compose.yml files.
  When debugging container build failures or multi-stage build issues.
  Trigger phrases: "dockerize this", "fix my Dockerfile", "add Docker support",
  "container build failing", "optimize Docker image size".
```

**Poor description:**

```yaml
description: "Docker helper skill"
```

The first example gives Claude rich context for matching. The second is too vague to reliably activate.

### The allowed-tools Field

This field is a comma-separated list of tools the skill is permitted to use. It acts as an allowlist -- Claude will only use the listed tools when this skill is active.

**Valid tools:**

`Read`, `Write`, `Edit`, `Bash`, `Glob`, `Grep`, `WebFetch`, `WebSearch`, `Task`, `TodoWrite`, `NotebookEdit`, `AskUserQuestion`, `Skill`

**Tool scoping with Bash:**

The `Bash` tool supports glob-style scoping to restrict which commands can be executed:

```yaml
# Allow only npm and npx commands
allowed-tools: Read, Edit, Bash(npm:*), Bash(npx:*)

# Allow only git commands
allowed-tools: Read, Glob, Grep, Bash(git:*)

# Allow all bash commands (use sparingly)
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
```

Principle of least privilege applies: request only the tools your skill genuinely needs. A skill that analyzes code but never modifies it should not include `Write` or `Edit`.

## The Skill Body

Everything below the frontmatter delimiter is the skill body -- the actual instructions Claude follows when the skill is active. This is where the substance lives.

### Writing Effective Instructions

The body should be written in clear, directive markdown. Use second person ("Write tests that...") or imperative mood ("Use the Arrange-Act-Assert pattern"). Avoid hedging language like "you might want to consider" -- be direct.

**Structure recommendations:**

- Use `## H2` headings to organize major sections
- Use `### H3` headings for subsections within a topic
- Include code blocks with language tags for all examples
- Use tables for reference data (configuration options, API fields, etc.)
- Use bold for key terms and inline code for identifiers, file names, and commands

### Supporting File References

Skills can reference additional files that Claude will load on demand. Use standard markdown links with relative paths:

```markdown
For API details, see the API reference.
Review the examples directory for templates.
```

When Claude encounters these links while executing a skill, it uses the `Read` tool to load the referenced file. This allows you to keep the main SKILL.md focused while providing deep reference material in supporting files.

### Path Variables

Two path variables are available for use in skill bodies:

| Variable | Resolves To | Use Case |
|----------|-------------|----------|
| `${CLAUDE_SKILL_DIR}` | The directory containing this SKILL.md | Referencing files relative to the skill |
| `${CLAUDE_PLUGIN_ROOT}` | The root directory of the plugin | Referencing files elsewhere in the plugin |
| `${CLAUDE_PLUGIN_DATA}` | Persistent data directory for the plugin | Storing state that survives updates |

Use these in bash commands and DCI expressions:

```markdown
Load the configuration template:

`cat ${CLAUDE_SKILL_DIR}/templates/config.yaml`
```

The `${CLAUDE_PLUGIN_DATA}` directory (available in Claude Code v2.1.78+) persists across plugin updates and reinstalls, making it suitable for caches, user preferences, or learned patterns.

### String Substitutions

Skills can accept arguments from users. When a user invokes a skill with arguments, these substitution variables are replaced before Claude processes the skill body:

| Variable | Description |
|----------|-------------|
| `$ARGUMENTS` | The full argument string |
| `$0` through `$9` | Individual positional arguments |
| `${CLAUDE_SESSION_ID}` | Current session identifier |

Pair these with the `argument-hint` frontmatter field to guide users:

```yaml
---
name: analyze-file
argument-hint: "<file-path>"
# ...
---

Analyze the file at `$ARGUMENTS` for security vulnerabilities.
```

## Dynamic Context Injection (DCI)

Dynamic context injection is a powerful feature that lets skills run shell commands at activation time and inject the output directly into the skill body. This eliminates the need for Claude to spend tool-call rounds gathering environmental information.

### Syntax

DCI expressions use the `` !`command` `` syntax on their own line:

```markdown
## Current Environment

!`node --version 2>/dev/null || echo 'Node.js not installed'`

!`git branch --show-current 2>/dev/null || echo 'Not a git repository'`

!`ls package.json 2>/dev/null && echo 'Node.js project detected' || echo 'No package.json found'`
```

When Claude activates this skill, the commands execute and their output replaces the DCI expressions in the skill body. Claude then reads the enriched instructions with real-time environmental data already embedded.

### Best Practices for DCI

**Always include fallbacks.** Commands may fail if a tool is not installed or the context is wrong. Use `|| echo 'fallback message'` to ensure the skill body remains coherent:

```markdown
!`terraform version 2>/dev/null || echo 'Terraform not installed'`
```

**Keep output small.** DCI injects output verbatim into the skill body, consuming context window space. Use summaries and counts rather than full file contents:

```markdown
# Good: summary
!`wc -l src/**/*.ts 2>/dev/null | tail -1`

# Bad: entire file contents
!`cat src/config.ts`
```

**Use for discovery, not execution.** DCI is designed to pre-load information that helps Claude make better decisions. Do not use it to perform the actual task -- that is what the skill body instructions and tool calls are for.

**Common DCI patterns:**

```markdown
# Detect package manager
!`[ -f pnpm-lock.yaml ] && echo 'pnpm' || ([ -f yarn.lock ] && echo 'yarn' || echo 'npm')`

# Get project language/framework
!`cat package.json 2>/dev/null | grep -o '"react"\|"vue"\|"svelte"\|"angular"' | head -1`

# List available scripts
!`cat package.json 2>/dev/null | python3 -c "import sys,json; [print(k) for k in json.load(sys.stdin).get('scripts',{})]"`

# Check CI status
!`gh run list --limit 3 --json status,conclusion,name 2>/dev/null || echo 'gh CLI not available'`
```

## Skill Activation Flow

Understanding how Claude decides to activate a skill helps you write better descriptions and structure your skills effectively.

1. **User sends a message.** The user asks Claude to do something (e.g., "Write tests for the AuthProvider component").

2. **Description matching.** Claude compares the user's intent against the `description` fields of all installed skills. Skills whose descriptions mention relevant concepts (testing, React, components) score higher.

3. **Skill loading.** Claude loads the matching skill's frontmatter and body into its context. If the skill has DCI expressions, they execute first and their output is injected.

4. **Tool scoping.** Claude's available tools are constrained to those listed in `allowed-tools` for the duration of this skill's execution.

5. **Instruction following.** Claude follows the instructions in the skill body, using the permitted tools to accomplish the task.

6. **Supporting file loading.** If the skill body contains markdown links to supporting files, Claude may load them on demand using the Read tool.

## Skill Organization

Skills live inside a plugin's `skills/` directory, each in its own subdirectory:

```
my-plugin/
└── skills/
    ├── code-review/
    │   ├── SKILL.md           # Main skill file
    │   ├── reference.md       # Supporting reference
    │   └── examples/
    │       └── patterns.md    # Example patterns
    ├── security-scan/
    │   └── SKILL.md
    └── performance-audit/
        └── SKILL.md
```

Each skill subdirectory must contain exactly one `SKILL.md` file. Supporting files (reference documents, templates, examples) can live alongside it in the same directory or in subdirectories.

### Naming Conventions

- Skill directory names use kebab-case: `code-review`, `security-scan`
- The skill file is always named `SKILL.md` (uppercase)
- The `name` field in frontmatter should match the directory name
- Supporting files use descriptive kebab-case names: `api-reference.md`, `common-patterns.md`

## Quality Standards

The Tons of Skills marketplace evaluates skills using a 100-point enterprise compliance rubric. High-scoring skills share these characteristics:

- **Substantive body content** (500+ words of genuine instructions, not boilerplate)
- **Complete frontmatter** with all required fields filled accurately
- **Specific descriptions** with trigger phrases that enable reliable auto-activation
- **Minimal tool permissions** requesting only what is needed
- **Code examples** with language-tagged fenced code blocks
- **Structured sections** using H2/H3 headings for scannable organization
- **No placeholder text** -- every section contains real, actionable content

You can check your skill's compliance score locally:

```bash
python3 scripts/validate-skills-schema.py --enterprise --verbose plugins/my-category/my-plugin/
```

Skills scoring below 70 points receive a D or F grade and are flagged for remediation. The marketplace displays grades on the [Skills](/skills) page to help users identify high-quality skills.

## Common Patterns

### The Domain Expert Skill

Teaches Claude deep knowledge about a specific technology:

```yaml
---
name: kubernetes-troubleshoot
description: |
  When debugging Kubernetes pod failures, CrashLoopBackOff errors,
  OOMKilled events, or cluster networking issues.
allowed-tools: Read, Bash(kubectl:*), Bash(helm:*), Grep, Glob
version: 1.0.0
author: DevOps Team
license: MIT
tags: [kubernetes, debugging, devops]
---
```

### The Workflow Skill

Guides Claude through a multi-step process:

```yaml
---
name: release-checklist
description: |
  When preparing a production release, cutting a release branch,
  or running pre-release validation.
allowed-tools: Read, Bash(git:*), Bash(npm:*), Glob, Grep
version: 1.0.0
author: Release Engineering
license: MIT
context: fork
agent: Explore
---
```

### The Guard Rail Skill

Enforces constraints without performing the main task:

```yaml
---
name: security-policy
description: |
  When writing code that handles authentication, authorization,
  secrets, API keys, or user credentials.
allowed-tools: Read, Grep, Glob
version: 1.0.0
author: Security Team
license: MIT
user-invocable: false
---
```

Setting `user-invocable: false` hides the skill from the `/` menu while allowing it to activate automatically when security-relevant work is detected.

## Next Steps

- Understand how agents complement skills: [Claude Code Agents and Subagents](/docs/concepts/agents)
- Learn about explicit invocation with commands: [Slash Commands and Hooks](/docs/concepts/commands-and-hooks)
- Browse available skills: [Skills Directory](/skills)
- Explore plugins that contain skills: [Explore Plugins](/explore)
