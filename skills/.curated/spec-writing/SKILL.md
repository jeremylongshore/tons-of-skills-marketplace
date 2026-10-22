---
name: spec-writing
description: 'Execute this skill should be used when the user asks about "writing
  specs", "specs.md format", "how to write specifications", "sprint requirements",
  "testing configuration", "scope definition", or needs guidance on creating effective
  sprint specifications for agentic development. Use when appropriate context detected.
  Trigger with relevant phrases based on skill purpose.

  '
allowed-tools: Read
version: 1.21.0
author: Damien Laine <damien.laine@gmail.com>
license: MIT
tags:
- community
- spec-writing
compatibility: Designed for Claude Code
---
# Spec Writing

## Overview

Spec Writing provides guidance on authoring effective `specs.md` files that drive the Sprint plugin's autonomous development workflow. A well-written specification determines the quality of agent output by clearly defining goals, scope boundaries, and testing requirements.

## Prerequisites

- Sprint plugin installed (`/plugin install sprint`)
- Project onboarding completed via `/sprint:setup` (creates `project-goals.md` and `project-map.md`)
- Sprint directory created via `/sprint:new` (generates `.claude/sprint/[N]/specs.md`)
- Understanding of the sprint phase lifecycle (see the `sprint-workflow` skill)

## Instructions

1. Open the generated `specs.md` file at `.claude/sprint/[N]/specs.md` and define a concise goal statement at the top. State what the sprint delivers in one sentence (e.g., "Add user authentication with email/password login").
2. Define explicit scope boundaries using **In Scope** and **Out of Scope** sections. List specific features, endpoints, or components in each. Agents only implement what appears in scope; ambiguity leads to drift.
3. Add the **Testing** section to control which testing agents run and how. Configure three settings as documented in `${CLAUDE_SKILL_DIR}/references/testing-configuration.md`:
   - `QA`: `required` | `optional` | `skip` -- Controls API and unit test execution
   - `UI Testing`: `required` | `optional` | `skip` -- Controls browser-based E2E tests
   - `UI Testing Mode`: `automated` | `manual` -- Auto-run or user-driven testing
4. Set QA to `required` for new API endpoints, business logic changes, and data validation rules. Set QA to `skip` for frontend-only changes, documentation updates, or configuration changes.
5. Set UI Testing to `required` for user-facing features, form submissions, and navigation flows. Choose `automated` mode for regression testing and standard CRUD flows; choose `manual` mode for complex interactions, visual verification, or exploratory testing.
6. Keep specifications minimal but precise. The architect expands high-level specs into detailed implementation files (`backend-specs.md`, `frontend-specs.md`, `api-contract.md`). Over-specifying implementation details in `specs.md` constrains the architect unnecessarily.
7. For iterative sprints, review `status.md` from the previous iteration. Remove completed items from specs and add any new requirements or bug fixes discovered during testing.

## Output

- A complete `specs.md` file with goal, scope (in/out), and testing configuration
- Clear scope boundaries that prevent agent drift during implementation
- Testing configuration that selects appropriate QA and UI testing agents
- Iteratively refined specs where completed work is removed and remaining work is focused

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Agents implement unintended features | Missing "Out of Scope" section | Explicitly list features excluded from this sprint |
| Tests not running during sprint | Testing section omitted or set to `skip` | Add `QA: required` and `UI Testing: required` to the Testing section |
| Sprint iterates without converging | Specs too broad for a single sprint | Break into smaller sprints targeting one domain boundary each |
| Architect produces conflicting spec files | Ambiguous or contradictory requirements in `specs.md` | Review for conflicting statements; each requirement should have a single interpretation |
| Manual tests not triggered | `UI Testing Mode` set to `automated` | Change to `manual` for scenarios requiring visual verification or exploratory testing |

## Examples

**Minimal but effective spec:**

```markdown
# Sprint 1: User Authentication

## Goal
Add user authentication with email/password login

## Scope
### In Scope
- Registration endpoint (POST /auth/register)
- Login endpoint (POST /auth/login)
- JWT token generation and validation
- Password hashing with bcrypt

### Out of Scope
- OAuth providers (Google, GitHub)
- Password reset flow
- Email verification

## Testing
- QA: required
- UI Testing: required
- UI Testing Mode: automated
```

**Frontend-only sprint (no QA needed):**

```markdown
# Sprint 3: Dashboard Redesign

## Goal
Redesign the admin dashboard with responsive layout

## Scope
### In Scope
- Responsive grid layout for dashboard widgets
- Dark mode toggle
- Mobile navigation drawer

### Out of Scope
- New API endpoints
- Database changes
- Authentication changes

## Testing
- QA: skip
- UI Testing: required
- UI Testing Mode: manual
```

## Resources

- `${CLAUDE_SKILL_DIR}/references/testing-configuration.md` -- Testing section options with guidance on when to use each setting
- Sprint workflow skill for understanding how specs feed into the phase lifecycle
- API contract skill for designing endpoint contracts referenced by specs
