---
name: agent-patterns
description: 'Execute this skill should be used when the user asks about "SPAWN REQUEST
  format", "agent reports", "agent coordination", "parallel agents", "report format",
  "agent communication", or needs to understand how agents coordinate within the sprint
  system. Use when appropriate context detected. Trigger with relevant phrases based
  on skill purpose.

  '
allowed-tools: Read
version: 1.21.0
author: Damien Laine <damien.laine@gmail.com>
license: MIT
tags:
- community
- agent-patterns
compatibility: Designed for Claude Code
---
# Agent Patterns

## Overview

Agent Patterns defines the coordination protocol for multi-agent sprint execution within the Sprint plugin. It governs how the project architect spawns implementation and testing agents, how agents communicate results via structured reports, and how parallel agents avoid conflicts.

## Prerequisites

- Sprint plugin installed and configured (`/plugin install sprint`)
- Sprint directory initialized at `.claude/sprint/[N]/`
- `specs.md` written with clear scope and testing configuration
- Familiarity with the sprint phase lifecycle (see the `sprint-workflow` skill)

## Instructions

1. Structure every agent spawn using the SPAWN REQUEST format. Include the agent name, the specification file it should read, and any scope constraints:

   ```
   SPAWN REQUEST
   Agent: python-dev
   Specs: .claude/sprint/1/backend-specs.md
   Contract: .claude/sprint/1/api-contract.md
   Scope: Authentication endpoints only
   ```

2. Ensure each spawned agent receives only the files relevant to its scope. Pass the `api-contract.md` as a shared interface so backend and frontend agents stay synchronized.
3. Collect structured reports from every agent upon completion. Each report must include: work completed, files modified, tests added, and conformity status against the specification.
4. When running agents in parallel, partition work by domain boundary (e.g., backend vs. frontend vs. CI/CD). Never assign overlapping file paths to concurrent agents.
5. Feed agent reports back to the project architect for review. The architect decides whether to iterate (re-spawn with narrowed specs) or advance to the next phase.
6. For testing agents, pass the UI test report format shown in `${CLAUDE_SKILL_DIR}/references/ui-test-report.md` so results follow a consistent schema including test counts, coverage, failures, and console errors.

## Output

- SPAWN REQUEST blocks consumed by the sprint orchestrator to launch agents
- Structured agent reports containing: summary, files changed, test results, and conformity status
- UI test reports with pass/fail counts, coverage details, failure descriptions, and console error logs
- Updated `status.md` reflecting completed and remaining work after each iteration

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Agent receives wrong specification file | Incorrect path in SPAWN REQUEST | Verify the sprint directory number and file name before spawning |
| Overlapping file modifications from parallel agents | Scope boundaries not clearly defined | Partition work by domain; assign distinct directories to each agent |
| Agent report missing required fields | Agent instructions lack report format | Include the structured report template in the agent prompt |
| Infinite iteration loop | Specs never fully satisfied | Check `status.md` for blocking issues; the orchestrator pauses after 5 iterations |
| Agent not found | Misspelled agent name in SPAWN REQUEST | Verify agent markdown files exist in `agents/` directory |

## Examples

**Spawning parallel implementation agents:**

```
SPAWN REQUEST
Agent: python-dev
Specs: .claude/sprint/1/backend-specs.md
Contract: .claude/sprint/1/api-contract.md

SPAWN REQUEST
Agent: nextjs-dev
Specs: .claude/sprint/1/frontend-specs.md
Contract: .claude/sprint/1/api-contract.md
```

Both agents share the same `api-contract.md` to ensure API compatibility.

**Structured agent report format:**

```
AGENT REPORT
Agent: python-dev
Status: COMPLETE
Files Modified: src/auth/routes.py, src/auth/models.py, tests/test_auth.py
Tests: 12 passed, 0 failed
Conformity: All backend-specs requirements implemented
Notes: JWT token expiry set to 24h per spec
```

**Testing agent coordination:**

```
SPAWN REQUEST
Agent: qa-test-agent
Specs: .claude/sprint/1/specs.md
Run After: python-dev, nextjs-dev

SPAWN REQUEST
Agent: ui-test-agent
Specs: .claude/sprint/1/specs.md
Run After: qa-test-agent
```

## Resources

- `${CLAUDE_SKILL_DIR}/references/ui-test-report.md` -- Structured UI test report format with coverage and failure tracking
- Sprint workflow skill for phase lifecycle context
- API contract skill for shared interface design
- Sprint plugin README for agent architecture overview
