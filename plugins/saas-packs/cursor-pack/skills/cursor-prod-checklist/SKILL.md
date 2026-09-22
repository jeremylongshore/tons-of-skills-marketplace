---
name: cursor-prod-checklist
description: 'Production readiness checklist for Cursor IDE setup: security, rules,
  indexing, privacy, and team

  standards. Triggers on "cursor production", "cursor ready", "cursor checklist",
  "optimize cursor setup",

  "cursor onboarding".

  '
allowed-tools: Read, Write, Edit, Bash(cmd:*)
version: 1.19.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- cursor
- cursor-prod
compatibility: Designed for Claude Code
---
# Cursor Production Checklist

## Overview

Use this gate before enabling Cursor for a production repository or team workflow. It verifies governance, context controls, review, and incident ownership—not the correctness of any generated code.

## Prerequisites

- A named repository/tenant owner, data classification, and approved privacy/model policy.
- Reviewed rules/ignore files, identity controls, and a rollback path for tenant configuration.

## Instructions

1. Complete each control with evidence: privacy setting, access model, exclusions, rules, review, tests, and support route.
2. Pilot in a representative non-sensitive repository and verify expected context boundaries.
3. Hold production enablement when any security, identity, data, or ownership gate is unverified.
4. Record the go/no-go decision and schedule periodic access/rule review.

## Output

- A production-readiness record with owner, evidence links, exceptions, and verification date.

## Error Handling

| Failed gate | Required action |
|---|---|
| Privacy or data routing unclear | Block enablement and obtain a documented security/privacy decision. |
| Excluded path appears in context | Stop pilot, repair exclusions, and assess exposure. |
| Review/test workflow is absent | Do not enable use for production changes. |

## Examples

Pilot one repository with Privacy Mode, SSO, reviewed `.cursorignore`, and a pull-request review requirement. Verify a sample sensitive path cannot be added to context before signing off the production checklist.

Comprehensive checklist for configuring Cursor IDE for production use. Covers security hardening, project rules, indexing optimization, privacy settings, and team standardization.

## Pre-Flight Checklist

### Authentication & Licensing

```
[ ] All team members authenticated with correct plan (Pro/Business/Enterprise)
[ ] SSO configured (Business/Enterprise) -- see cursor-sso-integration skill
[ ] Privacy Mode enabled (enforced at team level for Business+)
[ ] Verify plan at cursor.com/settings
```

### Project Rules

```
[ ] .cursor/rules/ directory created and committed to git
[ ] Core project rule with alwaysApply: true (stack, conventions, standards)
[ ] Language-specific rules with glob patterns (*.ts, *.py, etc.)
[ ] Security rule: "Never suggest hardcoded credentials or secrets"
[ ] No sensitive data (API keys, passwords) in any rule file
```

**Minimum viable rule set:**

```yaml
# .cursor/rules/project.mdc
---
description: "Core project context"
globs: ""
alwaysApply: true
---
# Project: [Name]
Stack: [framework, language, database, etc.]
Package manager: [npm/pnpm/yarn]

## Conventions
- [your team conventions here]
- Never commit console.log statements
- All functions require TypeScript return types
- Use Conventional Commits format
```

```yaml
# .cursor/rules/security.mdc
---
description: "Security constraints for AI-generated code"
globs: ""
alwaysApply: true
---
# Security Rules
- NEVER hardcode API keys, passwords, or secrets in code
- NEVER disable HTTPS/TLS verification
- ALWAYS use parameterized queries (no string concatenation for SQL)
- ALWAYS validate and sanitize user input
- Use environment variables for all configuration values
```

### Indexing Configuration

```
[ ] .cursorignore created at project root
[ ] Excluded: node_modules/, dist/, build/, .next/, vendor/
[ ] Excluded: *.min.js, *.map, *.lock, *.sqlite
[ ] Excluded: .env*, secrets/, credentials/
[ ] .cursorindexingignore created for large-but-useful files
[ ] Verified indexing completes (status bar shows "Indexed")
[ ] Tested @Codebase queries return relevant results
```

### Privacy & Security

```
[ ] Privacy Mode: ON (Cursor Settings > General > Privacy Mode)
[ ] Verified: cursor.com/settings shows "Privacy Mode: Enabled"
[ ] .cursorignore covers all files with PII or regulated data
[ ] API keys (if BYOK) stored in Cursor settings, NOT in project files
[ ] Team members briefed: AI output is a draft, not production-ready code
```

### AI Configuration

```
[ ] Default model set (Cursor Settings > Models)
[ ] BYOK configured if required by team (see cursor-api-key-management skill)
[ ] Auto mode evaluated vs fixed model selection
[ ] Tab completion enabled and tested
[ ] Conflicting extensions disabled (Copilot, TabNine, Codeium)
```

### Version Control Integration

```
[ ] .cursor/rules/ committed to git (team shares rules)
[ ] .cursorignore committed to git
[ ] .cursorindexingignore committed to git
[ ] AI-generated commit messages reviewed before pushing
[ ] Pre-commit hooks run (linting, tests) regardless of AI-generated code
```

## Team Onboarding Template

```markdown
# Cursor IDE Onboarding

## Setup (15 minutes)
1. Download Cursor from cursor.com/download
2. Sign in with your @company.com email (SSO will redirect)
3. Open our project repository in Cursor
4. Wait for indexing to complete (status bar)

## Daily Workflow
- Cmd+L (Chat): Ask questions, plan features
- Cmd+K (Inline Edit): Fix/refactor selected code
- Cmd+I (Composer): Multi-file changes
- Tab: Accept AI completions while typing

## Our Rules
- Project rules are in .cursor/rules/ -- read them
- Always review AI-generated code before committing
- Start new chats for new tasks (don't continue stale conversations)
- Use @Files for specific context, @Codebase for discovery

## Prohibited
- Do NOT paste credentials into Chat/Composer
- Do NOT disable Privacy Mode
- Do NOT commit AI-generated code without review and testing
```

## Maintenance Schedule

| Task | Frequency | How |
|------|-----------|-----|
| Review and update project rules | Monthly | Audit `.cursor/rules/` for stale info |
| Verify Privacy Mode enforcement | Quarterly | Admin dashboard or Cursor Settings |
| Rotate API keys (BYOK) | Quarterly | Provider console + Cursor Settings |
| Update .cursorignore | When project structure changes | Add new build/data directories |
| Review extension list | Monthly | Disable unused, check for conflicts |
| Cursor version update | As released | Help > Check for Updates |
| Team onboarding doc update | When workflow changes | Keep setup steps current |

## Production Anti-Patterns

| Anti-Pattern | Risk | Fix |
|-------------|------|-----|
| No .cursor/rules/ | AI generates inconsistent code | Create rules with team conventions |
| No .cursorignore | Secrets indexed, large files slow indexing | Add comprehensive ignore patterns |
| Privacy Mode off | Code stored by model providers | Enable at team level (admin dashboard) |
| One giant conversation | Context overflow, bad suggestions | Start new chat per task |
| Blind "Apply All" | Bugs, wrong patterns committed | Review every diff before applying |
| No pre-commit hooks | AI-generated bugs reach main branch | Enforce lint + test hooks |

## Enterprise Considerations

- **Compliance documentation**: Maintain records of Cursor configuration for SOC 2 / ISO 27001 audits
- **Change management**: Treat `.cursor/rules/` changes like infrastructure changes -- PR and review
- **Access reviews**: Quarterly review of team membership and seat assignments
- **Data classification**: Map .cursorignore to your data classification policy

## Resources

- [Cursor Enterprise](https://cursor.com/enterprise)
- [Privacy and Data Governance](https://docs.cursor.com/enterprise/privacy-and-data-governance)
- [Security Page](https://cursor.com/security)
