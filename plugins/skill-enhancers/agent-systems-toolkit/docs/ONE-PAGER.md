# Agent Systems Toolkit

**Create, validate, and upgrade agent-system artifacts through one evidence-bound workflow.**

## Problem

Skills, agents, plugins, MCP integrations, hooks, and marketplaces have different
authorities and host behaviors. Applying one assumed schema to all of them can
produce unsafe permissions, broken packaging, duplicate validators, and portability
claims that do not survive a clean installation.

## Solution

The toolkit provides three portable Agent Skills, five specialist role packets,
optional Claude Code agent adapters, capability routing to existing validators,
Beads workflow guidance, and deterministic evidence checks. It reports host
limitations instead of silently weakening the workflow.

## W5

| | |
| --- | --- |
| **Who** | Skill, plugin, agent, and integration authors plus maintainers and reviewers |
| **What** | Creates artifacts, selects canonical validators, and runs production-upgrade evidence gates |
| **When** | Starting a new artifact, auditing an existing one, or preparing a security-sensitive modernization |
| **Where** | Any harness that can supply the portable instructions; adapters cover host-specific features |
| **Why** | Keeps authority, permissions, compatibility claims, and release evidence explicit |

## Stack

| Layer | Choice |
| --- | --- |
| Portable workflow | Open Agent Skills `SKILL.md` contract |
| Host integration | Capability-detected adapters and Claude Code agent definitions |
| Durable tracking | Beads when required; disclosed fallback otherwise |
| Verification | Existing repository validators plus bounded Python standard-library helpers |
| External APIs | None required by the portable core |

## Differentiators

1. Routes to existing creator and validator authorities instead of copying them.
2. Runs the same five review roles with or without native subagent support.
3. Makes security, compatibility, approval, and release claims depend on reproducible evidence.
