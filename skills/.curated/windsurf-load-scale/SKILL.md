---
name: windsurf-load-scale
description: 'Scale Devin Desktop (formerly Windsurf) adoption across large organizations with workspace strategies
  and performance tuning.

  Use when rolling out Windsurf to 50+ developers, managing large monorepo workspaces,

  or planning enterprise-scale deployment.

  Trigger with phrases like "windsurf at scale", "windsurf large team",

  "windsurf monorepo", "windsurf organization", "windsurf 100 developers".

  '
argument-hint: "[team size and repository topology]"
allowed-tools: Read, Write, Edit
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- windsurf
- scaling
- enterprise
- large-team
compatibility: Designed for Claude Code
---
# Windsurf Load & Scale

## Overview

Strategies for deploying Devin Desktop (formerly Windsurf) across large organizations. Covers workspace partitioning, policy distribution, quota governance, and performance at scale.

## Prerequisites

- Windsurf Teams or Enterprise plan
- Admin dashboard access
- Understanding of team structure and repository layout
- Network/IT involvement for enterprise features

## Tool Use

- Use `Read` to inspect only the repository files and configuration needed for the request.
- Use `Write` only for a new artifact the user requested; never write credentials or unreviewed production configuration.
- Use `Edit` for bounded, reviewable changes and preserve unrelated user work.

## Instructions

### Step 1: Workspace Strategy for Large Codebases

```yaml
# Windsurf performance degrades with workspace size
# Cascade context quality inversely correlates with file count

workspace_sizing:
  optimal: "<5,000 files — fast indexing, precise Cascade context"
  acceptable: "Measure against available RAM and current indexing guidance"
  problematic: "20,000+ files — must partition into sub-workspaces"
  unworkable: "100,000+ files at root — Cascade context diluted, indexing very slow"

# Strategy: one Windsurf window per service/package
# Each developer opens their assigned service directory
```

### Step 2: Monorepo Partitioning

```
# Large monorepo (100K+ files)
company-monorepo/
├── .devin/rules/project.md              # Brief shared conventions only
├── .codeiumignore              # Aggressive: exclude EVERYTHING except src
├── apps/
│   ├── web-app/                # Developer A opens this window
│   │   ├── .devin/rules/project.md      # Next.js-specific AI context
│   │   └── .codeiumignore      # Local exclusions
│   ├── mobile-app/             # Developer B opens this window
│   │   ├── .devin/rules/project.md      # React Native context
│   │   └── .codeiumignore
│   └── admin-portal/           # Developer C opens this window
│       ├── .devin/rules/project.md
│       └── .codeiumignore
├── services/
│   ├── api-gateway/            # Backend team opens individual services
│   ├── auth-service/
│   ├── payment-service/
│   └── notification-service/
├── packages/
│   └── shared-types/           # Library maintainer opens this
└── infrastructure/
    └── terraform/              # DevOps opens this
```

**Rule:** Never open the monorepo root in Windsurf. Each developer opens their service directory.

### Step 3: Configuration Distribution at Scale

```yaml
# Central config repo for team-wide standards
windsurf-config/
├── templates/
│   ├── windsurfrules/
│   │   ├── nextjs.md           # Template for Next.js projects
│   │   ├── fastify.md          # Template for Fastify APIs
│   │   ├── react-native.md     # Template for mobile apps
│   │   └── shared-library.md   # Template for shared packages
│   ├── codeiumignore/
│   │   ├── node-project.ignore
│   │   ├── python-project.ignore
│   │   └── go-project.ignore
│   └── workflows/
│       ├── deploy-staging.md
│       ├── pr-review.md
│       └── quality-check.md
├── scripts/
│   ├── setup-windsurf.sh       # Onboarding script
│   └── sync-config.sh          # Distribute updates
└── README.md
```

**Sync script:**

```bash
#!/bin/bash
set -euo pipefail
# scripts/sync-config.sh — run from monorepo root

TEMPLATE_DIR="/path/to/windsurf-config/templates"

for service_dir in apps/*/  services/*/; do
  [ -d "$service_dir" ] || continue
  SERVICE=$(basename "$service_dir")

  # Copy .codeiumignore if missing
  [ -f "$service_dir/.codeiumignore" ] || \
    cp "$TEMPLATE_DIR/codeiumignore/node-project.ignore" "$service_dir/.codeiumignore"

  # Copy shared workflows
  mkdir -p "$service_dir/.windsurf/workflows"
  cp "$TEMPLATE_DIR/workflows/"*.md "$service_dir/.windsurf/workflows/" 2>/dev/null || true

  echo "Synced: $SERVICE"
done
```

### Step 4: Seat and Usage Governance at Scale

```yaml
# Usage planning for large teams; populate values from the current contract
usage_governance:
  team_size: 100

  seat_allocation:
    full_seats: 70        # regular users who require Desktop and included quota
    flex_seats: 30        # occasional users, when permitted by current plan

  controls:
    contract_owner: finance-platform
    on_demand_limit: "set in admin billing settings"
    review_period: quarterly

  optimization:
    quarterly_review: "Confirm roles and right-size inactive seats"
    training_program: "Monthly 30-min workshop for new features"
    workflow_investment: "Build reusable skills and workflows for common tasks"
```

### Step 5: Enterprise Network Configuration

```yaml
# IT/Network team requirements
network_config:
  endpoints_to_whitelist:
    - "*.codeium.com"          # AI inference
    - "*.windsurf.com"         # Auth, updates, admin portal
    - "windsurf.com"           # Downloads, documentation

  proxy_support:
    http_proxy: "${HTTP_PROXY}"
    https_proxy: "${HTTPS_PROXY}"
    no_proxy: "localhost,127.0.0.1,.internal.company.com"
    # Set via Windsurf Settings or environment variables

  deployment_modes:
    cloud: "Standard — code context sent to Codeium cloud"
    hybrid: "Code stays local, only prompts sent to cloud"
    negotiated_controls: "Document only the deployment and data controls in the current contract"
```

### Step 6: Onboarding Automation

```bash
#!/bin/bash
set -euo pipefail
# Large-team onboarding script

echo "=== Windsurf Team Onboarding ==="

# 1. Install Windsurf
if ! command -v windsurf &>/dev/null; then
  echo "Installing Windsurf..."
  brew install --cask windsurf 2>/dev/null || {
    echo "Download from: https://windsurf.com/download"
    exit 1
  }
fi

# 2. Import existing editor settings
echo "Importing VS Code settings..."
windsurf 2>/dev/null &  # First launch imports settings
sleep 3
kill %1 2>/dev/null || true

# 3. Install approved extensions
EXTENSIONS=(
  "esbenp.prettier-vscode"
  "dbaeumer.vscode-eslint"
  "biomejs.biome"
)
for ext in "${EXTENSIONS[@]}"; do
  windsurf --install-extension "$ext" 2>/dev/null
done

# 4. Disable conflicting extensions
CONFLICTS=("github.copilot" "tabnine.tabnine-vscode")
for ext in "${CONFLICTS[@]}"; do
  windsurf --disable-extension "$ext" 2>/dev/null || true
done

# 5. Set team config
echo "Configuring team settings..."
echo ""
echo "Complete. Next steps:"
echo "1. Open your service directory in Windsurf (not monorepo root)"
echo "2. Sign in with company SSO when prompted"
echo "3. Verify .devin/rules/project.md exists in your service directory"
```

## Output

Deliver a phased rollout plan with cohorts, repository and indexing boundaries, identity and seat ownership, policy distribution, adoption and reliability measures, support escalation, stop conditions, and rollback criteria. Include a pilot exit decision before broader deployment.

## Error Handling

| Issue | Cause | Solution |
|-------|-------|----------|
| Indexing slow across team | Large workspaces | Partition into sub-workspaces per service |
| Config drift between services | No central templates | Implement sync-config.sh script |
| Variable usage overspend | No spending limit | Set an approved limit and review seat allocation quarterly |
| Network blocking Windsurf | Firewall rules | Whitelist *.codeium.com and*.windsurf.com |
| Inconsistent AI suggestions | Different .devin/rules/project.md | Use central template repository |

## Examples

### Quick Team Health Dashboard

```bash
echo "=== Team Windsurf Health ==="
echo "Services with .devin/rules/project.md:"
find . -maxdepth 3 -name ".devin/rules/project.md" | wc -l
echo "Services with .codeiumignore:"
find . -maxdepth 3 -name ".codeiumignore" | wc -l
echo "Services without config (needs fix):"
for d in apps/* services/*; do
  [ -d "$d" ] || continue
  [ -f "$d/.devin/rules/project.md" ] || echo "  MISSING: $d/.devin/rules/project.md"
done
```

## Resources

- [Focused first-party references](references/official-docs.md)
- [Windsurf Enterprise](https://windsurf.com/enterprise)
- [Windsurf Admin Guide](https://docs.devin.ai/desktop/guide-for-admins)

## Related Skill

Continue with `windsurf-reliability-patterns` to add checkpoints, validation gates, rollback paths, and failure containment to the scaled rollout.
