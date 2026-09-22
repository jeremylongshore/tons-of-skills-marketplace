---
name: cursor-reference-architecture
description: 'Reference architecture for Cursor IDE projects: directory structure,
  rules organization, indexing

  strategy, and team configuration patterns. Triggers on "cursor architecture", "cursor
  project structure",

  "cursor best practices", "cursor file structure".

  '
allowed-tools: Read, Write, Edit, Bash(cmd:*)
version: 1.19.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- cursor
- cursor-reference
compatibility: Designed for Claude Code
---
# Cursor Reference Architecture

## Overview

Organize Cursor rules, ignore files, repository guidance, and workspace boundaries so AI assistance follows architecture rather than inventing it.

## Prerequisites

- An approved repository architecture, ownership model, and data-classification policy.
- Maintainers authorized to review `.cursor/rules`, ignore files, and shared templates.

## Instructions

1. Put durable engineering conventions in reviewed rules and keep sensitive/generated paths in ignore files.
2. Scope rules by repository area and avoid contradictory always-on instructions.
3. Test rule and indexing changes in a representative workspace before organization-wide rollout.
4. Review these files through normal pull requests with security and architecture owners when relevant.

## Output

- A versioned Cursor configuration that maps rules and context boundaries to real repository ownership.

## Error Handling

| Condition | Safe response |
|---|---|
| Rules conflict | Reduce them to one authoritative rule and test in a small workspace. |
| Sensitive paths are indexed | Add an ignore rule, verify exclusion, and evaluate exposure according to policy. |
| A shared template breaks a repo | Revert the configuration change and use a scoped repository override. |

## Examples

For a monorepo, commit a reviewed root rule for shared import conventions and scoped rules for each application. Add secrets, generated artifacts, and customer exports to ignore configuration, then verify a sample chat cannot attach those paths.

Reference architecture patterns for optimizing Cursor IDE project setup. Covers directory structure, rules organization, indexing strategy, and multi-project configuration for maximum AI effectiveness.

## Project Layout for Cursor

A well-structured project makes AI features significantly more effective:

```
my-project/
├── .cursor/
│   └── rules/
│       ├── project.mdc          # alwaysApply: true (stack, conventions)
│       ├── security.mdc         # alwaysApply: true (security constraints)
│       ├── typescript.mdc       # globs: "**/*.ts,**/*.tsx"
│       ├── api-routes.mdc       # globs: "src/api/**/*.ts"
│       ├── database.mdc         # globs: "src/db/**/*.ts,prisma/**"
│       └── testing.mdc          # globs: "**/*.test.ts,**/*.spec.ts"
├── .cursorignore                # Exclude from AI + indexing
├── .cursorindexingignore        # Exclude from indexing only
├── .gitignore
├── src/
│   ├── api/                     # API routes
│   ├── services/                # Business logic
│   ├── db/                      # Database layer
│   ├── types/                   # Shared TypeScript types
│   ├── utils/                   # Utility functions
│   └── components/              # UI components
├── tests/
├── prisma/
├── docs/                        # Architecture docs (good for @Docs)
└── package.json
```

### Why This Structure Helps Cursor

1. **Glob patterns work predictably**: `src/api/**/*.ts` cleanly scopes API rules
2. **@Files references are intuitive**: `@src/types/user.ts` is discoverable
3. **Indexing is focused**: clear separation of code vs build output vs data
4. **Rules inheritance**: project-level always-on + directory-scoped rules

## Rules Architecture

### Layer 1: Always-On Global Rules

```yaml
# .cursor/rules/project.mdc
---
description: "Core project context and conventions"
globs: ""
alwaysApply: true
---
# SaaS Dashboard Application

Stack: Next.js 15 (App Router), TypeScript 5.7, PostgreSQL 16, Prisma 6
Auth: NextAuth.js v5 with GitHub OAuth
Styling: Tailwind CSS 4
Testing: Vitest + Playwright
Package manager: pnpm

## Architecture Decisions
- Server Components by default, "use client" only when needed
- Repository pattern for database access
- Zod schemas for all external input validation
- Result types for error handling (never throw from services)
```

### Layer 2: Security (Always-On)

```yaml
# .cursor/rules/security.mdc
---
description: "Security constraints for all AI-generated code"
globs: ""
alwaysApply: true
---
# Security Requirements
- NEVER hardcode secrets, API keys, or passwords
- ALWAYS use parameterized queries (no string interpolation in SQL)
- ALWAYS validate and sanitize user input with Zod
- NEVER disable CORS, CSRF protection, or TLS verification
- Use httpOnly, secure, sameSite cookies for auth tokens
- Rate limit all public API endpoints
```

### Layer 3: Technology-Specific (Glob-Scoped)

```yaml
# .cursor/rules/react-components.mdc
---
description: "React component patterns"
globs: "src/components/**/*.tsx,app/**/*.tsx"
alwaysApply: false
---
# Component Standards
- Named exports only (no default exports)
- Props interface: {ComponentName}Props
- Use forwardRef for interactive components
- Colocate tests: Component.test.tsx next to Component.tsx
- Loading states: use Suspense boundaries, not conditional rendering
```

```yaml
# .cursor/rules/api-routes.mdc
---
description: "API route handler patterns"
globs: "app/api/**/*.ts,src/api/**/*.ts"
alwaysApply: false
---
# API Route Standards
- All handlers wrapped in withAuth() middleware
- Input validation with Zod (parse body, params, query)
- Response shape: { data: T } or { error: string, code: string }
- HTTP status codes: 200 OK, 201 Created, 400 Bad Request, 401, 403, 404, 500
- Structured logging with requestId for traceability
```

```yaml
# .cursor/rules/database.mdc
---
description: "Database access patterns"
globs: "src/db/**/*.ts,src/repositories/**/*.ts,prisma/**"
alwaysApply: false
---
# Database Conventions
- All queries via repository classes (never raw Prisma in API routes)
- Use transactions for multi-table writes
- Always include select/include to avoid over-fetching
- Pagination: cursor-based for lists, offset for admin tools
- Soft delete: use deletedAt timestamp, never hard delete user data
```

### Layer 4: Manual Reference Rules

```yaml
# .cursor/rules/deployment.mdc
---
description: "Deployment and infrastructure patterns"
globs: ""
alwaysApply: false
---
# Deployment
- Vercel for frontend, Railway for API
- Environment variables managed in Vercel/Railway dashboards
- Database migrations: `prisma migrate deploy` in CI
- Feature flags via LaunchDarkly
```

Reference manually with `@Cursor Rules` in Chat when discussing deployment.

## Indexing Strategy

### Optimized .cursorignore

```gitignore
# Build output
dist/
build/
.next/
out/
.vercel/
.turbo/
coverage/

# Dependencies
node_modules/
.pnpm-store/

# Generated
*.min.js
*.min.css
*.d.ts.map
*.tsbuildinfo
pnpm-lock.yaml

# Data / Assets
*.csv
*.sql
*.sqlite
*.png
*.jpg
*.gif
*.svg
*.ico
*.woff
*.woff2
*.ttf

# Environment
.env*

# IDE
.vscode/
.idea/
```

### .cursorindexingignore for Large References

```gitignore
# Not indexed, but accessible via @Files
docs/api-spec.yaml
tests/fixtures/
scripts/migration-data/
```

## Monorepo Architecture

### Turborepo / pnpm Workspaces

```
monorepo/
├── .cursor/
│   └── rules/
│       ├── monorepo.mdc         # alwaysApply: true (shared conventions)
│       ├── shared-types.mdc     # globs: "packages/shared/**"
│       ├── api.mdc              # globs: "apps/api/**"
│       └── web.mdc              # globs: "apps/web/**"
├── .cursorignore
├── apps/
│   ├── api/
│   ├── web/
│   └── admin/
├── packages/
│   ├── shared/
│   ├── ui/
│   └── config/
├── turbo.json
└── pnpm-workspace.yaml
```

**Key rule for monorepos:**

```yaml
# .cursor/rules/monorepo.mdc
---
description: "Monorepo import conventions"
globs: ""
alwaysApply: true
---
# Import Conventions
- Import shared types: import { User } from '@myorg/shared'
- Import UI components: import { Button } from '@myorg/ui'
- NEVER use relative paths across package boundaries
- Each package has its own tsconfig.json extending root
```

## Configuration Files Summary

| File | Committed to Git | Purpose |
|------|-----------------|---------|
| `.cursor/rules/*.mdc` | Yes | AI behavior rules (team-shared) |
| `.cursorignore` | Yes | File exclusion from AI + indexing |
| `.cursorindexingignore` | Yes | File exclusion from indexing only |
| `settings.json` (Cursor) | No (machine-local) | Editor preferences |
| `keybindings.json` (Cursor) | No (machine-local) | Custom shortcuts |

## Enterprise Considerations

- **Rules as code**: Treat `.cursor/rules/` changes like infrastructure changes -- require PR review
- **Template repository**: Create a company template repo with standard rules, ignore files, and onboarding docs
- **Compliance mapping**: Map security rules to specific compliance controls (SOC 2 CC6.1, etc.)
- **Architecture documentation**: Keep `docs/` directory indexed so AI can reference architecture decisions via `@Docs`

## Resources

- [Cursor Rules Documentation](https://docs.cursor.com/context/rules)
- [Codebase Indexing](https://docs.cursor.com/context/codebase-indexing)
- [Ignore Files](https://docs.cursor.com/context/ignore-files)
