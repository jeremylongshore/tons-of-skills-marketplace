# Devin Desktop / Windsurf Skill Pack

> Operate Devin Desktop (the current name for Windsurf) with Cascade, agent management, Rules, Skills, Workflows, Hooks, MCP, and enterprise controls (30 skills)

Devin Desktop is the new name for Windsurf. Existing plans, settings, extensions, workflows, and in-progress work carry forward through the product update. The `windsurf-*` names remain stable for marketplace discovery and backward compatibility while the guidance tracks current Devin Desktop documentation.

## Installation

```bash
/plugin install windsurf-pack@claude-code-plugins-plus
```

## Skills Included

### Standard Skills (S01-S12)

| Skill | What It Does |
|-------|-------------|
| `windsurf-install-auth` | Install Devin Desktop, authenticate, choose an organization, and verify Cascade |
| `windsurf-hello-world` | First Cascade interaction, Supercomplete, Command mode, @ mentions |
| `windsurf-local-dev-loop` | Dev workflow with Turbo mode, Previews, terminal AI, .devin/rules/project.md |
| `windsurf-sdk-patterns` | .devin/rules/project.md, workspace rules with triggers, MCP server config |
| `windsurf-core-workflow-a` | Cascade Code mode: multi-file agentic coding with checkpoints |
| `windsurf-core-workflow-b` | Workflows (slash commands), Memories, reusable automation |
| `windsurf-common-errors` | Diagnose Cascade failures, Supercomplete issues, indexing problems |
| `windsurf-debug-bundle` | Collect diagnostic data for Windsurf support tickets |
| `windsurf-rate-limits` | Daily/weekly quota, extra usage, and model-cost diagnostics |
| `windsurf-security-basics` | .codeiumignore, telemetry controls, secret protection |
| `windsurf-prod-checklist` | Team rollout checklist, onboarding script, monitoring setup |
| `windsurf-upgrade-migration` | Upgrade Windsurf, migrate from VS Code or Cursor |

### Pro Skills (P13-P18)

| Skill | What It Does |
|-------|-------------|
| `windsurf-ci-integration` | CI gates for .devin/rules/project.md, AI code quality checks in GitHub Actions |
| `windsurf-deploy-integration` | Use current Netlify App Deploys or reviewed provider-specific pipelines |
| `windsurf-webhooks-events` | Build Windsurf extensions with VS Code API, event tracking |
| `windsurf-performance-tuning` | Indexing optimization, .codeiumignore, Cascade speed tuning |
| `windsurf-cost-tuning` | Full/flex seat analysis, quota governance, and variable-usage budgeting |
| `windsurf-reference-architecture` | Complete project structure optimized for Cascade AI |

### Flagship Skills (F19-F24)

| Skill | What It Does |
|-------|-------------|
| `windsurf-multi-env-setup` | Configure per-service rules, monorepo strategy, team onboarding |
| `windsurf-observability` | Admin Dashboard analytics, adoption metrics, productivity tracking |
| `windsurf-incident-runbook` | Triage AI-caused bugs, service outages, rollback procedures |
| `windsurf-data-handling` | Data boundaries, `.codeiumignore`, and evidence-based compliance review |
| `windsurf-enterprise-rbac` | SSO/SAML, RBAC, seat management, org-wide AI policies |
| `windsurf-migration-deep-dive` | Full migration from Cursor/VS Code, feature comparison, team rollout plan |

### Flagship+ Skills (X25-X30)

| Skill | What It Does |
|-------|-------------|
| `windsurf-advanced-troubleshooting` | Layer isolation, context debugging, MCP diagnostics, nuclear reset |
| `windsurf-load-scale` | 50-1000+ developer rollout, monorepo partitioning, config distribution |
| `windsurf-reliability-patterns` | Git checkpointing, incremental scoping, validation gates, team safety policy |
| `windsurf-policy-guardrails` | Terminal safety (Turbo allow/deny), code review gates, usage policies |
| `windsurf-architecture-variants` | Workspace strategies: solo, monorepo, multi-window, polyglot |
| `windsurf-known-pitfalls` | Top 10 Windsurf gotchas every developer should know |

## Key Concepts

| Windsurf Feature | What It Is |
|-----------------|------------|
| **Cascade** | Agentic AI assistant — Code mode edits files, Chat mode answers questions |
| **Supercomplete** | Intent-aware inline completions; verify current usage labeling in the product |
| **Command** | Inline code editing (Cmd/Ctrl+I) — select code, describe change |
| **`.devin/rules/*.md`** | Preferred version-controlled workspace Rules; legacy Windsurf paths remain fallbacks |
| **`AGENTS.md`** | Location-scoped, zero-frontmatter repository instructions |
| **.codeiumignore** | Files excluded from AI indexing — gitignore syntax |
| **Workflows** | Reusable multi-step automation saved as markdown, invoked via slash commands |
| **Skills** | Multi-step procedures with supporting files, invoked dynamically or by mention |
| **Memories** | Local auto-generated context; use Rules or `AGENTS.md` for durable team knowledge |
| **Previews** | In-IDE web app preview with element selection — click to send to Cascade |
| **Turbo Mode** | Auto-execute terminal commands with allow/deny safety lists |
| **Hooks** | Event-driven validation, logging, and policy enforcement around Cascade actions |
| **MCP** | Provider-authenticated external tools over stdio, Streamable HTTP, or SSE |

## Usage

Skills trigger automatically when you discuss Windsurf topics. For example:

- "Help me set up Windsurf" triggers `windsurf-install-auth`
- "Cascade is slow" triggers `windsurf-performance-tuning`
- "Deploy from Windsurf" triggers `windsurf-deploy-integration`
- "Set up Windsurf for my team" triggers `windsurf-multi-env-setup`

## License

MIT
