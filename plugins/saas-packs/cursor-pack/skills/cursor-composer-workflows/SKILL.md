---
name: cursor-composer-workflows
description: 'Master Cursor Composer for multi-file AI editing, scaffolding, and refactoring.
  Triggers on "cursor composer",

  "multi-file edit", "cursor generate files", "composer workflow", "cursor scaffold",
  "Cmd+I".

  '
allowed-tools: Read, Write, Edit, Bash(cmd:*)
version: 1.19.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- cursor
- workflow
compatibility: Designed for Claude Code
---
# Cursor Composer Workflows

## Overview

Structure Composer work around explicit planning, small reviewed diffs, test evidence, and rollback rather than unattended multi-file generation.

## Prerequisites

- A bounded issue, affected-file inventory, repository rules, and test commands.
- A recoverable branch and reviewer for material architectural, security, or data changes.

## Instructions

1. Request a plan and non-goals before any edits.
2. Apply one coherent slice at a time, review the diff, and run its focused checks.
3. Keep human decisions for API, security, migration, and dependency changes.
4. Commit validated slices and revert/split failures rather than accepting a broad repair.

## Output

- A sequence of small reviewed Composer-assisted changes with validation and rollback evidence.

## Error Handling

| Condition | Safe response |
|---|---|
| Plan exceeds scope | Revise the request and reduce affected files. |
| Diff fails test or policy | Reject/revert the slice and diagnose within the stated boundary. |
| Composer needs sensitive context | Do not attach it; use sanitized interfaces or approved process. |

## Examples

Ask Composer to plan a module-local refactor, accept only the first reviewed slice, run its focused test, and commit it. Stop if it proposes a dependency, migration, or unrelated repository change.

Master Cursor Composer (Cmd+I / Ctrl+I) for multi-file code generation, scaffolding, and coordinated refactoring. Composer is the primary tool for changes that span multiple files.

## Composer Interface

```
┌─────────────────────────────────────────────────────────┐
│  Composer                                    [Model ▾]  │
│─────────────────────────────────────────────────────────│
│  Context: [src/api/] [prisma/schema.prisma]             │
│─────────────────────────────────────────────────────────│
│  Create a CRUD API for products with:                   │
│  - Prisma model with id, name, price, category          │
│  - API routes (GET list, GET by id, POST, PUT, DELETE)  │
│  - Zod validation schemas                               │
│  - Unit tests with vitest                               │
│─────────────────────────────────────────────────────────│
│  ┌─ Changes ──────────────────────────────────────────┐ │
│  │  ✅ prisma/schema.prisma          (+12 lines)      │ │
│  │  ✅ src/api/products/route.ts     (new file)       │ │
│  │  ✅ src/api/products/[id]/route.ts (new file)      │ │
│  │  ✅ src/schemas/product.ts        (new file)       │ │
│  │  ✅ tests/api/products.test.ts    (new file)       │ │
│  └────────────────────────────────────────────────────┘ │
│  [Apply All]  [Review Changes]  [Reject]                │
└─────────────────────────────────────────────────────────┘
```

## Core Workflow Patterns

### 1. Feature Scaffolding

Generate a complete feature across multiple files:

```
@src/api/users/route.ts @prisma/schema.prisma

Create a complete "orders" feature following the same patterns as users:
1. Prisma model: Order (id, userId, items, total, status, createdAt)
2. OrderItem model: (id, orderId, productId, quantity, price)
3. API routes: GET /api/orders, GET /api/orders/[id], POST /api/orders
4. Zod validation schemas matching the Prisma models
5. Service layer with createOrder, getOrders, getOrderById
```

Composer reads the referenced files to replicate the existing pattern.

### 2. Cross-File Refactoring

Rename, restructure, or migrate patterns across the codebase:

```
@src/services/ @src/api/

Refactor all service functions to use a Result type instead of throwing errors.

Current pattern:
  async function getUser(id: string): Promise<User> { throw new NotFoundError(); }

Target pattern:
  async function getUser(id: string): Promise<Result<User, NotFoundError>> { ... }

Update all callers in the API routes to handle the Result type.
```

### 3. Test Generation

Generate tests that match existing test patterns:

```
@tests/api/users.test.ts @src/api/products/route.ts

Generate vitest tests for the products API following the same patterns
as users.test.ts. Cover:
- GET /api/products returns list with pagination
- GET /api/products/[id] returns 404 for missing product
- POST /api/products validates required fields
- POST /api/products returns 201 with created product
Use the same mock setup and assertion patterns.
```

### 4. Migration / Upgrade

Apply systematic changes across many files:

```
@src/components/

Migrate all components from CSS Modules to Tailwind CSS:
- Replace className={styles.container} with className="..."
- Map existing CSS properties to Tailwind utilities
- Remove the .module.css import and file
- Preserve responsive breakpoints and dark mode support
```

## Agent Mode

Composer can operate in Agent mode, which autonomously executes multi-step tasks:

- Reads and searches files without explicit @-mentions
- Runs terminal commands (with your approval)
- Chains multiple tool calls (up to 25 before pausing)
- Makes decisions about which files to modify

Agent mode activates by default in Cursor 2.0. It is best for open-ended tasks where you describe the goal but not every step.

### Parallel Agents

Run up to 8 agents simultaneously, each in its own Composer tab. Useful for:

- Working on unrelated features in parallel
- Exploring different implementation approaches
- Running tests in one agent while coding in another

## Diff Review and Application

Before applying changes, Composer shows a complete diff for each file:

```diff
// prisma/schema.prisma
+ model Order {
+   id        String      @id @default(cuid())
+   userId    String
+   user      User        @relation(fields: [userId], references: [id])
+   items     OrderItem[]
+   total     Int
+   status    OrderStatus @default(PENDING)
+   createdAt DateTime    @default(now())
+ }
+
+ enum OrderStatus {
+   PENDING
+   CONFIRMED
+   SHIPPED
+   DELIVERED
+   CANCELLED
+ }
```

**Review workflow:**

1. Click each file in the Changes panel to see its diff
2. Accept individual files or `Apply All`
3. After applying, run your build/tests before committing
4. If something is wrong, `Cmd+Z` undoes the last applied change

## Composer Prompting Best Practices

### Be Specific About File Structure

```
# BAD
Create a blog feature

# GOOD
Create a blog feature with these files:
- src/api/posts/route.ts (GET list with pagination, POST create)
- src/api/posts/[slug]/route.ts (GET by slug, PUT update, DELETE)
- src/types/post.ts (Post interface, CreatePostInput, UpdatePostInput)
- src/services/post.service.ts (PostService class with Prisma operations)
```

### Reference Existing Patterns

```
# BAD
Add authentication middleware

# GOOD
@src/middleware/rateLimit.ts
Add authentication middleware in src/middleware/auth.ts following
the same middleware pattern: export a function that returns NextResponse,
use the same error response format, add the same type annotations.
```

### Incremental Over Monolithic

Instead of one massive prompt, break into steps:

1. "Create the Prisma models and run prisma generate"
2. "Create the service layer with CRUD operations"
3. "Create the API routes that use the service"
4. "Add validation schemas and wire them into the routes"
5. "Generate tests for the service and routes"

Each step can reference the output of the previous step.

## Enterprise Considerations

- **Code review before apply**: Always review diffs. Composer can hallucinate imports or use wrong patterns.
- **Version control**: Commit before running Composer on existing code. Easy rollback with `git checkout .`
- **Team standards**: Use `.cursor/rules/` to encode patterns so Composer follows team conventions
- **Cost awareness**: Composer uses premium model tokens. Complex multi-file prompts consume significant context.

## Resources

- [Composer Overview](https://docs.cursor.com/composer/overview)
- [Agent Mode](https://docs.cursor.com/agent)
- [Context Management](https://docs.cursor.com/context/@-symbols/overview)
