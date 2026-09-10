---
name: windsurf-sdk-patterns
description: 'Analyze and apply production-ready Devin Desktop (formerly Windsurf) workspace configuration and Cascade
  interaction patterns.

  Use when configuring .devin/rules/project.md, workspace rules, MCP servers,

  or establishing team coding standards for Windsurf AI.

  Trigger with phrases like "windsurf patterns", "windsurf best practices",

  "windsurf config patterns", "windsurfrules", "windsurf workspace".

  '
allowed-tools: Read, Write, Edit, Grep
argument-hint: "[scope or requirements]"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- windsurf
- configuration
- rules
- mcp
compatibility: Designed for Claude Code
---
# Windsurf Configuration Patterns

## Overview

Production-ready configuration patterns for Windsurf IDE: rules files, workspace rules with trigger modes, MCP server integration, and Cascade prompt engineering.

## Prerequisites

- Windsurf authenticated and operational
- Understanding of Cascade Code and Chat modes
- Project with established coding conventions

## Tool Use

- Use `Read` to inspect only the repository files and configuration needed for the request.
- Use `Grep` to locate relevant settings, rules, logs, or code without broad collection.
- Use `Write` only for a new artifact the user requested; never write credentials or unreviewed production configuration.
- Use `Edit` for bounded, reviewable changes and preserve unrelated user work.

## Instructions

### Step 1: Root-Level .devin/rules/project.md (Permanent Context)

The `.devin/rules/project.md` file is the single highest-impact configuration for Cascade output quality. It provides persistent context every session.

```markdown
<!-- .devin/rules/project.md -->

# Project: payments-api

## Stack
- Runtime: Node.js 20 LTS
- Language: TypeScript 5.x (strict, noUncheckedIndexedAccess)
- Framework: Fastify v4
- ORM: Drizzle (PostgreSQL)
- Validation: zod
- Testing: Vitest
- Linting: Biome

## Architecture Rules
- Route handlers in src/routes/ — no business logic
- Business logic in src/services/ — never throw, use Result<T,E>
- Database queries in src/repositories/ — Drizzle only
- Shared types in src/types/ — all exported with JSDoc

## Don't
- Don't use `any` type
- Don't use default exports
- Don't use class-based patterns (use functions + closures)
- Don't modify files in migrations/ without explicit request
- Don't use deprecated APIs: my_old_helper, legacyAuth

## Testing
- Unit tests for every service method
- Integration tests for every route handler
- No mocking repositories in integration tests
- Use test fixtures from tests/fixtures/
```

**Limits:** 6,000 characters per rules file. 12,000 total (global + workspace combined).

### Step 2: Workspace Rules with Trigger Modes

Create granular rules in `.devin/rules/` with YAML frontmatter:

```markdown
<!-- .devin/rules/testing.md -->
---
trigger: glob
globs: **/*.test.ts, **/*.spec.ts
---
All test files must:
- Use describe/it blocks (not test())
- Mock external API calls with msw
- Assert both success and error paths
- Include at least one snapshot test for UI components
- Use factory functions from tests/fixtures/ for test data
```

```markdown
<!-- .devin/rules/api-routes.md -->
---
trigger: glob
globs: src/routes/**/*.ts
---
API route handlers must:
- Validate input with zod schema before processing
- Return consistent error format: { error: string, code: string, statusCode: number }
- Include request ID in all log lines
- Never call database directly — use repository layer
```

```markdown
<!-- .devin/rules/security.md -->
---
trigger: model_decision
description: Apply when code touches authentication, authorization, or secrets
---
Security requirements:
- Never log secrets, tokens, or PII
- Use parameterized queries (never string interpolation for SQL)
- Validate JWT tokens with jose library
- Rate limit all public endpoints
- CORS: explicit origin whitelist, never wildcard in production
```

```markdown
<!-- .devin/rules/migrations.md -->
---
trigger: manual
---
Database migration rules (activate with @migrations):
- Always create reversible migrations (up + down)
- Never drop columns in production — deprecate first
- Add indexes for any new foreign key columns
- Test migration on a copy of production data first
```

### Step 3: MCP Server Configuration

Connect external tools to Cascade via Model Context Protocol:

```json
// ~/.codeium/windsurf/mcp_config.json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
      }
    },
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "DATABASE_URL": "${DATABASE_URL}"
      }
    },
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    }
  }
}
```

Enable in Windsurf Settings > Cascade > Model Context Protocol (MCP).

**Tool limit:** Cascade supports max 100 MCP tools total across all servers. Disable unused tools in each MCP's settings page.

### Step 4: Effective Cascade Prompt Patterns

```
GOOD prompts (specific, scoped):
"In src/services/payment.ts, add a refundPayment method that calls
Stripe's refund API. Handle partial refunds. Return Result<Refund, PaymentError>."

"@src/routes/users.ts Add input validation using the UserCreateSchema
from src/types/user.ts. Return 400 with field-level errors."

BAD prompts (vague, unscoped):
"Add validation to the API"
"Refactor the codebase"
"Make it better"
```

## Output

Create a minimal customization set using the correct mechanism—Rule, `AGENTS.md`, Workflow, Skill, Hook, or MCP configuration—with activation behavior, ownership, secret handling, and a verification example. Avoid undocumented settings keys.

## Error Handling

| Issue | Cause | Solution |
|-------|-------|----------|
| Rules ignored by Cascade | File over 6,000 chars | Trim to essentials, split into workspace rules |
| Workspace rules not loading | Wrong directory or invalid frontmatter | Use `.devin/rules/*.md` and validate the `trigger:` mode |
| MCP server not connecting | Command not found | Ensure npx can resolve the package |
| Too many MCP tools | Over 100 tool limit | Disable unused tools per MCP server |
| Glob trigger not firing | Wrong pattern syntax | Use gitignore-style globs: `**/*.test.ts` |

## Examples

### Global Rules (Apply to All Projects)

```markdown
<!-- ~/.codeium/windsurf/memories/global_rules.md (6,000 char limit) -->
- Always use English for code comments and commit messages
- Prefer functional programming patterns over OOP
- Write self-documenting code; add comments only for "why", not "what"
- When suggesting terminal commands, explain what they do
- Never suggest installing global npm packages
```

### Project Health Check

```bash
# Verify Windsurf config exists
ls -la .devin/rules/project.md .codeiumignore .devin/rules/ 2>/dev/null
```

## Resources

- [Focused first-party references](references/official-docs.md)
- [Windsurf Rules Directory](https://windsurf.com/editor/directory)
- [Cascade Memories](https://docs.devin.ai/desktop/cascade/memories)
- [MCP Integration](https://docs.devin.ai/desktop/cascade/mcp)

## Related Skill

Continue with `windsurf-core-workflow-a` to apply these configuration patterns in a bounded Cascade session with explicit validation and rollback checkpoints.
