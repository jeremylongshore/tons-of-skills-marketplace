---
name: windsurf-architecture-variants
description: 'Choose workspace architectures for different project scales in Devin Desktop (formerly Windsurf).

  Use when deciding how to structure Windsurf workspaces for monorepos,

  multi-service setups, or polyglot codebases.

  Trigger with phrases like "windsurf workspace strategy", "windsurf monorepo",

  "windsurf project layout", "windsurf multi-service", "windsurf workspace size".

  '
allowed-tools: Read, Grep
argument-hint: "[scope or requirements]"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- windsurf
- architecture
- workspace
- monorepo
compatibility: Designed for Claude Code
---
# Windsurf Architecture Variants

## Overview

Workspace structure directly affects Cascade context and indexing behavior. Select and verify an architecture for single projects, monorepos, multi-service systems, polyglot codebases, or large organizations.

## Prerequisites

- Windsurf installed
- Understanding of Cascade's workspace indexing model
- Git workflow established

Confirm the target repository size, ownership boundaries, and developer workflow before selecting a workspace layout.

## Authentication

Public documentation checks require no authentication. Any editor, organization, remote-indexing, or MCP operation uses the operator's existing Devin Desktop session and the target provider's approved credentials; never copy those credentials into repository files.

## Tool Use

- Use `Read` to inspect only the repository files and configuration needed for the request.
- Use `Grep` to locate relevant settings, rules, logs, or code without broad collection.

## Instructions

### Step 1: Select the Single-Project Variant (Solo / Small Team)

**Best for:** 1-3 developers, single service, <10K files.

```
my-project/
├── .devin/rules/project.md          # Full project context
├── .codeiumignore          # Exclude build artifacts
├── src/
├── tests/
├── package.json
└── README.md
```

**Configuration:**

- Open entire project as workspace
- Cascade indexes everything — no partitioning needed
- `.devin/rules/project.md` contains complete stack and architecture details

### Step 2: Select Focused Monorepo Windows (Medium Team)

**Best for:** 3-15 developers, monorepo with 2-10 packages.

```
monorepo/
├── .devin/rules/project.md          # Brief shared conventions
├── .codeiumignore          # Aggressive exclusions at root
├── packages/
│   ├── api/
│   │   ├── .devin/rules/project.md  # API-specific rules
│   │   └── .codeiumignore
│   ├── web/
│   │   ├── .devin/rules/project.md  # Frontend-specific rules
│   │   └── .codeiumignore
│   └── shared/
│       ├── .devin/rules/project.md  # Library conventions
│       └── .codeiumignore
└── .windsurf/
    └── workflows/          # Shared workflows
```

**Strategy:**

```bash
# Each developer opens their package directory:
windsurf packages/api/        # Backend dev
windsurf packages/web/        # Frontend dev
windsurf packages/shared/     # Library maintainer

# NOT: windsurf monorepo/     # Too broad!
```

### Step 3: Select a Multi-Window Team Workflow (Large Team)

**Best for:** 15+ developers, microservices, 50K+ total files.

```
Developer A: Windsurf → services/auth/        (auth service)
Developer B: Windsurf → services/payments/    (payments)
Developer C: Windsurf → services/notifications/ (notifications)
Developer D: Windsurf → shared/libs/          (shared libraries)

Each developer gets focused Cascade context per workspace window.
```

**Team conventions:**

```markdown
1. One Windsurf window per service/package
2. Every service has its own .devin/rules/project.md and .codeiumignore
3. Cascade tasks scoped to current workspace only
4. Cross-service changes: open both workspaces side by side
5. Tag cascade commits: git commit -m "[cascade] description"
6. Use shared workflows from central config repo
```

### Step 4: Add Polyglot and Language-Specific Boundaries

**Best for:** Projects with multiple languages (TypeScript + Python + Go).

```
# Each language has different .devin/rules/project.md
services/
├── ts-api/
│   └── .devin/rules/project.md     # TypeScript patterns, Fastify, Vitest
├── python-ml/
│   └── .devin/rules/project.md     # Python patterns, FastAPI, pytest
└── go-gateway/
    └── .devin/rules/project.md     # Go patterns, chi router, go test
```

```markdown
<!-- .devin/rules/project.md for Python service -->
# Project: ML Pipeline

## Stack
- Language: Python 3.11
- Framework: FastAPI
- ML: scikit-learn, pandas
- Testing: pytest with fixtures
- Type checking: mypy (strict)

## Conventions
- Use pydantic for all data models
- Async endpoints with asyncio
- Type hints on all functions
- No print() — use logging module
```

### Step 5: Add Frontend and Design-System Context

**Best for:** UI-heavy projects with design system, Storybook, component library.

```markdown
<!-- .devin/rules/project.md for design system -->
# Project: Design System

## Stack
- Framework: React 18 + Next.js 14
- Styling: Tailwind CSS + custom tokens
- Components: Radix UI primitives
- Docs: Storybook 8
- Testing: Vitest + Testing Library

## Component Conventions
- One component per file (ComponentName.tsx)
- Co-located tests: ComponentName.test.tsx
- Co-located stories: ComponentName.stories.tsx
- Props interface exported: ComponentNameProps
- Use forwardRef for all components
- Use CVA (class-variance-authority) for variants

## Design Tokens
- Colors: use design-system/tokens, never raw Tailwind colors
- Spacing: use space-* scale (4px base)
- Typography: use text-* presets
```

**Cascade integration:** Use Previews to iterate on UI components:

```
"Preview the Button component with all variants"
Click elements in Preview → send to Cascade for refinement
```

## Decision Matrix

| Factor | Solo | Focused Mono | Multi-Window | Polyglot |
|--------|------|-------------|-------------|----------|
| Team Size | 1-3 | 3-15 | 15+ | Any |
| Codebase | <10K files | 10K-50K | 50K+ | Mixed |
| Cascade Speed | Fast | Fast (per window) | Fast (per window) | Fast (per window) |
| Setup Effort | Minimal | .codeiumignore + rules | Per-service config | Per-language rules |
| Context Quality | Excellent | Good | Good | Good (per lang) |

## Output

Deliver a workspace topology recommendation naming the selected variant, indexing boundaries, rule and `AGENTS.md` locations, ignore strategy, tradeoffs, and a staged migration plan. Include explicit assumptions for repository size, languages, ownership, and team concurrency.

## Error Handling

| Issue | Cause | Solution |
|-------|-------|----------|
| Cascade is slow | Too many files indexed | Open smaller workspace, add .codeiumignore |
| Wrong file context | Monorepo root open | Open specific service directory |
| Conflicting edits | Multiple devs, same files | Feature branches per Cascade session |
| Wrong language patterns | Multi-language workspace | Separate .devin/rules/project.md per language directory |
| Stale suggestions | Index out of date | Preserve diagnostics, then use the current indexing reset control |

## Examples

### Optimized .codeiumignore (Universal)

```gitignore
node_modules/
dist/
build/
.next/
coverage/
*.min.js
*.map
__pycache__/
.venv/
target/
vendor/
*.log
*.sqlite
```

### Workspace Health Check

```bash
set -euo pipefail
FILE_COUNT=$(find . -type f -not -path '*/node_modules/*' -not -path '*/.git/*' | wc -l)
echo "Indexed files: ~$FILE_COUNT"
[ "$FILE_COUNT" -gt 10000 ] && echo "WARNING: Consider opening a subdirectory"
[ -f .devin/rules/project.md ] && echo "Rules: $(wc -c < .devin/rules/project.md) chars" || echo "Rules: MISSING"
[ -f .codeiumignore ] && echo "Ignore: $(wc -l < .codeiumignore) patterns" || echo "Ignore: MISSING"
```

## Resources

- [Focused first-party references](references/official-docs.md)
- [Windsurf Context Awareness](https://docs.devin.ai/desktop/context-awareness/overview)
- [Windsurf Ignore](https://docs.devin.ai/desktop/context-awareness/windsurf-ignore)

## Related Skill

Continue with `windsurf-known-pitfalls` to test the selected architecture against indexing, context, configuration, and team-workflow failure modes.
