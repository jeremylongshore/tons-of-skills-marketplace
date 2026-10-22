---
name: sprint-workflow
description: 'Execute this skill should be used when the user asks about "how sprints
  work", "sprint phases", "iteration workflow", "convergent development", "sprint
  lifecycle", "when to use sprints", or wants to understand the sprint execution model
  and its convergent diffusion approach. Use when appropriate context detected. Trigger
  with relevant phrases based on skill purpose.

  '
allowed-tools: Read
version: 1.21.0
author: Damien Laine <damien.laine@gmail.com>
license: MIT
tags:
- community
- workflow
- sprint-workflow
compatibility: Designed for Claude Code
---
# Sprint Workflow

## Overview

Sprint Workflow describes the convergent diffusion execution model used by the Sprint plugin. A sprint progresses through six distinct phases -- from loading specifications through architectural planning, parallel implementation, testing, review, and finalization.

## Prerequisites

- Sprint plugin installed (`/plugin install sprint`)
- Project onboarded via `/sprint:setup` (creates `.claude/project-goals.md` and `.claude/project-map.md`)
- Sprint created via `/sprint:new` with a completed `specs.md`
- Understanding of the agent system (see the `agent-patterns` skill)

## Instructions

1. **Phase 0 -- Load Specifications.** The orchestrator locates the sprint directory at `.claude/sprint/[N]/`, reads `specs.md` for requirements, reads `status.md` if resuming a prior iteration, and detects the project type for framework-specific agent selection. See `${CLAUDE_SKILL_DIR}/references/sprint-phases.md` for the full phase reference.
2. **Phase 1 -- Architectural Planning.** The project-architect agent reads `project-map.md` for architecture context and `project-goals.md` for business objectives. It produces specification files (`api-contract.md`, `backend-specs.md`, `frontend-specs.md`) and returns SPAWN REQUEST blocks for implementation agents.
3. **Phase 2 -- Implementation.** The orchestrator spawns implementation agents in parallel based on the architect's SPAWN REQUEST blocks. Agents include `python-dev`, `nextjs-dev`, `cicd-agent`, and `allpurpose-agent`. Each agent reads its assigned spec files and the shared `api-contract.md`, then returns a structured report.
4. **Phase 3 -- Testing.** Testing agents execute sequentially: `qa-test-agent` runs first (API and unit tests), then `ui-test-agent` runs browser-based E2E tests. Framework-specific diagnostics agents (e.g., `nextjs-diagnostics-agent`) run in parallel with UI tests. All agents produce test reports.
5. **Phase 4 -- Review and Iteration.** The architect reviews all agent reports, analyzes conformity against specifications, updates specs (removing completed items, adding fixes for failures), and updates `status.md`. The architect then decides: spawn more implementation agents, run more tests, or finalize.
6. **Phase 5 -- Finalization.** The orchestrator writes the final `status.md` summary, ensures all spec files are in a consistent state, cleans up temporary files like `manual-test-report.md`, and signals FINALIZE to end the sprint.
7. **Convergence model.** Each iteration reduces noise: completed work is removed from specs, working code is preserved, and only failures are re-addressed. Most sprints converge within 3-5 iterations. After 5 iterations without convergence, the orchestrator pauses and prompts for manual intervention.

## Output

- Phase-by-phase execution log showing agent spawns, reports, and decisions
- Updated `status.md` after each iteration reflecting completed and remaining work
- Specification files that shrink with each iteration as requirements are satisfied
- Final `status.md` summary upon sprint completion
- FINALIZE signal to the orchestrator when all specs are satisfied

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Sprint stuck in iteration loop (hits 5 iterations) | Specs too broad or contain unresolvable conflicts | Review `status.md` for blocking issues; narrow scope or resolve conflicting requirements |
| Phase 2 agents not spawned | Architect SPAWN REQUEST missing or malformed | Verify architect agent produced valid SPAWN REQUEST blocks with correct agent names |
| Tests fail repeatedly on same issue | Implementation does not match contract | Compare agent output against `api-contract.md`; check for schema mismatches |
| Sprint cannot find specs | Wrong sprint directory number | Verify `.claude/sprint/[N]/specs.md` exists; run `/sprint:new` if needed |
| Architect skips testing phase | Testing section missing from `specs.md` | Add `QA: required` and `UI Testing: required` to the specs (see `spec-writing` skill) |

## Examples

**Starting a new sprint:**

```bash
/sprint:new       # Creates .claude/sprint/1/specs.md
# Edit specs.md with requirements
/sprint           # Executes the full phase lifecycle
```

**Resuming after iteration pause:**

```bash
# Review .claude/sprint/1/status.md for blockers
# Adjust specs.md to narrow scope or fix conflicts
/sprint           # Resumes from Phase 0, reads updated specs and status
```

**Typical convergence flow:**

```
Iteration 1: Architect plans → 3 agents implement → tests find 2 failures
Iteration 2: Architect narrows specs to 2 fixes → agents patch → tests pass
Iteration 3: All specs satisfied → FINALIZE
```

## Resources

- `${CLAUDE_SKILL_DIR}/references/sprint-phases.md` -- Detailed reference for all six phases with agent assignments and handoff rules
- Agent patterns skill for SPAWN REQUEST format and report structure
- Spec writing skill for authoring effective `specs.md` files
- API contract skill for designing the shared interface between agents
