---
name: clade-reference-architecture
description: "Build Claude Code plugins \u2014 skills, agents, MCP servers, hooks,\
  \ and slash commands.\nUse when working with reference-architecture patterns.\n\
  The complete guide to extending Claude Code with the Anthropic plugin system.\n\
  Trigger with \"claude code plugin\", \"build a skill\", \"create mcp server\",\n\
  \"anthropic plugin architecture\", \"claude code hooks\".\n"
allowed-tools: Read, Write, Edit, Bash(npm:*)
version: 1.1.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- anthropic
- claude-code
- plugins
- skills
- mcp
compatibility: Designed for Claude Code
---
# Claude Code Plugin Architecture

## Overview

Claude Code has a plugin system with 4 extension points: **skills** (auto-activating knowledge), **commands** (slash commands), **agents** (specialized sub-agents), and **MCP servers** (tool providers). This skill covers building all four.

## Prerequisites

- A supported Claude Code environment and an isolated plugin workspace
- A declared ownership boundary for filesystem, network, and credential access
- Validation tooling for manifests, skill metadata, commands, agents, and MCP
- A rollback plan that can disable a plugin without deleting user state

## Instructions

Start with the smallest extension point that meets the requirement, declare
only the tools and permissions it needs, and validate it locally before adding
it to a marketplace or shared environment. Test discovery, activation, failure,
and rollback paths; do not expose secrets through examples, environment files,
logs, or MCP response payloads.

## Plugin Structure

```
my-plugin/
├── .claude-plugin/
│   └── plugin.json          # Required: name, version, description, author
├── skills/
│   └── my-skill/
│       └── SKILL.md          # Auto-activating skill
├── commands/
│   └── my-command.md         # Slash command (/my-command)
├── agents/
│   └── my-agent.md           # Custom agent
└── README.md
```

## Building a Skill (SKILL.md)

```yaml
---
name: my-skill
description: |
  When to activate this skill. Include trigger phrases so Claude
  knows when to use it. Be specific about the problem it solves.
allowed-tools: Read, Write, Edit, Bash(npm:*)
version: 1.0.0
author: Your Name <you@example.com>
license: MIT
compatible-with: claude-code
tags: [category, topic]
---

# Skill Title

## Overview
What this skill does and when to use it.

## Prerequisites
- Claude Code installed
- Understanding of Markdown and YAML frontmatter
- For MCP servers: Node.js 18+ and `@modelcontextprotocol/sdk`

## Instructions
Step-by-step instructions Claude follows when this skill activates.

### Step 1: Do the thing
Explain what to do with code examples.

## Output
What the user should expect when this skill runs.

## Error Handling
| Error | Cause | Solution |
|-------|-------|----------|
| ... | ... | ... |
```

## Building a Slash Command

```yaml
---
name: my-command
description: "Run my custom workflow"
user-invocable: true
argument-hint: "<file-path>"
allowed-tools: Read, Write, Edit, Bash(npm:*)
version: 1.0.0
---

# /my-command

When the user runs `/my-command <file-path>`, do the following:

1. Read the file at $ARGUMENTS
2. Analyze it for issues
3. Report findings
```

## Building an Agent

```yaml
---
name: my-agent
description: "Specialized agent for code review"
capabilities: ["code-review", "security-audit"]
model: sonnet
maxTurns: 10
---

# Code Review Agent

You are a code review specialist. When invoked:
1. Read the files provided
2. Check for security issues, code quality, and performance
3. Report findings with specific line references
```

## Building an MCP Server

```typescript
// src/index.ts
#!/usr/bin/env node
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';

const server = new Server({ name: 'my-tools', version: '1.0.0' }, {
  capabilities: { tools: {} },
});

server.setRequestHandler('tools/list', async () => ({
  tools: [{
    name: 'search_docs',
    description: 'Search documentation for a query',
    inputSchema: {
      type: 'object',
      properties: { query: { type: 'string' } },
      required: ['query'],
    },
  }],
}));

server.setRequestHandler('tools/call', async (request) => {
  if (request.params.name === 'search_docs') {
    const results = await searchDocs(request.params.arguments.query);
    return { content: [{ type: 'text', text: JSON.stringify(results) }] };
  }
});

const transport = new StdioServerTransport();
await server.connect(transport);
```

## Hooks

```json
// .claude/settings.json
{
  "hooks": {
    "pre-tool-call": [{
      "matcher": "Edit",
      "command": "echo 'About to edit a file'"
    }],
    "post-tool-call": [{
      "matcher": "Bash",
      "command": "echo 'Bash command completed'"
    }]
  }
}
```

## Path Variables

| Variable | Context | Resolves To |
|----------|---------|-------------|
| `${CLAUDE_SKILL_DIR}` | Skills (bash/DCI) | Skill's directory |
| `${CLAUDE_PLUGIN_ROOT}` | Hooks | Plugin root directory |
| `${CLAUDE_PLUGIN_DATA}` | Persistent state | Survives updates |
| `$ARGUMENTS` | Commands | User-provided args |

## Error Handling

| Condition | Response |
|---|---|
| Manifest or metadata validation fails | Stop installation, correct the declared contract, and rerun validation. |
| Plugin requests unapproved capability | Remove or narrowly justify the capability before release. |
| MCP server fails or returns malformed data | Fail closed, redact diagnostic output, and preserve a correlation ID. |
| Upgrade changes plugin behavior | Disable or pin the new version and restore the last tested release. |

## Output

Produce a plugin architecture record identifying the chosen extension point,
manifest version, declared tools/permissions, test evidence, release owner,
and rollback procedure. Treat a rendered example as illustrative only; the
validated manifest and runtime behavior are the operative contract.

## Examples

See Building a Skill (SKILL.md), Building a Slash Command, Building an Agent, Building an MCP Server, and Hooks configuration examples above.

## Resources

- [Plugin Docs](https://code.claude.com/docs/en/plugins)
- [SKILL.md Spec](https://code.claude.com/docs/en/skills)
- [MCP Protocol](https://modelcontextprotocol.io)

## Next Steps

See `clade-multi-env-setup` for managing plugins across environments.
