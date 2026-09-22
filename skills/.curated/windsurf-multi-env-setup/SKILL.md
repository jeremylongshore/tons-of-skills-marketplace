---
name: windsurf-multi-env-setup
description: 'Configure Devin Desktop (formerly Windsurf) IDE and Cascade AI across team members and project
  environments.

  Use when onboarding teams to Windsurf, setting up per-project Cascade configuration,

  or managing Windsurf settings across development, staging, and production contexts.

  Trigger with phrases like "windsurf team setup", "windsurf environments",

  "windsurf multi-project", "windsurf team config", "cascade rules per env".

  '
allowed-tools: Read, Write, Edit
argument-hint: "[scope or requirements]"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- windsurf
- team-setup
- multi-environment
compatibility: Designed for Claude Code
---
# Windsurf Multi-Environment Setup

## Overview

Configure Windsurf consistently across team members, projects, and deployment contexts. Windsurf is an IDE, not a cloud API -- "multi-environment setup" means standardizing AI behavior, workspace configuration, and Cascade context across your team.

## Prerequisites

- Windsurf IDE installed on developer machines
- Shared git repository
- Team agreement on coding standards per service

## Tool Use

- Use `Read` to inspect only the repository files and configuration needed for the request.
- Use `Write` only for a new artifact the user requested; never write credentials or unreviewed production configuration.
- Use `Edit` for bounded, reviewable changes and preserve unrelated user work.

## Instructions

### Step 1: Per-Project Cascade Rules

```markdown
<!-- .devin/rules/project.md - committed to each service repo -->

# Project: PaymentService

## Stack
- Language: TypeScript (strict)
- Framework: Fastify v4
- Database: PostgreSQL with Drizzle
- Testing: Vitest
- Queue: BullMQ for async jobs

## Architecture Rules
- All handlers in src/routes/ — never business logic
- Business logic in src/services/ only
- Database queries in src/repositories/ only
- Use Result<T, E> pattern for errors, never throw in services
- PCI-sensitive data only in src/pci/ (encrypted at rest)

## Naming Conventions
- Route handlers: GET/POST/PUT/DELETE prefix
- Service methods: verb + noun (createPayment, findOrder)
- Repository methods: DB operations (findById, upsert)
```

### Step 2: Team IDE Settings Template

```json
// .windsurf/settings.json - committed to repo
{
  "codeium.indexing.excludePatterns": [
    "node_modules/**", "dist/**", ".next/**",
    "coverage/**", "*.min.js", "**/*.map", "**/*.lock"
  ],
  "codeium.autocomplete.enable": true,
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "biomejs.biome",
  "typescript.tsdk": "node_modules/typescript/lib"
}
```

### Step 3: Monorepo Multi-Service Setup

```
monorepo/
  services/
    auth/
      .devin/rules/project.md        # Auth context: JWT, OAuth, session management
      .codeiumignore         # Exclude auth secrets directory
    payments/
      .devin/rules/project.md        # Payments context: Stripe, PCI compliance
      .codeiumignore         # Exclude PCI data directories
    notifications/
      .devin/rules/project.md        # Notifications: queues, email templates
      .codeiumignore
  .windsurf/
    settings.json            # Shared IDE settings
    rules/
      shared-patterns.md     # trigger: always_on
    workflows/
      deploy-service.md      # /deploy-service workflow
```

**Key practice:** Each developer opens their service directory as the workspace, NOT the monorepo root. This gives Cascade focused context and fast indexing.

### Step 4: Environment-Specific Workflow Rules

```markdown
<!-- .devin/rules/deployment-context.md -->
---
trigger: glob
globs: deploy/**, scripts/deploy-*, .github/workflows/deploy-*
---
## Deployment Rules
- Target: AWS ECS on us-east-1
- Container registry: 123456789.dkr.ecr.us-east-1.amazonaws.com
- Secrets: AWS Secrets Manager (prefix: myapp/{environment}/)
- Never hardcode environment-specific values
- All environment config via ENV vars, not config files
- Staging deploys from develop branch, production from main
```

### Step 5: Onboarding Script

```bash
#!/bin/bash
# scripts/setup-windsurf.sh
set -euo pipefail

echo "Setting up Windsurf for this project..."

# Verify Windsurf installation
windsurf --version || { echo "Install Windsurf: https://windsurf.com/download"; exit 1; }

# Install recommended extensions
windsurf --install-extension esbenp.prettier-vscode
windsurf --install-extension dbaeumer.vscode-eslint

# Disable conflicting extensions
windsurf --disable-extension github.copilot 2>/dev/null || true
windsurf --disable-extension tabnine.tabnine-vscode 2>/dev/null || true

# Verify configuration
[ -f ".devin/rules/project.md" ] || echo "WARNING: .devin/rules/project.md not found"
[ -f ".codeiumignore" ] || echo "WARNING: .codeiumignore not found"

echo ""
echo "Setup complete."
echo "IMPORTANT: Open your service directory (not monorepo root) for best Cascade performance."
echo "Example: windsurf services/payments/"
```

### Step 6: Per-Environment MCP Configuration

```json
// ~/.codeium/windsurf/mcp_config.json
// Developers can configure environment-specific MCP servers
{
  "mcpServers": {
    "staging-db": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "DATABASE_URL": "${STAGING_DATABASE_URL}"
      }
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
      }
    }
  }
}
```

## Output

Return an environment matrix showing shared versus local settings, repository Rules and `AGENTS.md`, excluded paths, identity ownership, test commands, and drift checks. Keep production credentials and environment endpoints outside version-controlled examples.

## Error Handling

| Issue | Cause | Solution |
|-------|-------|----------|
| Cascade lacks project context | .devin/rules/project.md missing or empty | Add stack + patterns to rules file |
| Slow indexing | Monorepo root open with no ignore rules | Open service subdirectory |
| Inconsistent team suggestions | No shared settings | Commit `.windsurf/settings.json` |
| Cascade touches wrong files | Too broad workspace scope | Open specific service directory |
| New dev has no AI context | Skipped onboarding | Run setup-windsurf.sh script |

## Examples

### Quick Health Check

```bash
ls -la .devin/rules/project.md .codeiumignore .windsurf/settings.json 2>/dev/null
```

### Per-Environment Cascade Workflows

```markdown
<!-- .windsurf/workflows/deploy-staging.md -->
---
name: deploy-staging
---
1. Run `npm test` — abort if failures
2. Run `npm run build`
3. Run `aws ecs update-service --cluster staging --service payments --force-new-deployment`
4. Wait 60 seconds, then check: `curl -sf https://staging-api.example.com/health | jq .`
```

## Resources

- [Focused first-party references](references/official-docs.md)
- [Windsurf Rules Documentation](https://docs.devin.ai/desktop/cascade/memories)
- [Windsurf Admin Guide](https://docs.devin.ai/desktop/guide-for-admins)
- [Context Awareness](https://docs.devin.ai/desktop/context-awareness/overview)

## Related Skill

Continue with `windsurf-reference-architecture` to connect environment-specific controls to the repository-wide configuration, ownership, validation, and governance model.
