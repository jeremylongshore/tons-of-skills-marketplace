---
name: windsurf-incident-runbook
description: 'Execute Devin Desktop (formerly Windsurf) incident response when AI features fail or cause production
  issues.

  Use when Cascade breaks code, Windsurf service is down, AI-generated code causes

  production incidents, or team needs emergency Windsurf troubleshooting.

  Trigger with phrases like "windsurf incident", "windsurf outage",

  "windsurf broke production", "cascade caused bug", "windsurf emergency".

  '
allowed-tools: Read, Grep, Bash(git:*), Bash(curl:*)
argument-hint: "[scope or requirements]"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- windsurf
- incident-response
- runbook
- troubleshooting
compatibility: Designed for Claude Code
---
# Windsurf Incident Runbook

## Overview

Incident response procedures for Windsurf-related issues: Cascade service outages, AI-generated code causing bugs, and team workflow disruptions.

## Prerequisites

- Access to Windsurf dashboard and status page
- Git access to affected repositories
- Team communication channel (Slack, Teams)

## Tool Use

- Use `Read` to inspect only the repository files and configuration needed for the request.
- Use `Grep` to locate relevant settings, rules, logs, or code without broad collection.
- Use only the command-scoped `Bash` entries declared in frontmatter, with non-destructive checks before mutations.

## Instructions

1. Classify severity and assign an incident commander.
2. Preserve evidence, stop unsafe automation, and check the official service status.
3. Use the matching playbook below; prefer a reviewed revert through the protected delivery path.
4. Validate recovery with production health signals and record follow-up owners.

## Severity Levels

| Level | Definition | Response Time | Examples |
|-------|------------|---------------|----------|
| P1 | Production broken by AI code | < 15 min | Cascade-generated code deployed with critical bug |
| P2 | Team workflow blocked | < 1 hour | Windsurf service outage, all Cascade down |
| P3 | Degraded AI features | < 4 hours | Slow Cascade, Supercomplete intermittent |
| P4 | Minor inconvenience | Next business day | Specific model unavailable, feature regression |

## Quick Triage Decision Tree

```
Is Windsurf service itself down?
├─ YES: Check https://status.windsurf.com
│   ├─ Status page shows incident → WAIT for Windsurf to resolve
│   │   Action: Switch to manual coding, notify team
│   └─ Status page green → Local issue
│       Action: Restart Windsurf, check internet, re-authenticate
│
└─ NO: Did AI-generated code cause a production issue?
    ├─ YES → P1 INCIDENT
    │   1. Revert the deployment immediately
    │   2. Identify the Cascade-generated commit(s)
    │   3. Fix manually or with targeted Cascade prompt
    │   4. Post-incident: update review policy
    │
    └─ NO: Is Cascade giving bad suggestions?
        ├─ YES → Check .devin/rules/project.md, start fresh Cascade session
        └─ NO → See windsurf-common-errors
```

## P1 Playbook: AI Code Caused Production Bug

### Step 1: Immediate Mitigation

```bash
set -euo pipefail
# Revert the deployment
git log --oneline -10  # Find the bad commit(s)

# On a dedicated incident branch created through the normal repository process:
git revert HEAD --no-edit  # Revert the confirmed bad commit
git status --short

# If multiple Cascade commits:
git revert --no-commit HEAD~3..HEAD  # Revert last 3 commits
git commit -m "revert: undo cascade changes causing [issue]"
# Push the incident branch and use the protected emergency PR/deploy lane.
```

### Step 2: Identify Root Cause

```bash
# Find all Cascade-generated commits
git log --all --oneline --grep="cascade" --since="1 week ago"
git log --all --oneline --grep="\[cascade\]" --since="1 week ago"

# Compare before/after
git diff [last-good-commit]..HEAD -- src/

# Common root causes:
# 1. Cascade modified shared utility used by many modules
# 2. Cascade changed error handling (swallowed exceptions)
# 3. Cascade "optimized" code that had intentional behavior
# 4. Cascade introduced dependency on newer API version
```

### Step 3: Fix and Validate

```bash
set -euo pipefail
git checkout -b fix/cascade-revert
# Make targeted fix
npm test
npm run typecheck
# Deploy to staging first
```

## P2 Playbook: Windsurf Service Outage

### Step 1: Confirm and Communicate

```bash
# Check Windsurf status
curl -sf https://status.windsurf.com || echo "Status page unreachable"
```

### Step 2: Team Notification

```
Team notification template:

Windsurf AI features are currently unavailable.
Status: https://status.windsurf.com

Impact: Cascade and Supercomplete are not working.
Workaround: Continue coding manually. Windsurf still works as a
standard VS Code editor — only AI features are affected.

ETA: Monitoring status page for updates.
```

### Step 3: Workarounds During Outage

```markdown
1. Windsurf still works as VS Code (file editing, terminal, git)
2. Extensions still work (ESLint, Prettier, debugger)
3. Only Cascade, Supercomplete, and Command mode are down
4. Continue coding manually until service restores
5. Do NOT switch to a different editor mid-task (context loss)
```

## P3 Playbook: Degraded AI Features

```markdown
Symptoms and fixes:

Slow Cascade → Start fresh session, reduce workspace size
No Supercomplete → Check status bar widget, verify enabled
Wrong model → Check quota and policy state, then select an available model
MCP disconnected → Restart MCP servers (Command Palette)
Indexing stuck → Download diagnostics, then use the current indexing reset control
```

## Post-Incident Actions

### Evidence Collection

```bash
set -euo pipefail
# Collect relevant data
mkdir incident-$(date +%Y%m%d)
git log --since="1 day ago" --stat > incident-$(date +%Y%m%d)/commits.txt
cp .devin/rules/project.md incident-$(date +%Y%m%d)/ 2>/dev/null || true
# See windsurf-debug-bundle for full diagnostic collection
```

### Postmortem Template

```markdown
## Incident: [Title]
**Date:** YYYY-MM-DD
**Duration:** X hours Y minutes
**Severity:** P[1-4]

### Summary
[1-2 sentence description]

### Timeline
- HH:MM — [Event]
- HH:MM — [Event]

### Root Cause
[Was this an AI-generated code issue? Windsurf service issue? Config issue?]

### What Went Wrong
- [ ] AI-generated code not reviewed thoroughly
- [ ] Missing tests for AI-modified code
- [ ] .devin/rules/project.md didn't prevent the bad pattern
- [ ] Cascade modified shared code without constraint

### Action Items
- [ ] Update .devin/rules/project.md to prevent this pattern
- [ ] Add test coverage for affected module
- [ ] Update team Cascade usage policy
- [ ] Add CI gate for AI-modified code
```

## Output

Maintain an incident record with severity, commander, timeline, affected revision, containment action, recovery evidence, customer impact, and follow-up owners. Never place credentials or sensitive source in the record, and never bypass protected-branch controls for speed.

## Error Handling

| Issue | Immediate Action | Long-Term Fix |
|-------|-----------------|---------------|
| AI code in prod broke feature | Git revert + redeploy | Enforce test gates for Cascade commits |
| Windsurf service down | Code manually | No action needed — external service |
| AI modified protected files | Git revert those files | Add to .codeiumignore |
| Team lost work from Cascade | Recover from git history | Enforce pre-Cascade git commit policy |

## Examples

### Quick Health Check

```bash
curl -sf https://status.windsurf.com | head -5 || echo "WINDSURF STATUS UNREACHABLE"
```

### Find Recent Cascade Commits

```bash
git log --all --oneline --since="7 days ago" | grep -i cascade
```

## Resources

- [Focused first-party references](references/official-docs.md)
- [Windsurf Status Page](https://status.windsurf.com)
- [Windsurf GitHub Issues](https://windsurf.com/support)

## Related Skill

Continue with `windsurf-data-handling` when the incident involves sensitive context, retention questions, diagnostic evidence, or regulated-data exposure.
