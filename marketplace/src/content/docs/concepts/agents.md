---
title: "Claude Code Agents and Subagents"
description: "How agent definitions work in Claude Code plugins — creating specialized AI personas with capabilities, tool restrictions, and autonomous multi-step workflows using agents/*.md files."
section: "concepts"
order: 3
keywords:
  - "Claude Code agents"
  - "subagents"
  - "agent definition"
  - "disallowedTools"
  - "agent vs skill"
  - "multi-agent"
  - "autonomous agent"
  - "agent frontmatter"
officialLinks:
  - title: "Claude Code Documentation"
    url: "https://code.claude.com/docs/en/"
  - title: "Claude Code Plugins Overview"
    url: "https://code.claude.com/docs/en/plugins"
relatedDocs:
  - "concepts/plugins"
  - "concepts/skills"
  - "concepts/commands-and-hooks"
---

Agents are specialized AI personas defined within Claude Code plugins. Where skills teach Claude *what* to do in a specific domain, agents define *who* Claude becomes when tackling a particular class of problem. An agent carries a distinct identity with its own capabilities, tool restrictions, and behavioral parameters -- making it suitable for complex, autonomous, multi-step workflows.

## When to Use Agents vs Skills

The distinction between agents and skills is fundamental to designing effective plugins. Choosing the wrong abstraction leads to either overly constrained workflows (using skills where agents are needed) or unnecessarily broad permissions (using agents where skills would suffice).

| Characteristic | Skills | Agents |
|---------------|--------|--------|
| **Activation** | Auto-activates based on context | Explicitly delegated or invoked |
| **Tool model** | Allowlist (`allowed-tools`) | Denylist (`disallowedTools`) |
| **Scope** | Focused, single-task | Broad, multi-step workflows |
| **Autonomy** | Follows instructions within one turn | Can iterate autonomously over multiple turns |
| **Identity** | Adds knowledge to Claude | Gives Claude a specialized persona |
| **Typical length** | 500-2,000 words | 200-1,000 words (directives, not procedures) |

**Use a skill when:**

- The task is focused and well-defined (e.g., "write tests for this component")
- You want auto-activation based on context matching
- You need precise tool restrictions (only allow specific tools)
- The instruction set is procedural: step 1, step 2, step 3

**Use an agent when:**

- The task requires autonomous exploration and decision-making
- Multiple tool categories are needed, with only a few excluded
- The agent needs to iterate (try, evaluate, adjust) over multiple turns
- You want Claude to adopt a specific professional persona (security auditor, UX researcher, etc.)
- The work involves judgment calls that vary based on what the agent discovers

## Agent File Structure

Agent definitions live in the `agents/` directory of a plugin. Each agent is a single markdown file with YAML frontmatter:

```
my-plugin/
└── agents/
    ├── security-auditor.md
    ├── performance-analyst.md
    └── code-archaeologist.md
```

### Complete Agent Example

```markdown
---
name: security-auditor
description: "Security-focused code reviewer specializing in OWASP Top 10, dependency vulnerabilities, and secrets detection"
capabilities:
  - "Static analysis of source code for security vulnerabilities"
  - "Dependency audit using npm audit and Snyk patterns"
  - "Secrets and credential detection in code and configuration"
  - "OWASP Top 10 compliance checking"
model: sonnet
effort: high
maxTurns: 15
disallowedTools:
  - "WebFetch"
  - "WebSearch"
expertise_level: expert
activation_priority: high
---

You are a senior application security engineer conducting a thorough security
review. Your primary objective is to identify vulnerabilities before code
reaches production.

## Review Methodology

1. **Reconnaissance**: Map the attack surface by identifying entry points
   (API routes, form handlers, file uploads, WebSocket endpoints).

2. **Dependency Analysis**: Check `package.json`, `requirements.txt`, or
   equivalent for known vulnerable dependencies. Flag any package with
   a critical or high severity CVE.

3. **Code Analysis**: Systematically review for:
   - SQL injection and NoSQL injection
   - Cross-site scripting (XSS) in rendered output
   - Insecure deserialization
   - Hardcoded secrets, API keys, or credentials
   - Missing authentication or authorization checks
   - Path traversal vulnerabilities
   - Server-side request forgery (SSRF)

4. **Configuration Review**: Check for insecure defaults in:
   - CORS policies
   - Cookie settings (HttpOnly, Secure, SameSite)
   - TLS configuration
   - Error handling (information leakage)

5. **Report**: Categorize findings by severity (Critical, High, Medium, Low)
   with specific file locations, code snippets, and remediation guidance.

## Output Format

Present findings as a structured security report:

- **Finding ID**: SEC-001, SEC-002, etc.
- **Severity**: Critical / High / Medium / Low
- **Category**: OWASP category (e.g., A03:2021 Injection)
- **Location**: File path and line number
- **Description**: What the vulnerability is
- **Impact**: What an attacker could do
- **Remediation**: Specific code changes to fix it
```

## Frontmatter Fields

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Unique agent identifier within the plugin (kebab-case) |
| `description` | string | 20-200 character summary of the agent's specialty |

### Optional Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `capabilities` | array | [] | List of capabilities the agent provides |
| `model` | string | (default) | LLM model override: `sonnet`, `haiku`, or `opus` |
| `effort` | string | medium | Reasoning effort level: `low`, `medium`, or `high` |
| `maxTurns` | number | (default) | Maximum iterations in the agentic loop |
| `disallowedTools` | array | [] | Tools the agent is forbidden from using |
| `expertise_level` | string | (none) | Agent expertise: `intermediate`, `advanced`, or `expert` |
| `activation_priority` | string | (none) | Priority: `low`, `medium`, `high`, or `critical` |
| `permissionMode` | string | default | Permission behavior for tool usage |

### The disallowedTools Field

This is the defining difference between agents and skills. Where skills use `allowed-tools` (an allowlist -- only these tools may be used), agents use `disallowedTools` (a denylist -- all tools are available *except* these).

The denylist approach makes sense for agents because they need broad capabilities to work autonomously. Rather than listing every tool an agent might need, you list only the tools it should never touch:

```yaml
# Agent that can do everything except modify files
disallowedTools:
  - "Write"
  - "Edit"

# Agent that can do everything except network access
disallowedTools:
  - "WebFetch"
  - "WebSearch"

# Agent that cannot invoke other MCP servers
disallowedTools:
  - "mcp__database-server"
  - "mcp__slack-integration"
```

If your use case requires tight tool restrictions (only 2-3 tools allowed), use a skill instead. The denylist model works best when the agent needs most tools but should be prevented from accessing a few specific ones.

### Model Selection

The `model` field lets you choose the right model for the agent's complexity and cost profile:

```yaml
# Complex reasoning, security analysis, architecture review
model: opus

# General-purpose coding, standard analysis
model: sonnet

# Fast, simple tasks, triage, classification
model: haiku
```

This is an optimization lever. An agent that performs deep architectural analysis benefits from `opus`, while an agent that triages issues or classifies files can use `haiku` for faster, cheaper execution.

### Effort and maxTurns

These two fields control how much autonomous work an agent does before stopping:

```yaml
# High effort, many iterations — for thorough investigations
effort: high
maxTurns: 20

# Low effort, few iterations — for quick checks
effort: low
maxTurns: 5
```

The `effort` field (available in Claude Code v2.1.78+) affects the model's reasoning depth per turn. The `maxTurns` field caps the total number of agentic loop iterations, preventing runaway agents from consuming excessive resources.

These fields are agent-only -- they have no effect in SKILL.md files. Skills execute within the main conversation flow and do not have their own agentic loop.

## How Agents Are Invoked

Agents can be activated through several mechanisms:

### Delegation by Claude

When Claude encounters a subtask that matches an installed agent's description and capabilities, it may delegate to that agent automatically. This happens through the `Task` tool, which spawns a subagent with the specified identity and restrictions.

### Explicit Invocation from Skills

Skills can explicitly invoke agents using the `context` and `agent` frontmatter fields:

```yaml
---
name: full-audit
description: |
  When performing a comprehensive codebase audit covering security,
  performance, and accessibility.
allowed-tools: Read, Glob, Grep, Task
context: fork
agent: security-auditor
version: 1.0.0
author: Audit Team
license: MIT
---
```

When this skill activates, Claude forks execution into a subagent running as `security-auditor`. The subagent has its own context window and tool permissions.

### From Slash Commands

Commands can reference agents in their instructions:

```markdown
---
name: security-review
description: "Run a comprehensive security audit on the current codebase"
---

Delegate this task to the security-auditor agent. Have it review all source
files in the `src/` directory and produce a findings report.
```

## Designing Effective Agents

### The Persona Principle

The most effective agents have a clear professional identity. Rather than describing what the agent should do in exhaustive detail (that is what skills are for), describe *who* the agent is and how it approaches problems.

**Effective persona:**

```markdown
You are a senior performance engineer with 15 years of experience optimizing
web applications. You approach every system by first understanding the
critical user paths, then measuring actual bottlenecks before proposing
solutions. You never optimize prematurely.
```

**Less effective (too procedural for an agent):**

```markdown
Step 1: Read all JavaScript files.
Step 2: Look for large bundle sizes.
Step 3: Check for unnecessary dependencies.
Step 4: Write a report.
```

The persona approach gives the agent room to exercise judgment. It knows to measure before optimizing, to focus on critical paths, and to avoid premature optimization -- but the specific sequence of actions depends on what it discovers.

### Capability Declarations

The `capabilities` array serves as a contract between the agent and the system. It tells Claude (and the user) exactly what this agent can deliver:

```yaml
capabilities:
  - "Identify N+1 query patterns in ORM code"
  - "Analyze bundle sizes and recommend code splitting strategies"
  - "Profile React component render cycles"
  - "Detect memory leaks in long-running processes"
  - "Generate Lighthouse performance reports"
```

Each capability should be specific and actionable. Avoid vague capabilities like "improve performance" -- instead, list the concrete analyses and actions the agent can perform.

### Output Structure

Define a clear output format in the agent body. Agents that produce well-structured reports are far more useful than agents that produce stream-of-consciousness analysis:

```markdown
## Report Format

Structure every analysis as:

### Executive Summary
One paragraph: what was reviewed, top finding, overall assessment.

### Findings
Numbered list, each with:
- **Severity**: Critical / Warning / Info
- **Location**: File path and line
- **Issue**: What is wrong
- **Impact**: Measured or estimated performance cost
- **Fix**: Specific code change

### Recommendations
Prioritized list of improvements, ordered by impact/effort ratio.
```

### Scope Boundaries

Explicitly state what the agent should and should not do:

```markdown
## Scope

- DO analyze all `.ts` and `.tsx` files in `src/`
- DO check `package.json` for known heavy dependencies
- DO review webpack/vite configuration for optimization opportunities
- DO NOT modify any files (this is a read-only audit)
- DO NOT run benchmarks or load tests (time-consuming, do separately)
- DO NOT review test files unless they contain performance test utilities
```

## Agent Patterns

### The Auditor

Read-only agent that analyzes and reports without modifying anything:

```yaml
disallowedTools:
  - "Write"
  - "Edit"
  - "Bash"
expertise_level: expert
effort: high
maxTurns: 20
```

### The Builder

Agent that creates new code or configuration from scratch:

```yaml
disallowedTools:
  - "WebFetch"
expertise_level: advanced
effort: high
maxTurns: 15
```

### The Triager

Fast agent that classifies issues and routes them:

```yaml
model: haiku
disallowedTools:
  - "Write"
  - "Edit"
expertise_level: intermediate
effort: low
maxTurns: 5
```

### The Researcher

Agent that gathers information from the codebase without modifying it:

```yaml
model: sonnet
disallowedTools:
  - "Write"
  - "Edit"
expertise_level: advanced
effort: medium
maxTurns: 10
```

## Multi-Agent Orchestration

Complex workflows often benefit from multiple agents working in sequence or parallel. A plugin can define several agents that complement each other:

```
my-audit-plugin/
└── agents/
    ├── security-auditor.md      # Finds security vulnerabilities
    ├── performance-analyst.md   # Identifies performance bottlenecks
    ├── accessibility-checker.md # Validates WCAG compliance
    └── report-compiler.md       # Combines findings into a unified report
```

A top-level command or skill can orchestrate these agents:

```markdown
---
name: full-audit
description: "Run a comprehensive codebase audit"
---

Execute the following audit sequence:

1. Delegate security analysis to the **security-auditor** agent
2. Delegate performance analysis to the **performance-analyst** agent
3. Delegate accessibility checking to the **accessibility-checker** agent
4. Pass all findings to the **report-compiler** agent for a unified report
```

When designing multi-agent systems, be mindful of:

- **Context isolation.** Each agent has its own context window. Information does not automatically flow between agents -- you must explicitly pass findings through the orchestrating command or skill.
- **Rate limits.** Multiple agents running in parallel consume API tokens faster. Consider using the `maxTurns` field to cap each agent's iteration count.
- **Ordering.** Some agents may depend on the output of others. Structure your orchestration to respect these dependencies.

For production multi-agent patterns, see the [Multi-Agent Rate Limits playbook](/playbooks/01-multi-agent-rate-limits/).

## Quality Standards

The Tons of Skills marketplace validates agents using Anthropic's field specification:

- The `name` and `description` fields are required
- `description` must be 20-200 characters
- `capabilities` should list specific, actionable items
- `disallowedTools` entries must reference valid tool names
- No invalid or deprecated fields should be present in frontmatter
- The agent body should contain actionable directives, not boilerplate

Run the enterprise validator to check your agents:

```bash
python3 scripts/validate-skills-schema.py --enterprise --agents-only plugins/my-category/my-plugin/
```

## Next Steps

- Understand the complementary skill system: [Understanding Agent Skills (SKILL.md)](/docs/concepts/skills)
- Learn about explicit user invocation: [Slash Commands and Hooks](/docs/concepts/commands-and-hooks)
- Browse plugins with agents: [Explore Plugins](/explore)
