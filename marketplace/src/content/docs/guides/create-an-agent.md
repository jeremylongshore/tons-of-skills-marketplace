---
title: "How to Create a Claude Code Agent"
description: "Guide to creating autonomous Claude Code agents. Learn the difference between agents and skills, write agent frontmatter with capabilities and disallowedTools, set maxTurns and effort, and test agent behavior."
section: "guides"
order: 3
keywords:
  - "agent"
  - "autonomous agent"
  - "disallowedTools"
  - "maxTurns"
  - "capabilities"
  - "sub-agent"
  - "Claude Code agent"
  - "agent development"
officialLinks:
  - title: "Anthropic Claude Code Documentation"
    url: "https://code.claude.com/docs/en/"
  - title: "Anthropic Agents Reference"
    url: "https://code.claude.com/docs/en/agents"
relatedDocs:
  - "concepts/agents"
  - "reference/skill-frontmatter"
---

## Agents vs. Skills vs. Commands

Before building an agent, understand when each component type is appropriate:

| Component | Invocation | Tool Control | Autonomy |
|-----------|-----------|--------------|----------|
| **Command** | User types `/command-name` | Inherits session tools | Single response |
| **Skill** | Auto-activates on context | Allowlist (`allowed-tools`) | Single response |
| **Agent** | Called as sub-agent | Denylist (`disallowedTools`) | Multi-turn loop up to `maxTurns` |

**Use an agent when:**

- The task requires multiple autonomous iterations (explore, analyze, fix, verify)
- The agent needs broad tool access with only a few restrictions
- The workflow benefits from independent reasoning without user prompts at each step
- The task is a distinct specialty area (security scanning, performance profiling, code review)

**Use a skill instead when:**

- The task completes in a single pass
- You want tight control over which tools are available (allowlist)
- Auto-activation based on context is the desired trigger

**Use a command instead when:**

- The user should explicitly invoke it from the slash menu
- The task is straightforward and does not require iteration

## Step 1: Plan Your Agent

Agents are specialists. Each agent should own a specific domain and execute autonomously within it. Answer these questions during planning:

1. **What is the agent's specialty?** Define a clear domain: "security vulnerability scanning", "database migration planning", "API integration testing".

2. **What tools should be restricted?** Agents use a denylist (`disallowedTools`). Think about which tools could cause harm if used without supervision. For a read-only auditing agent, deny `Write`, `Edit`, and `Bash`.

3. **How many iterations are needed?** A simple analysis agent might need 5 turns. A complex scanning agent that reads dozens of files and cross-references findings might need 20.

4. **What expertise level is required?** This affects how the agent presents itself and the depth of its analysis. Use `advanced` or `expert` for specialized technical domains.

## Step 2: Create the Agent File

Agent files live in the `agents/` directory of a plugin:

```
my-plugin/
├── .claude-plugin/
│   └── plugin.json
├── agents/
│   └── code-reviewer.md     # <-- agent file
└── README.md
```

Create the file:

```bash
mkdir -p my-plugin/agents
touch my-plugin/agents/code-reviewer.md
```

The filename becomes the agent's identifier. Use kebab-case: `code-reviewer.md`, `security-scanner.md`, `performance-profiler.md`.

## Step 3: Write Agent Frontmatter

The frontmatter block configures the agent's identity, capabilities, and constraints. Here is a complete example:

```yaml
---
name: code-reviewer
description: "Reviews code changes for quality, correctness, security, and adherence to project conventions"
capabilities:
  - "Static code analysis and pattern detection"
  - "Security vulnerability identification"
  - "Performance anti-pattern detection"
  - "Style and convention compliance checking"
  - "Test coverage gap analysis"
model: sonnet
effort: high
maxTurns: 20
expertise_level: expert
activation_priority: medium
---
```

### Frontmatter Field Reference

#### Required Fields

**`name`** -- Unique identifier for the agent in kebab-case. Must match the filename (without `.md`).

```yaml
name: code-reviewer
```

**`description`** -- A 20-200 character summary of what the agent does. This is displayed when listing available agents and used by Claude Code to decide when to delegate to the agent.

```yaml
description: "Reviews code changes for quality, correctness, security, and adherence to project conventions"
```

#### Recommended Fields

**`capabilities`** -- An array of strings describing what the agent can do. Each capability should be a short phrase. These help Claude Code understand the agent's strengths and help users know what to expect.

```yaml
capabilities:
  - "Analyze git diffs for code quality issues"
  - "Detect security vulnerabilities in changed code"
  - "Check adherence to project linting rules"
  - "Suggest refactoring opportunities"
```

**`model`** -- Override the LLM model for this agent. Options: `sonnet`, `haiku`, `opus`. Use `haiku` for fast, simple tasks. Use `sonnet` for balanced performance. Use `opus` for complex reasoning tasks.

```yaml
model: sonnet
```

**`maxTurns`** -- Maximum number of agentic loop iterations. Each "turn" is one cycle of the agent's think-act-observe loop. A code reviewer analyzing a 10-file PR might need 15-20 turns. A simple linter might need 5.

```yaml
maxTurns: 20
```

If omitted, the system default applies. Set this explicitly to prevent runaway agents.

**`effort`** -- Controls the model's reasoning depth. Options: `low`, `medium`, `high`. Higher effort means more careful analysis but slower execution.

```yaml
effort: high
```

#### Optional Fields

**`disallowedTools`** -- An array of tools the agent is forbidden from using. This is the opposite of skills' `allowed-tools`. Agents get all tools by default, and you remove the dangerous ones.

```yaml
disallowedTools:
  - "Write"
  - "Edit"
  - "Bash"
```

This example creates a read-only agent that can analyze code but cannot modify it.

Common denylist patterns:

| Pattern | Use Case |
|---------|----------|
| `["Write", "Edit"]` | Read-only analysis agent |
| `["Bash"]` | Agent that reads and writes files but cannot run commands |
| `["WebFetch", "WebSearch"]` | Agent restricted to local codebase |
| `["mcp__servername"]` | Deny access to a specific MCP server |

**`expertise_level`** -- How specialized the agent is. Options: `intermediate`, `advanced`, `expert`. This affects the agent's self-presentation and the depth of its analysis.

```yaml
expertise_level: expert
```

**`activation_priority`** -- How eagerly Claude Code should delegate to this agent. Options: `low`, `medium`, `high`, `critical`. A `critical` agent is invoked whenever its domain is detected. A `low` agent is only invoked when explicitly requested.

```yaml
activation_priority: medium
```

**`permissionMode`** -- Controls whether the agent asks for user permission before taking actions. Set to `default` for standard behavior.

```yaml
permissionMode: default
```

## Step 4: Write Agent Instructions

The body of the agent file is Markdown that defines the agent's personality, expertise, and operating procedures. This is where you shape how the agent thinks and acts.

### Structure Your Instructions

```markdown
# Agent Name

You are a [role description] specializing in [domain]. Your purpose
is to [primary objective].

## Your Expertise

Describe the agent's knowledge areas in detail. Be specific about
frameworks, tools, and methodologies the agent should know.

## Process

Define the agent's workflow as numbered steps:

1. Gather context (read relevant files, check git status)
2. Analyze (apply expertise to the gathered data)
3. Synthesize (draw conclusions, identify patterns)
4. Report (present findings in structured format)

## Output Format

Define exactly how the agent should present results.

## Constraints

- What the agent should NOT do
- Boundaries on scope
- When to stop and ask for help
```

### Writing Effective Agent Instructions

**Define the persona clearly.** The opening paragraph sets the agent's identity. "You are a senior security engineer specializing in application security" is better than "You help with security."

**Be prescriptive about the process.** Agents iterate autonomously, so they need clear steps to follow. Vague instructions lead to unfocused exploration.

**Specify the output format.** Without a defined format, agents produce inconsistent output across runs. Include a template:

```markdown
## Output Format

Present your review as:

### Summary
One paragraph overview of findings.

### Critical Issues
| File | Line | Issue | Recommendation |
|------|------|-------|----------------|
| ... | ... | ... | ... |

### Warnings
Bulleted list of non-critical concerns.

### Positive Patterns
Note any particularly well-written code worth highlighting.
```

**Set clear boundaries.** Tell the agent when to stop:

```markdown
## Constraints

- Review only files changed in the current branch (use git diff)
- Do not modify any files -- this is a read-only review
- If you encounter a file type you cannot analyze, skip it and note it
- Stop after reviewing all changed files; do not expand scope
- Maximum 3 iterations of re-reading a file for clarification
```

## Step 5: Full Working Example

Here is a complete, production-ready code review agent:

```yaml
---
name: code-reviewer
description: "Reviews code changes for quality, correctness, security, and adherence to project conventions"
capabilities:
  - "Static code analysis and pattern detection"
  - "Security vulnerability identification"
  - "Performance anti-pattern detection"
  - "Style and convention compliance checking"
  - "Test coverage gap analysis"
model: sonnet
effort: high
maxTurns: 20
disallowedTools:
  - "Write"
  - "Edit"
expertise_level: expert
activation_priority: medium
---

# Code Reviewer

You are a senior software engineer conducting a thorough code review.
Your purpose is to analyze code changes for correctness, security,
performance, and maintainability. You do not modify code -- you only
read and report.

## Your Expertise

- Language-specific best practices (TypeScript, Python, Go, Rust)
- OWASP security guidelines
- Performance optimization patterns
- Testing best practices and coverage analysis
- Clean code principles and design patterns

## Review Process

1. Run `git diff --name-only HEAD~1` to identify changed files
2. For each changed file:
   a. Read the full file to understand context
   b. Read the diff with `git diff HEAD~1 -- <file>`
   c. Analyze the changes against the criteria below
3. Check for test coverage of changed code
4. Check for documentation updates if public APIs changed
5. Compile findings into the output format

## Review Criteria

### Correctness
- Logic errors, off-by-one, null handling
- Type safety issues
- Race conditions in async code
- Missing error handling

### Security
- Input validation gaps
- SQL injection, XSS, CSRF exposure
- Hardcoded secrets or credentials
- Insecure dependency usage

### Performance
- N+1 query patterns
- Unnecessary re-renders (React)
- Missing memoization for expensive computations
- Large bundle impact from new imports

### Maintainability
- Function length (flag > 50 lines)
- Cyclomatic complexity
- Code duplication
- Naming clarity

## Output Format

### Code Review Summary

**Scope:** N files changed, M insertions, K deletions

**Verdict:** APPROVE / REQUEST CHANGES / NEEDS DISCUSSION

### Critical Issues
Issues that must be fixed before merging.

| # | File | Line | Category | Description |
|---|------|------|----------|-------------|

### Suggestions
Non-blocking improvements worth considering.

| # | File | Line | Category | Description |
|---|------|------|----------|-------------|

### Positive Notes
Well-written code worth highlighting.

## Constraints

- Review only files changed in the current branch
- Do not modify any files
- If a file is too large to analyze in one read (>1000 lines),
  focus on the changed sections
- Do not review generated files, lock files, or vendor directories
- Stop after all changed files are reviewed
```

## Step 6: Testing Your Agent

### Invoke the Agent

Install your plugin and invoke the agent:

```bash
# Install the plugin
claude /plugin add /path/to/my-plugin

# Ask Claude to use the agent
# Claude Code will delegate to the code-reviewer agent
"Review my recent code changes"
```

### Verify Behavior

Check these behaviors during testing:

1. **Tool restrictions work.** If you denied `Write` and `Edit`, verify the agent never modifies files.
2. **Iteration count is appropriate.** Watch the agent's turns. If it finishes in 3 turns but you set `maxTurns: 20`, consider lowering the limit. If it hits the limit and stops mid-work, raise it.
3. **Output format matches.** Verify the agent follows your specified output template.
4. **Scope stays bounded.** Verify the agent does not expand beyond the defined scope.

### Validation

Run the enterprise validator:

```bash
python3 scripts/validate-skills-schema.py --enterprise --verbose my-plugin/agents/code-reviewer.md
```

The validator checks:

- Required frontmatter fields are present
- `description` length is within 20-200 characters
- `capabilities` is a valid array if present
- No invalid frontmatter fields
- Body content has sufficient depth

## Common Patterns

### Read-Only Auditor

An agent that analyzes but never modifies:

```yaml
disallowedTools: ["Write", "Edit", "Bash"]
maxTurns: 15
effort: high
```

### Autonomous Fixer

An agent that finds issues and fixes them:

```yaml
# No disallowed tools -- full access
maxTurns: 25
effort: high
```

### Quick Scanner

A fast agent for lightweight checks:

```yaml
model: haiku
effort: low
maxTurns: 5
```

### Multi-Domain Expert

An agent covering several related areas:

```yaml
capabilities:
  - "Frontend performance optimization"
  - "Bundle size analysis"
  - "Core Web Vitals assessment"
  - "Image optimization recommendations"
  - "Font loading strategy review"
expertise_level: expert
maxTurns: 20
```

## Key Differences from Skills

Remember these critical differences when deciding between agents and skills:

| Aspect | Skill | Agent |
|--------|-------|-------|
| Tool control | Allowlist (`allowed-tools`) | Denylist (`disallowedTools`) |
| Autonomy | Single response | Multi-turn loop |
| Activation | Auto-triggers on context | Called as sub-agent |
| Iteration | No `maxTurns` | `maxTurns` controls loop |
| Effort | No effort control | `effort` sets reasoning depth |
| File location | `skills/name/SKILL.md` | `agents/name.md` |

## Next Steps

Once your agent is working:

1. Add it to a plugin alongside commands and skills (see [How to Build a Claude Code Plugin](/docs/guides/build-a-plugin))
2. Write clear documentation in your README about when and how to use the agent
3. Validate and [publish to the marketplace](/docs/guides/publish-to-marketplace)

Agents compose well with skills and commands. A plugin might have a `/security-scan` command that invokes the `security-scanner` agent, plus a `security-review` skill that auto-activates during code review to surface common vulnerabilities. Design your plugin's components to work together as a cohesive toolkit.
