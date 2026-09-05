# PRD: Agent Systems Toolkit

**Author:** Jeremy Longshore

**Date:** 2026-09-05

**Status:** Active

## Problem

Agent-system authors currently cross several creator, validator, and host-specific
workflows to build skills, agents, plugins, MCP integrations, hooks, and catalogs.
Treating those formats as interchangeable creates schema drift, excessive tool
permissions, unsupported portability claims, and review evidence that cannot be
reproduced. The capability and runtime audit in `../000-docs/002-RL-RSRC-capability-and-runtime-audit.md`
records the existing surface and the boundary this toolkit must preserve.

## Target users

| User | Context | Primary need |
| --- | --- | --- |
| Marketplace maintainer | Creating or modernizing repository artifacts | One governed workflow that delegates to canonical validators |
| Skill or plugin author | Targeting one or more agent harnesses | A portable core with explicit host-adapter boundaries |
| Security reviewer | Assessing generated or upgraded artifacts | Least-privilege defaults and revision-bound evidence |

## Success criteria

1. All three skills pass the marketplace schema and strict conformance gates at grade A.
2. The capability map routes every supported artifact class to its existing authority without replacing a public ID.
3. The portable skills require no network, shell, MCP, or subagent capability in frontmatter.
4. Focused tests prove artifact discovery, evidence validation, degraded operation, and security invariants.

## Functional requirements

- **FR-1:** Route creation and validation by artifact type and target host.
- **FR-2:** Orchestrate research, architecture, implementation, verification, and security roles without requiring subagent support.
- **FR-3:** Use Beads when repository policy requires it and disclose weaker persistence when it is unavailable.
- **FR-4:** Bind validation, review, approval, and release claims to exact revisions and retained evidence.
- **FR-5:** Fail closed on unknown formats, permissions, side effects, support states, and secrets.

## Out of scope

- Replacing existing creator or validator implementations.
- Claiming universal automatic discovery or host compatibility.
- Publishing, merging, deploying, or performing destructive changes without explicit authorization.
