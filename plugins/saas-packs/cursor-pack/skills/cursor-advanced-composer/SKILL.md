---
name: cursor-advanced-composer
description: 'Advanced Cursor Composer techniques: agent mode, parallel agents, complex
  refactoring, and multi-step

  orchestration. Triggers on "advanced composer", "composer patterns", "multi-file
  generation",

  "composer refactoring", "agent mode", "parallel agents".

  '
allowed-tools: Read, Write, Edit, Bash(cmd:*)
version: 1.19.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- cursor
- cursor-advanced
compatibility: Designed for Claude Code
---
# Cursor Advanced Composer

## Overview

Use Composer for bounded multi-file proposals when a human owner can inspect the plan, diff, tests, and rollback before applying changes.

## Prerequisites

- A defined task, affected-file boundary, repository rules, and a clean working tree or recoverable branch.
- Required test commands and a reviewer for changes that alter architecture, security, or data flow.

## Instructions

1. Ask Composer for a plan and affected-file list before applying any edits.
2. Constrain it to the approved scope and provide acceptance checks/non-goals.
3. Inspect each diff, run focused validation, and split or reject changes that exceed scope.
4. Commit only reviewed, test-backed changes; retain a revert path.

## Output

- A reviewed multi-file change proposal with affected files, validation results, and rollback reference.

## Error Handling

| Condition | Safe response |
|---|---|
| Composer proposes unrelated files | Reject or split the request; do not apply all. |
| Output conflicts with rules/tests | Treat project controls as authoritative and revise manually or with a narrower prompt. |
| Sensitive context is attached | Stop, remove it, and follow exposure handling. |

## Examples

Ask Composer to add a feature only in `src/feature/` and its existing tests, requiring a plan first. Apply no files until the plan and diff are reviewed; run the focused suite and revert the commit if acceptance fails.

Advanced patterns for Cursor Composer including agent orchestration, complex multi-file refactoring, architecture migrations, and quality-control workflows.

## Agent Mode Deep Dive

In Agent mode, Composer autonomously chains tool calls: reading files, searching the codebase, running terminal commands, and writing code. It operates in a loop until the task is complete or it hits the 25-tool-call limit.

### Agent Tool Capabilities

| Tool | What it does | Approval needed? |
|------|-------------|------------------|
| Read file | Reads any file in workspace | No |
| Search codebase | Semantic + text search | No |
| Write file | Creates or overwrites files | Shows diff first |
| Edit file | Modifies sections of files | Shows diff first |
| Run terminal command | Executes shell commands | Yes (click Allow) |
| List directory | Browses folder structure | No |

### Controlling Agent Behavior

Give the agent constraints in your prompt:

```
Migrate all React class components in src/components/ to functional
components with hooks.

Constraints:
- Do NOT modify test files
- Preserve all existing prop types
- Replace lifecycle methods with useEffect equivalents
- Keep the same file names and export structure
- Run `npm test` after each file to verify
```

### Checkpoint Pattern

For large refactors, use explicit checkpoints:

```
Phase 1: Create the new database schema types in src/types/schema-v2.ts.
         Show me the types before proceeding.

Phase 2: Update the repository layer to use the new types.
         Run tests after each repository file change.

Phase 3: Update the API routes to use the new repository methods.

Phase 4: Update the frontend components to match the new API response shapes.

Stop after each phase and show me a summary of changes.
```

The agent pauses after 25 tool calls automatically. Click "Continue" to allow more.

## Parallel Agent Workflows

Run up to 8 Composer agents simultaneously, each in its own tab.

### Use Case: Parallel Feature Development

```
# Agent 1 (Tab: "Auth")
Implement JWT authentication:
- src/middleware/auth.ts
- src/services/token.service.ts
- src/api/auth/login/route.ts
- src/api/auth/refresh/route.ts

# Agent 2 (Tab: "Products")
Implement product catalog:
- prisma/schema additions
- src/api/products/route.ts
- src/services/product.service.ts

# Agent 3 (Tab: "Tests")
Write integration tests for the existing user API:
- tests/integration/users.test.ts
```

Each agent has its own context and conversation history. They can modify the same codebase simultaneously, but be careful with overlapping files.

### Conflict Resolution Between Agents

If two agents modify the same file, the second write overwrites the first. Mitigate this by:

- Assigning non-overlapping file scopes to each agent
- Running agents sequentially for shared files
- Using git to cherry-pick the best changes

## Complex Refactoring Patterns

### Pattern: Extract and Replace

Extract a pattern into a shared utility, then replace all occurrences:

```
@src/api/

I see repeated error handling in every API route:
try { ... } catch (err) { if (err instanceof ZodError) ... }

Step 1: Create src/utils/api-handler.ts with a withValidation()
wrapper that handles the try/catch + Zod pattern.

Step 2: Update ALL route files in src/api/ to use withValidation()
instead of manual try/catch.

Show me api-handler.ts first, then refactor the routes.
```

### Pattern: Interface-First Migration

Define the target interface, then migrate implementations:

```
@src/services/

Step 1: Create src/interfaces/repository.ts with a generic
Repository<T> interface:
  - findById(id: string): Promise<T | null>
  - findMany(filter: Filter<T>): Promise<T[]>
  - create(data: CreateInput<T>): Promise<T>
  - update(id: string, data: UpdateInput<T>): Promise<T>
  - delete(id: string): Promise<void>

Step 2: Refactor UserService to implement Repository<User>.
Step 3: Refactor ProductService to implement Repository<Product>.
Step 4: Update API routes to use the Repository interface type.
```

### Pattern: Test-Driven Refactoring

Write tests first, then refactor with confidence:

```
@src/services/payment.service.ts

Step 1: Write comprehensive tests for the current PaymentService
behavior. Cover all public methods and edge cases.
Run `npm test` to verify they pass.

Step 2: Refactor PaymentService to use the Strategy pattern for
different payment providers (Stripe, PayPal, manual).
Run `npm test` after each change to ensure nothing breaks.
```

## Multi-Codebase Orchestration

For monorepos or multi-root workspaces:

```
@packages/shared/src/types/
@packages/api/src/routes/
@packages/web/src/hooks/

Add a "notifications" feature across all packages:
1. shared: NotificationType enum, Notification interface
2. api: GET /notifications, POST /notifications/mark-read endpoints
3. web: useNotifications hook, NotificationBell component

Use the shared types in both api and web packages.
Import from @myorg/shared (the workspace alias).
```

## Quality Control Workflows

### Pre-Apply Review Checklist

Before clicking "Apply All":

1. **Read every diff** -- do not blindly apply multi-file changes
2. **Check imports** -- Composer sometimes generates wrong import paths
3. **Verify types** -- ensure type annotations are correct, not `any`
4. **Look for hallucinations** -- methods or modules that do not exist
5. **Run build** -- `Cmd+`` > run your build command after applying

### Post-Apply Validation

```
# In Composer or terminal:
npm run build       # Catches import errors, type mismatches
npm run lint        # Catches style violations
npm run test        # Catches behavior regressions
```

### Rollback Strategy

If applied changes break the build:

```bash
# Undo all uncommitted changes
git checkout .

# Or selectively undo specific files
git checkout -- src/api/products/route.ts
```

Always commit working code before starting a Composer session.

## Advanced Prompting Techniques

### System-Level Instructions via Rules

Create a Composer-specific rule:

```yaml
# .cursor/rules/composer-standards.mdc
---
description: "Standards for Composer-generated code"
globs: ""
alwaysApply: true
---
When generating code via Composer:
- Always include JSDoc comments on exported functions
- Always add error handling (never let functions throw unhandled)
- Generate corresponding test files for new modules
- Use named exports, never default exports
- Import types with `import type` syntax
```

### Iterative Refinement

After first pass:

```
The generated product.service.ts looks good but:
1. Add pagination support to findMany (page, limit params)
2. Add a findByCategory method
3. Use transactions for createWithItems
```

Composer retains conversation context, so follow-up instructions build on previous output.

## Enterprise Considerations

- **Compliance**: Review generated code for license compliance before committing
- **Security**: Composer may generate code with SQL injection or XSS vulnerabilities -- always audit
- **Cost**: Agent mode with reasoning models (o1, Opus) can consume thousands of tokens per session
- **Audit trail**: Commit Composer output with descriptive messages for code review traceability

## Resources

- [Composer Overview](https://docs.cursor.com/composer/overview)
- [Agent Mode Documentation](https://docs.cursor.com/agent)
- [Cursor 2.0 Agent Architecture](https://cursor.com/blog)
