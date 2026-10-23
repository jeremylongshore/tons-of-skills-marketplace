# NOI — Plane

> **Plane is a team behavior observatory.**

## Evidence boundary

This document records design intent and hypothetical signals, not measured team
behavior or proof that an endpoint exposes history. The current API mapping and
compound-command evidence rules govern execution. Historical metrics require
actual snapshots/events; comments and assignment counts cannot establish intent,
competence, causality or capacity. Do not repeat the rhetorical personnel judgments
below as findings.

## What this NOI claims

Plane describes itself as an open-source project tracker — issues, cycles, modules, projects, work-in-progress. That's the **claimed identity**. It's accurate but it's the floor, not the ceiling.

The **secret identity** is what you can read off Plane that nobody talks about: how a team actually behaves under pressure. Cycle close-out velocity, the gap between estimate and actual, which workflows quietly orphan tickets in `In Progress`, which engineers consistently ship under the wire and which stack up at the deadline, which reviewers gate-keep harder than the spec demands, which projects burn cycles on rework versus on net-new work, and where the team's stated priorities diverge from what's actually getting closed.

That's not project tracking. That's an observatory pointed at organizational behavior, with Plane's API as the telescope.

## What this NOI unlocks that the obvious wrapper doesn't

A "Plane wrapper" skill calls `list_project_issues` and renders results. Useful but generic — every Plane SDK does that. The team-behavior-observatory framing demands compound queries that synthesize multiple endpoints into observations no single endpoint exposes:

- **Cycle close velocity vs. estimate**: cross-reference cycle close dates with cycle planning dates and issue-level estimate vs. actual time-to-close. Surfaces "the team consistently overruns 2-week cycles by 4 days" — invisible from any single endpoint.
- **Stale-ticket drift**: `In Progress` tickets older than the cycle they were planned in, scored by ownership churn (assignee changes during the open window). Surfaces "the cluster of tickets that quietly fail every two weeks because three people share ownership."
- **Reviewer gate strength**: time-from-blocker-flagged to blocker-cleared, sliced by reviewer. Distinguishes reviewers who clear blockers fast (engineers) from reviewers who serve as control points (process gatekeeping). Surfaces "PRs assigned to X close in 1.4 days; PRs assigned to Y close in 6.8 — Y is a bottleneck, not a senior."
- **Stated-vs-actual priority drift**: the priority labels on planned issues vs. the priority labels on issues that actually closed in the cycle. Surfaces "the team plans P1s and ships P3s — the planning conversation is theater."
- **Cross-project workload concentration**: aggregate `assigned_to` counts across all active projects per engineer. Surfaces "Alice is on 7 active cycles across 4 projects; that's not focus, that's project-management debt."

None of these are visible in Plane's dashboard. None are accessible from a single API endpoint. Each requires the skill to JOIN data the API only exposes per-resource — which is the compound-command discipline the forge mandates.

## Why this NOI matters for downstream design

Every gate downstream of this point reads from `noi.md`. The compound commands designed in `compound-commands.md` are derived from these specific observations, not from "what endpoints does Plane have." The agents (`plane-expert`, `plane-analyst`) carry this framing in their system prompts — they answer behavioral questions about teams, not ticket-CRUD questions.

If a future maintainer asks "should we add X to this skill?" — the answer is: **does X surface team-behavior signal?** If yes, design it as a compound query. If no (e.g., "create issue from CLI"), add it to a separate utility skill instead. The NOI is the gate that keeps this skill from sprawling into a generic Plane wrapper.

## Not what this NOI claims

- Not a CRUD wrapper for Plane (that's `mcp__plane` directly)
- Not a CLI alternative to `projects.intentsolutions.io` (the web UI is fine for ticket entry)
- Not a Plane-specific clone of standard project-tracker skills (the framing rejects that direction)
