---
name: cursor-rules-config
description: 'Configure Cursor project rules using .cursor/rules/*.mdc files and legacy
  .cursorrules. Triggers on "cursorrules",

  ".cursorrules", "cursor rules", "cursor config", "cursor project settings", ".mdc
  rules", "project rules".

  '
allowed-tools: Read, Write, Edit, Bash(cmd:*)
version: 1.19.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- cursor
- cursor-rules
compatibility: Designed for Claude Code
---
# Cursor Rules Config

## Overview

Manage Cursor rules as versioned engineering policy that shapes AI context and behavior; rules must be specific, scoped, reviewed, and consistent with repository source of truth.

## Prerequisites

- Repository owner approval, existing engineering/security standards, and a test workspace.
- A reviewed ignore strategy for secrets, generated files, and sensitive data.

## Instructions

1. Write one clear rule per concern with scope, priority, and concrete acceptance behavior.
2. Keep shared rules in source control and use path-scoped rules for local conventions.
3. Test new rules on a non-sensitive fixture, inspect resulting behavior, and merge via normal review.
4. Periodically remove stale/conflicting rules and document any intentional exceptions.

## Output

- A reviewed, versioned rule set with clear scope and a tested behavior example.

## Error Handling

| Condition | Safe response |
|---|---|
| Rules conflict | Resolve to one authority and test the revised rule before rollout. |
| Rule exposes sensitive content | Remove it, repair ignore controls, and assess the exposure. |
| Rule is too broad | Scope it by path/task rather than disabling all shared governance. |

## Examples

Add a path-scoped API rule that requires existing validation and tests, then test it on a sanitized fixture. Open a PR for the rule and verify it does not apply to unrelated frontend files before merging.

Configure project-specific AI behavior through Cursor's rules system. The modern approach uses `.cursor/rules/*.mdc` files; the legacy `.cursorrules` file is still supported but deprecated.

## Rules System Architecture

### Modern Project Rules (.cursor/rules/*.mdc)

Each `.mdc` file contains YAML frontmatter followed by markdown content:

```yaml
---
description: "Enforce TypeScript strict mode and functional patterns"
globs: "src/**/*.ts,src/**/*.tsx"
alwaysApply: false
---
# TypeScript Standards

- Use `const` over `let`, never `var`
- Prefer pure functions over classes
- All functions must have explicit return types
- Use discriminated unions over enums
```

**Frontmatter fields:**

| Field | Type | Purpose |
|-------|------|---------|
| `description` | string | Concise rule purpose (shown in Cursor UI) |
| `globs` | string | Gitignore-style patterns for auto-attachment |
| `alwaysApply` | boolean | `true` = always active; `false` = only when matching files referenced |

### Rule Types by `alwaysApply` + `globs` Combination

| alwaysApply | globs | Behavior |
|-------------|-------|----------|
| `true` | empty | Always injected into every prompt |
| `false` | set | Auto-attached when matching files are in context |
| `false` | empty | Manual only -- reference with `@Cursor Rules` in chat |

### File Naming Convention

Use kebab-case with `.mdc` extension. Names should describe the rule's scope:

```
.cursor/rules/
  typescript-standards.mdc
  react-component-patterns.mdc
  api-error-handling.mdc
  testing-conventions.mdc
  database-migrations.mdc
  security-requirements.mdc
```

Create new rules via: `Cmd+Shift+P` > `New Cursor Rule`

### Complete Project Rules Example

**`.cursor/rules/project-context.mdc`** (always-on):

```yaml
---
description: "Core project context and conventions"
globs: ""
alwaysApply: true
---
# Project: E-Commerce Platform

Tech stack: Next.js 15, TypeScript 5.7, Prisma ORM, PostgreSQL, Tailwind CSS 4.
Package manager: pnpm. Monorepo with turborepo.

## Conventions
- API routes in `app/api/` using Route Handlers
- Server Components by default, `"use client"` only when needed
- Error boundaries at layout level
- All monetary values stored as integers (cents)
- Dates stored as UTC, displayed in user timezone
```

**`.cursor/rules/react-patterns.mdc`** (glob-scoped):

```yaml
---
description: "React component standards for TSX files"
globs: "src/**/*.tsx,app/**/*.tsx"
alwaysApply: false
---
# React Component Rules

- Export components as named exports, not default
- Props interface named `{Component}Props`
- Use `forwardRef` for components accepting `ref`
- Colocate styles in `.module.css` files
- Server Components: no `useState`, `useEffect`, or event handlers

```tsx
// Correct pattern
export interface ButtonProps {
  variant: 'primary' | 'secondary';
  children: React.ReactNode;
  onClick?: () => void;
}

export function Button({ variant, children, onClick }: ButtonProps) {
  return (
    <button className={styles[variant]} onClick={onClick}>
      {children}
    </button>
  );
}
```

```

**`.cursor/rules/api-routes.mdc`** (glob-scoped):
```yaml
---
description: "API route handler patterns"
globs: "app/api/**/*.ts"
alwaysApply: false
---
# API Route Standards

- Always validate request body with Zod
- Return typed `NextResponse.json()` responses
- Use consistent error response shape: `{ error: string, code: string }`
- Wrap handlers in try/catch with structured logging

```ts
import { NextRequest, NextResponse } from 'next/server';
import { z } from 'zod';

const CreateOrderSchema = z.object({
  items: z.array(z.object({
    productId: z.string().uuid(),
    quantity: z.number().int().positive(),
  })),
});

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const parsed = CreateOrderSchema.parse(body);
    const order = await createOrder(parsed);
    return NextResponse.json(order, { status: 201 });
  } catch (err) {
    if (err instanceof z.ZodError) {
      return NextResponse.json(
        { error: 'Validation failed', code: 'INVALID_INPUT', details: err.issues },
        { status: 400 }
      );
    }
    return NextResponse.json(
      { error: 'Internal server error', code: 'INTERNAL_ERROR' },
      { status: 500 }
    );
  }
}
```

```

## Legacy .cursorrules Format

Place a `.cursorrules` file in project root. Plain markdown, no frontmatter:

```markdown
# Project Rules

You are working on a Django REST Framework API.

## Stack
- Python 3.12, Django 5.1, DRF 3.15
- PostgreSQL 16 with pgvector extension
- Redis for caching and Celery broker
- pytest for testing

## Conventions
- ViewSets over function-based views
- Always use serializer validation
- Custom exceptions inherit from `APIException`
- All endpoints require authentication unless explicitly marked
- Use `select_related` and `prefetch_related` to avoid N+1 queries

## Code Style
- Type hints on all function signatures
- Docstrings on all public methods (Google style)
- Max function length: 30 lines
```

## Migration: .cursorrules to .cursor/rules/

Split a monolithic `.cursorrules` into scoped `.mdc` files:

1. Create `.cursor/rules/` directory
2. Extract global context into an `alwaysApply: true` rule
3. Extract language/framework rules into glob-scoped rules
4. Delete `.cursorrules` after verifying all rules load

## Referencing Files in Rules

Use `@file` syntax to include additional context files when a rule is applied:

```yaml
---
description: "Database schema context for migration files"
globs: "prisma/**/*.prisma,drizzle/**/*.ts"
alwaysApply: false
---
Reference these files for schema context:
@prisma/schema.prisma
@docs/data-model.md
```

## Debugging Rules

1. Open Chat and type `@Cursor Rules` to see which rules are active
2. Check glob patterns match your files: open a file, then verify the rule appears in context pills
3. Rules with `alwaysApply: true` always show; glob rules only appear when matching files are in context

## Enterprise Considerations

- **Version control**: Commit `.cursor/rules/` to git -- rules are project documentation
- **Team alignment**: Use `alwaysApply: true` for team-wide standards
- **Sensitive data**: Never put API keys, secrets, or credentials in rules files
- **Rule size**: Keep individual rules focused and under 200 lines; split large rules into multiple files
- **Audit trail**: Rules changes appear in git history for compliance review

## Resources

- [Cursor Rules Documentation](https://docs.cursor.com/context/rules)
- [MDC Rules Deep Dive](https://forum.cursor.com/t/a-deep-dive-into-cursor-rules-0-45/60721)
- [awesome-cursorrules](https://github.com/PatrickJS/awesome-cursorrules)
