---
name: windsurf-prod-checklist
description: 'Execute Devin Desktop (formerly Windsurf) production readiness checklist for team and enterprise
  deployments.

  Use when rolling out Windsurf to a team, preparing for enterprise deployment,

  or auditing production configuration.

  Trigger with phrases like "windsurf production", "windsurf team rollout",

  "windsurf go-live", "windsurf enterprise deploy", "windsurf checklist".

  '
allowed-tools: Read, Grep
argument-hint: "[scope or requirements]"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- windsurf
- deployment
- enterprise
- checklist
compatibility: Designed for Claude Code
---
# Windsurf Production Checklist

## Overview

Complete checklist for rolling out Windsurf to production teams. Covers workspace configuration, security hardening, team onboarding, and monitoring.

## Prerequisites

- Windsurf plan selected (Pro, Teams, or Enterprise)
- Admin access to Windsurf dashboard
- Git repositories identified for rollout
- Team agreement on AI usage policy

## Tool Use

- Use `Read` to inspect only the repository files and configuration needed for the request.
- Use `Grep` to locate relevant settings, rules, logs, or code without broad collection.

## Instructions

### Step 1: Complete Pre-Deployment Configuration

**Workspace Config (per repository):**

- [ ] `.devin/rules/project.md` created with project stack, patterns, and constraints
- [ ] `.codeiumignore` excludes secrets, build artifacts, and large binaries
- [ ] `.devin/rules/` contains glob-triggered rules for file-type-specific patterns
- [ ] Workspace settings committed to `.windsurf/settings.json`

**Security:**

- [ ] Telemetry configured per company policy
- [ ] `.codeiumignore` covers all secret file patterns
- [ ] Autocomplete disabled for secret-containing file types (.env, .key)
- [ ] Enterprise: SSO/SAML configured and enforced
- [ ] Enterprise retention and training-use terms verified against the current contract

**Team Policy:**

- [ ] AI usage policy document created and shared
- [ ] Commit convention for AI-generated code established (e.g., `[cascade]` prefix)
- [ ] Code review requirements for AI-generated changes defined
- [ ] Competing AI extensions disabled (Copilot, TabNine)

### Step 2: Complete Team Onboarding

**Per-Developer Setup:**

```bash
#!/bin/bash
# scripts/setup-windsurf.sh — run on each developer machine

echo "Setting up Windsurf for this project..."

# Verify Windsurf is installed
windsurf --version || { echo "Install Windsurf first: https://windsurf.com/download"; exit 1; }

# Verify config files exist
[ -f .devin/rules/project.md ] || echo "WARNING: .devin/rules/project.md missing"
[ -f .codeiumignore ] || echo "WARNING: .codeiumignore missing"

# Install recommended extensions
windsurf --install-extension esbenp.prettier-vscode
windsurf --install-extension dbaeumer.vscode-eslint

# Disable conflicting extensions
windsurf --disable-extension github.copilot 2>/dev/null || true

echo "Setup complete. Open project folder (not monorepo root) for best AI context."
```

**Training Checklist:**

- [ ] Demo: Supercomplete (Tab) vs Cascade (Cmd+L) vs Command (Cmd+I)
- [ ] Demo: Code mode vs Chat mode
- [ ] Demo: @ mentions for file context
- [ ] Demo: Turbo mode with allow/deny lists
- [ ] Demo: Previews for UI development
- [ ] Demo: Git checkpoint before Cascade workflow
- [ ] Share: `.devin/rules/project.md` explained
- [ ] Share: Daily/weekly quota, extra usage, and model selection

### Step 3: Establish Monitoring and Optimization

**Admin Dashboard Monitoring:**

```yaml
# Metrics to track weekly (Admin Dashboard > Analytics)
metrics:
  adoption:
    - active_users_vs_total_seats    # compare with organization-defined target
    - daily_active_users             # trend: increasing
  quality:
    - completion_acceptance_rate     # baseline before setting a target
    - cascade_success_rate           # baseline before setting a target
  efficiency:
    - included_vs_on_demand_usage    # review with authorized billing owner
    - tasks_completed_per_day        # proxy for productivity
```

**Quarterly Review:**

- [ ] Audit seat utilization -- downgrade inactive seats
- [ ] Review `.devin/rules/project.md` -- update with new patterns
- [ ] Check for new Windsurf features in changelog
- [ ] Survey team satisfaction and pain points
- [ ] Analyze quota and on-demand usage patterns

### Step 4: Prove the Rollback Procedure

If Windsurf causes issues:

```
1. Disable Cascade for team: Admin Dashboard > Features > Cascade > Off
2. Developers can still use Supercomplete (non-agentic)
3. Switch to manual coding while investigating
4. Review recent Cascade-generated commits for issues
5. File support ticket with debug bundle (see windsurf-debug-bundle)
```

## Output

Return a signed readiness checklist with evidence for identity, repository access, data boundaries, policy controls, pilot results, support ownership, usage monitoring, incident response, and rollback. List every incomplete item with an owner and due date.

## Error Handling

| Issue | Severity | Mitigation |
|-------|----------|------------|
| Cascade generates broken code | Medium | Enforce tests-pass-before-merge policy |
| AI exposes secrets in suggestions | High | Audit `.codeiumignore`, rotate exposed secrets |
| Team not adopting | Low | Training session, share productivity data |
| Quota exhausted mid-sprint | Medium | Check reset timing and use approved extra usage or lower-cost models |

## Examples

### Recommended Extension Set

```json
// .vscode/extensions.json (also works in Windsurf)
{
  "recommendations": [
    "esbenp.prettier-vscode",
    "dbaeumer.vscode-eslint",
    "biomejs.biome"
  ],
  "unwantedRecommendations": [
    "github.copilot",
    "tabnine.tabnine-vscode"
  ]
}
```

### Quick Compliance Check

```bash
set -euo pipefail
echo "Config: $([ -f .devin/rules/project.md ] && echo 'OK' || echo 'MISSING')"
echo "Ignore: $([ -f .codeiumignore ] && echo 'OK' || echo 'MISSING')"
echo "Rules:  $([ -d .devin/rules ] && echo 'OK' || echo 'MISSING')"
```

## Resources

- [Focused first-party references](references/official-docs.md)
- [Windsurf Admin Guide](https://docs.devin.ai/desktop/guide-for-admins)
- [Windsurf Enterprise](https://windsurf.com/enterprise)
- [Windsurf Security](https://windsurf.com/security)

## Related Skill

Continue with `windsurf-upgrade-migration` to preserve these production controls through editor, extension, configuration, and policy changes.
