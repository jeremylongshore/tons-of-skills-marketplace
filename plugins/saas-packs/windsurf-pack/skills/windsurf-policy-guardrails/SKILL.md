---
name: windsurf-policy-guardrails
description: 'Implement team-wide Devin Desktop (formerly Windsurf) usage policies, code quality gates, and
  Cascade guardrails.

  Use when setting up code review policies for AI-generated code, configuring Turbo
  mode

  safety controls, or implementing CI gates for Cascade output.

  Trigger with phrases like "windsurf policy", "windsurf guardrails",

  "cascade safety rules", "windsurf team rules", "AI code policy".

  '
allowed-tools: Read, Write, Edit, Bash(npx:*)
argument-hint: "[scope or requirements]"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- windsurf
- policy
- guardrails
- team-management
compatibility: Designed for Claude Code
---
# Windsurf Policy Guardrails

## Overview

Policy guardrails for team Windsurf usage: controlling what Cascade can do, enforcing code review for AI output, configuring terminal safety controls, and preventing common AI coding mistakes.

## Prerequisites

- Windsurf configured for team use
- Git workflow established
- CI/CD pipeline in place
- Team agreement on AI usage standards

## Tool Use

- Use `Read` to inspect only the repository files and configuration needed for the request.
- Use `Write` only for a new artifact the user requested; never write credentials or unreviewed production configuration.
- Use `Edit` for bounded, reviewable changes and preserve unrelated user work.
- Use only the command-scoped `Bash` entries declared in frontmatter, with non-destructive checks before mutations.

## Instructions

### Step 1: Terminal Command Safety (Turbo Mode Controls)

Configure what Cascade can and cannot auto-execute:

```json
// settings.json — Team-wide terminal safety
{
  "windsurf.cascadeCommandsAllowList": [
    "npm test", "npm run", "npx vitest", "npx tsc",
    "git status", "git diff", "git log", "git add",
    "eslint", "prettier", "biome",
    "ls", "cat", "head", "tail", "wc", "grep"
  ],
  "windsurf.cascadeCommandsDenyList": [
    "rm -rf", "rm -r /",
    "sudo",
    "git push --force", "git reset --hard",
    "DROP TABLE", "DELETE FROM", "TRUNCATE",
    "curl | bash", "wget | sh",
    "chmod 777",
    "kill -9",
    "shutdown", "reboot", "halt",
    "mkfs", "dd if=",
    "npm publish", "npx publish"
  ]
}
```

### Step 2: Workspace Isolation Rules

Prevent Cascade from accessing sensitive directories:

```gitignore
# .codeiumignore — security boundary
# AI cannot see or modify files matching these patterns

# Credentials
.env
.env.*
credentials/
secrets/
*.pem
*.key

# Infrastructure
terraform.tfstate*
*.tfvars
ansible/vault*

# Customer data
data/production/
exports/
```

```markdown
<!-- .devin/rules/protected-files.md -->
---
trigger: always_on
---
## Protected Files Policy
- NEVER modify files in migrations/ without explicit request
- NEVER modify Dockerfile or docker-compose.yml without explicit request
- NEVER modify CI/CD workflows (.github/workflows/) without explicit request
- NEVER modify package.json dependencies without explicit request
- ALWAYS ask before changing database schema files
```

### Step 3: AI Code Review Policy

```yaml
# .github/workflows/ai-code-gate.yml
name: AI Code Quality Gate
on: pull_request

jobs:
  ai-review-gate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }

      - name: Check cascade commit policy
        run: |
          # Count files changed
          FILES=$(git diff --name-only origin/main..HEAD | wc -l)

          # Large changesets need explicit review
          if [ "$FILES" -gt 15 ]; then
            echo "::warning::Large changeset ($FILES files modified)."
            echo "If AI-generated, ensure line-by-line review."
          fi

          # New files must have tests
          NEW_SRC=$(git diff --name-only --diff-filter=A origin/main..HEAD | grep -cE '\.(ts|js)$' || true)
          NEW_TEST=$(git diff --name-only --diff-filter=A origin/main..HEAD | grep -cE '\.(test|spec)\.' || true)
          if [ "$NEW_SRC" -gt 3 ] && [ "$NEW_TEST" -eq 0 ]; then
            echo "::error::$NEW_SRC new source files without tests."
            echo "Add tests before merging AI-generated code."
            exit 1
          fi

      - name: Scan for hardcoded secrets
        run: |
          SECRETS_FOUND=$(git diff origin/main..HEAD | grep -cE '(sk_live|sk_test|AKIA[A-Z0-9]|ghp_|glpat-|xoxb-)' || true)
          if [ "$SECRETS_FOUND" -gt 0 ]; then
            echo "::error::Potential hardcoded secret detected in diff."
            exit 1
          fi
```

### Step 4: Team Cascade Usage Guidelines

```markdown
<!-- docs/windsurf-policy.md — committed to repo -->

# Team Windsurf AI Usage Policy

## Required Practices
1. **Git before Cascade** — commit or stash before every Cascade session
2. **Feature branches only** — never use Cascade on main or develop
3. **Review every diff** — accept changes file-by-file, not "accept all"
4. **Test after accepting** — run tests before committing Cascade changes
5. **Tag AI commits** — prefix with `[cascade]` for traceability

## Prohibited Actions
1. Never paste secrets, API keys, or passwords into Cascade chat
2. Never let Cascade modify production config without manual review
3. Never use Cascade to write security-critical code without expert review
4. Never accept Cascade suggestions for database migrations without DBA review
5. Never use Turbo mode with commands not in the allow list

## Code Review Standards for AI-Generated Code
- Reviewer MUST verify logic, not just syntax
- Reviewer MUST check edge cases (AI often misses boundary conditions)
- Reviewer MUST verify error handling (AI tends to happy-path)
- Reviewer MUST check for AI-specific patterns: unnecessary abstraction,
  over-engineering, cargo-cult patterns from training data

## Accountability
- The developer who accepts and commits AI-generated code is responsible
- "Cascade wrote it" is not an excuse for bugs in production
- All standard code review requirements apply to AI-generated code
```

### Step 5: Extension Trust Policy

```json
// .vscode/extensions.json (works in Windsurf)
{
  "recommendations": [
    "esbenp.prettier-vscode",
    "dbaeumer.vscode-eslint",
    "biomejs.biome"
  ],
  "unwantedRecommendations": [
    "github.copilot",
    "github.copilot-chat",
    "tabnine.tabnine-vscode",
    "sourcegraph.cody-ai"
  ]
}
```

### Step 6: Pre-Cascade Checklist Workflow

```markdown
<!-- .windsurf/workflows/safe-cascade.md -->
---
name: safe-cascade
description: Pre-flight checks before Cascade work
---
// turbo-all

1. Run `git status` — verify clean working tree
2. Run `git checkout -b cascade/$(date +%Y%m%d-%H%M%S)` — new branch
3. Run `git log --oneline -3` — note recent context
4. Report: "Ready for Cascade. Branch created. Clean working tree."
5. Ask: "What would you like Cascade to do?"
```

## Output

Deliver a version-controlled policy package covering Rules or `AGENTS.md`, Hooks, MCP allowlists, protected paths, review gates, exception ownership, audit evidence, and rollout communication. Product prompts supplement—not replace—repository permissions and CI enforcement.

## Error Handling

| Issue | Cause | Solution |
|-------|-------|----------|
| Cascade modifies secrets | Files not in .codeiumignore | Add to .codeiumignore, rotate exposed secret |
| Untested AI code merged | No CI gate | Add test-required check to PR |
| Conflicting suggestions | Multiple AI extensions | Remove competing extensions |
| Developer bypasses policy | No enforcement | Add CI gates, team training |
| Cascade runs destructive command | Not in deny list | Add to cascadeCommandsDenyList |

## Examples

### Quick Policy Verification

```bash
set -euo pipefail
echo "=== Policy Compliance Check ==="
echo "Branch protection: $(gh api repos/:owner/:repo/branches/main/protection --jq '.required_status_checks.contexts | length' 2>/dev/null || echo 'N/A') checks"
echo ".codeiumignore: $([ -f .codeiumignore ] && echo 'EXISTS' || echo 'MISSING')"
echo "Policy doc: $([ -f docs/windsurf-policy.md ] && echo 'EXISTS' || echo 'MISSING')"
echo "Extension control: $([ -f .vscode/extensions.json ] && echo 'EXISTS' || echo 'MISSING')"
```

## Resources

- [Focused first-party references](references/official-docs.md)
- [Windsurf Terminal Docs](https://docs.devin.ai/desktop/terminal)
- [Windsurf Rules](https://docs.devin.ai/desktop/cascade/memories)
- [Windsurf Admin Guide](https://docs.devin.ai/desktop/guide-for-admins)

## Related Skill

Continue with `windsurf-architecture-variants` to place these controls at the correct repository, service, language, and organization boundaries.
