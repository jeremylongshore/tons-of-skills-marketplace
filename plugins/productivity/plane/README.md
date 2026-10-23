# Plane — Team Behavior Observatory

> **Plane is a team behavior observatory.** Most Plane integrations wrap the API for ticket entry; this one synthesizes the data Plane already has into observations about how a team actually behaves under pressure — cycle velocity vs. plan, ownership churn on stuck tickets, reviewer gate strength, stated-vs-actual priority drift, and cross-project workload concentration.

## What this plugin is

A behavioral observation layer on top of Plane's project-tracking API. It does **not** replicate `mcp__plane`'s CRUD surface; that's the data-retrieval layer. This plugin sits one level up — it asks behavioral questions that require JOINing across multiple Plane endpoints to answer.

## What this plugin is not

- Not a Plane CLI (use `mcp__plane` MCP directly for ticket CRUD)
- Not a clone of the Plane web dashboard (the dashboard already shows you ticket state)
- Not a generic project-tracker skill (the framing is specifically behavioral, anchored in the NOI)

## The five compound commands

Each answers a question that **cannot** be answered from any single Plane API endpoint:

| Command | Question |
|---|---|
| `/plane-cycle-velocity` | Does cycle close-out match cycle planning? |
| `/plane-stale-tickets` | Which `In Progress` tickets are quietly failing under shared ownership? |
| `/plane-reviewer-gate-strength` | Which reviewers gate-keep harder than the spec demands? |
| `/plane-priority-drift` | Does the team plan high-priority work but ship low-priority work? |
| `/plane-cross-project-load` | Which engineers are spread across too many active projects? |

Each command's exact endpoint sequence, scoring formula, and output table format is documented in [`skills/plane/references/compound-commands.md`](skills/plane/references/compound-commands.md).

## Install

```
/plugin install plane@claude-code-plugins-plus
```

## Prerequisites

- A separately configured Plane MCP server with host-permitted read tools. This plugin installs or pins no server. Inspect its implementation/version and schemas; see the versioned mapping in `skills/plane/references/api-surface.md`. Without permitted tools, output is documentation-only.
- Historical plan, assignment-change, and reviewer-delay metrics require corresponding snapshots/events. Current ticket data alone cannot establish them.
- A Plane workspace with at least one project, cycle, and active issues — empty workspaces return informative empty states.

## How it works

The skill reads the nested `plane-expert` and `plane-analyst` files as reference
checklists within the current session. They are not registered plugin agents and
grant no MCP permissions. API-help mode uses pinned references; analysis mode
selects verified read capabilities and computes only metrics supported by actual
data. Missing history stays unavailable. Mutation exclusions are prose guidance,
not a runtime MCP filter. No authenticated workspace or behavioral evaluation was
run for the 2026-10-23 source review.

## Provenance

This plugin was produced by `/skill-creator --forge plane` on 2026-05-07. The forge run's audit trail lives in [`.forge/`](.forge/) — research notes, ecosystem analysis, validation evidence — visible to anyone reviewing how the plugin came to exist.

The [editable marketplace catalog](../../../.claude-plugin/marketplace.extended.json) retains `"generated": true` and `"author_type": "forge"` as provenance metadata. These are not executable plugin-manifest fields or runtime verification evidence; no verification badge is established by this record.

## License

MIT. See `LICENSE` (project-wide root file).
