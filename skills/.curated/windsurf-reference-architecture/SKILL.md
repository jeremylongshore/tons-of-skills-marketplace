---
name: windsurf-reference-architecture
description: 'Implement Devin Desktop (formerly Windsurf) reference architecture with optimal project structure
  and AI configuration.

  Use when designing workspace configuration for Windsurf, setting up team standards,

  or establishing architecture patterns that maximize Cascade effectiveness.

  Trigger with phrases like "windsurf architecture", "windsurf project structure",

  "windsurf best practices", "windsurf team setup", "optimize for cascade".

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
- configuration
- team-setup
compatibility: Designed for Claude Code
---
# Windsurf Reference Architecture

## Overview

Complete project architecture optimized for Windsurf AI. Covers workspace configuration, rules hierarchy, workflow organization, and team standardization patterns that maximize Cascade's effectiveness.

## Prerequisites

- Windsurf IDE installed
- Team agreement on coding standards
- Repository with consistent project structure

## Architecture Diagram

```
┌──────────────────────────────────────────────────────┐
│              Windsurf Workspace                       │
│  ┌───────────────┐  ┌────────────────────────────┐    │
│  │ .devin/rules/project.md│  │ .windsurf/                 │    │
│  │ (AI context)  │  │  ├── rules/ (trigger rules)│    │
│  │               │  │  ├── workflows/ (automation)│    │
│  │               │  │  └── settings.json         │    │
│  └───────────────┘  └────────────────────────────┘    │
│  ┌───────────────┐  ┌────────────────────────────┐    │
│  │ .codeiumignore│  │ ~/.codeium/                │    │
│  │ (index rules) │  │  ├── global_rules.md       │    │
│  │               │  │  ├── windsurf/memories/    │    │
│  │               │  │  └── windsurf/mcp_config   │    │
│  └───────────────┘  └────────────────────────────┘    │
├──────────────────────────────────────────────────────┤
│              Cascade AI Engine                        │
│  ┌───────────┐  ┌───────────┐  ┌─────────────────┐   │
│  │ Super-    │  │ Cascade   │  │ Command         │   │
│  │ complete  │  │ Write/Chat│  │ (Inline Edit)   │   │
│  │ (Tab)     │  │ (Cmd+L)  │  │ (Cmd+I)         │   │
│  └───────────┘  └───────────┘  └─────────────────┘   │
├──────────────────────────────────────────────────────┤
│              Context Layers                           │
│  Rules > Memories > @Mentions > Open Files > Index   │
└──────────────────────────────────────────────────────┘
```

## Tool Use

- Use `Read` to inspect only the repository files and configuration needed for the request.
- Use `Grep` to locate relevant settings, rules, logs, or code without broad collection.

## Instructions

### Step 1: Project File Structure

```
my-project/
├── .devin/rules/project.md              # AI context (stack, patterns, constraints)
├── .codeiumignore              # Indexing exclusions
├── .windsurf/
│   ├── settings.json           # IDE settings (committed)
│   ├── rules/
│   │   ├── testing.md          # trigger: glob **/*.test.ts
│   │   ├── api-routes.md       # trigger: glob src/routes/**
│   │   ├── security.md         # trigger: model_decision
│   │   └── migrations.md       # trigger: manual
│   └── workflows/
│       ├── new-feature.md      # /new-feature
│       ├── deploy-staging.md   # /deploy-staging
│       ├── review-pr.md        # /review-pr
│       └── quality-check.md    # /quality-check
├── src/
│   ├── routes/                 # API route handlers
│   ├── services/               # Business logic
│   ├── repositories/           # Data access
│   └── types/                  # Shared types
├── tests/
│   ├── fixtures/               # Test data factories
│   └── services/               # Service unit tests
└── docs/
    └── architecture.md         # Architecture decisions
```

### Step 2: Rules Hierarchy

```yaml
# Priority order (highest to lowest):
rules_hierarchy:
  1_global_rules:
    path: ~/.codeium/windsurf/memories/global_rules.md
    limit: 6000 chars
    scope: All workspaces
    use_for: "Personal coding preferences, universal standards"

  2_workspace_rule:
    path: .devin/rules/project.md (project root)
    limit: 12000 chars
    scope: Current workspace
    use_for: "Project stack, architecture, conventions"

  3_location_scoped_rules:
    path: .devin/rules/*.md or AGENTS.md in subdirectories
    limit: 12000 chars each
    scope: Triggered by glob, model_decision, or manual
    use_for: "File-type-specific patterns, conditional rules"

  4_memories:
    path: ~/.codeium/windsurf/memories/
    scope: Workspace-specific (auto-generated)
    use_for: "Decisions, discoveries (supplement, don't replace rules)"

# Total active chars: 12000 max (global + workspace rules combined)
# If exceeded: global rules take priority, workspace rules truncated
```

### Step 3: Team Configuration Template

```json
// .windsurf/settings.json (committed to git)
{
  "codeium.indexing.excludePatterns": [
    "node_modules/**", "dist/**", ".next/**",
    "coverage/**", "*.min.js", "**/*.map"
  ],
  "codeium.autocomplete.enable": true,
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "biomejs.biome",
  "typescript.tsdk": "node_modules/typescript/lib",
  "files.associations": { "*.css": "tailwindcss" }
}
```

### Step 4: Monorepo Strategy

```
monorepo/
├── .devin/rules/project.md              # Shared conventions (brief)
├── .codeiumignore              # Broad exclusions
├── apps/
│   ├── web/
│   │   └── .devin/rules/project.md      # Next.js-specific rules
│   └── mobile/
│       └── .devin/rules/project.md      # React Native rules
├── packages/
│   ├── api/
│   │   └── .devin/rules/project.md      # Express/Fastify rules
│   └── shared/
│       └── .devin/rules/project.md      # Library conventions
└── .windsurf/
    └── workflows/              # Cross-package workflows

# BEST PRACTICE: Open apps/web/ or packages/api/ directly
# NOT the monorepo root
# Cascade gets focused context per workspace window
```

### Step 5: Context Pinning Strategy

```markdown
## What to Pin in Cascade

Pin files that provide essential context:
- Type definition files (types/*.ts)
- Architecture decision records (docs/adr/)
- API schema files (openapi.yaml)
- Database schema (prisma/schema.prisma, drizzle/schema.ts)

How to pin:
- Click the pin icon next to a file in the Cascade context area
- Pinned files are always included in Cascade's context window
- Limit: pin 3-5 files max (more = diluted context)
```

## Output

Deliver a repository-grounded architecture showing Rules, `AGENTS.md`, Workflows, Skills, Hooks, MCP boundaries, ignore files, CI gates, ownership, and validation commands. Explain why each customization mechanism was chosen and how it activates.

## Error Handling

| Issue | Cause | Solution |
|-------|-------|----------|
| Cascade ignores project patterns | Missing/empty .devin/rules/project.md | Add stack and architecture details |
| Rules truncated | Over 12,000 combined chars | Split into workspace rules with triggers |
| Wrong patterns for file type | No glob-triggered rules | Add `.devin/rules/` with glob triggers |
| Team inconsistency | No shared config | Commit `.windsurf/` directory to git |
| Slow indexing in monorepo | Root workspace open | Open specific package/app directory |

## Examples

### Minimal .devin/rules/project.md for Any Project

```markdown
# Project: Inventory API
Stack: TypeScript, Fastify, and PostgreSQL.
Testing: Run Vitest unit tests and the repository integration suite.
Conventions:
- Validate external input at the route boundary.
- Keep database access behind repository modules.
- Add or update a regression test with every bug fix.
Avoid:
- Writing secrets, production data, or generated output into source files.
- Bypassing protected migrations or deployment approval.
```

### Verify Architecture Setup

```bash
set -euo pipefail
echo "=== Windsurf Architecture Check ==="
echo "Rules: $([ -f .devin/rules/project.md ] && wc -c < .devin/rules/project.md || echo 'MISSING') chars"
echo "Ignore: $([ -f .codeiumignore ] && wc -l < .codeiumignore || echo 'MISSING') patterns"
echo "Rules dir: $(ls .devin/rules/ 2>/dev/null | wc -l || echo 0) files"
echo "Workflows: $(ls .windsurf/workflows/ 2>/dev/null | wc -l || echo 0) files"
```

## Resources

- [Focused first-party references](references/official-docs.md)
- [Windsurf Rules Directory](https://windsurf.com/editor/directory)
- [Context Awareness](https://docs.devin.ai/desktop/context-awareness/overview)
- [Cascade Customizations Catalog](https://github.com/Windsurf-Samples/cascade-customizations-catalog)

## Related Skill

Continue with `windsurf-architecture-variants` to adapt this baseline to monorepos, multi-service workspaces, polyglot stacks, and large organizations.
