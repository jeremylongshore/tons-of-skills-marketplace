---
name: owner-routing
description: |
    Exercise the triage server's five owner-lookup contracts and produce an
    explicit uncertainty result when the current prototype returns no team.
    Use when testing routing precedence or documenting missing ownership data.
    Trigger with "route this bug cluster".
allowed-tools: "Read, mcp__triage__lookup_service_owner, mcp__triage__lookup_oncall, mcp__triage__parse_codeowners, mcp__triage__lookup_recent_assignees, mcp__triage__lookup_recent_committers"
version: 0.2.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: "Designed for Claude Code with the x-bug-triage-plugin MCP server; current lookup tools are offline contract stubs and do not query GitHub, on-call, or service catalogs."
tags: [triage, routing, ownership, prototype, uncertainty]
argument-hint: "<owner/repo> [surface] [paths...]"
model: inherit
effort: medium
---

# Owner Routing

Run the public routing contract honestly. The current MCP lookup tools return their precedence level
and base confidence but no team or assignee, so a normal result is explicit uncertainty.

## Overview

The runtime registers five read-only routing tools for levels 1-5. Level 6 is a conceptual fallback,
not an MCP tool, and this repository has no populated fallback map. Read
[the runtime contract](references/runtime-contract.md) before interpreting a response.

## Prerequisites

- Start the triage MCP server from this repository.
- Provide an owner/repo; optionally provide a surface and affected paths.
- Treat the supplied repo name as data only. These tools do not authenticate to or inspect GitHub.

## Instructions

1. Call lookup_service_owner with the repo and optional surface.
2. If the result contains a non-empty team or assignee, retain it as level 1. Otherwise continue.
3. Call lookup_oncall, parse_codeowners, lookup_recent_assignees, and lookup_recent_committers in order.
4. Reject results with neither team nor assignee; base confidence alone is not ownership evidence.
5. If a caller supplies a previously reviewed routing override, present it separately as human input.
   The MCP tools do not load overrides from SQLite.
6. If every level is empty, return uncertainty and explain that live integrations are absent.
7. Never invent level 6. A fallback recommendation requires an explicit operator-supplied mapping.

## Output

Return one routing report:

- repo, surface, and paths evaluated;
- all five tool results in precedence order;
- accepted recommendation or null;
- uncertainty and a plain-language reason;
- any operator-supplied override, clearly labeled as external input.

## Examples

```text
Repo: example/product
Levels checked: 1, 2, 3, 4, 5
Recommendation: null
Uncertainty: true
Reason: current lookup tools are offline stubs and returned no team or assignee.
```

```text
Operator override: platform-team
Disposition: use as human-supplied routing input; not independently verified by this runtime.
```

## Error Handling

| Situation                          | Response                                                                      |
| ---------------------------------- | ----------------------------------------------------------------------------- |
| MCP server is unavailable          | Stop and report setup failure.                                                |
| A tool throws                      | Record that level as failed and continue; do not relabel failure as no match. |
| Result has confidence but no owner | Reject it as an empty routing signal.                                         |
| No fallback mapping was supplied   | Return uncertainty rather than guessing.                                      |
| Repo string is malformed           | Stop and request owner/repo.                                                  |

## Guardrails

- Never claim these tools read CODEOWNERS, commits, issues, on-call data, or a service catalog today.
- Never let numeric base confidence substitute for an actual team or assignee.
- Never persist or announce an assignment without human review outside this skill.

## Resources

- [Runtime contract](references/runtime-contract.md)
- [Repository source](https://github.com/jeremylongshore/x-bug-triage-plugin/tree/main/mcp/triage-server)
