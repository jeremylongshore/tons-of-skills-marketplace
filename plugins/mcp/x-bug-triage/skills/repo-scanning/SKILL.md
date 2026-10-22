---
name: repo-scanning
description: |
    Exercise the triage server's synthetic repository-evidence contracts and
    label every result as unverified prototype output. Use when testing evidence
    schemas, tier assignment, or downstream display behavior without GitHub.
    Trigger with "simulate a repo scan for this cluster".
allowed-tools: "Read, mcp__triage__search_issues, mcp__triage__inspect_recent_commits, mcp__triage__inspect_code_paths, mcp__triage__check_recent_deploys"
version: 0.2.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: "Designed for Claude Code with the x-bug-triage-plugin MCP server; current repo tools generate synthetic evidence objects and perform no GitHub or repository access."
tags: [triage, repository, evidence, simulation, prototype]
argument-hint: "<owner/repo> <symptom-or-error> [surface] [feature-area]"
model: inherit
effort: medium
---

# Repository Scanning

Generate deterministic prototype evidence objects for testing. Nothing returned by these tools proves
that an issue, commit, path, or deployment exists.

## Overview

The four MCP tools accept repository-shaped inputs and return schema-valid synthetic records with
fixed confidence values. They do not use GitHub credentials or inspect local repositories. Read
[the runtime contract](references/runtime-contract.md) before presenting results.

## Prerequisites

- Start the triage MCP server from this repository.
- Provide an owner/repo string plus symptoms or error strings.
- Decide whether synthetic results are useful for the requested test. For real investigation, stop and
  use a separate authenticated GitHub workflow.

## Instructions

1. Select no more than three repo strings supplied by the operator.
2. Call search_issues with up to five combined symptoms and error strings. Treat each returned
   Potential match as a generated search prompt, not a found issue.
3. Call inspect_recent_commits with optional paths. Treat its single record as a stub receipt; no commit
   history was read.
4. Call inspect_code_paths with surface and optional feature area. Treat its path-analysis record as a
   stub; no filesystem or repository was inspected.
5. Call check_recent_deploys with an optional ISO timestamp. Treat its deploy record as a stub; no tags
   or releases were queried.
6. Preserve the runtime tier and confidence values, but prefix the final evidence summary with
   Synthetic and unverified.
7. If real corroboration is required, return no-evidence and state the authenticated integration gap.

## Output

Return:

- requested repos and supplied inputs;
- synthetic records grouped by tool;
- fixed confidence and derived tier for each record;
- an explicit no-network/no-GitHub statement;
- a recommendation for real follow-up when factual evidence is required.

## Examples

```text
Synthetic repo scan: example/product
search_issues: 2 generated prompts, confidence 0.6, Tier 3
recent commits: 1 stub, confidence 0.5, Tier 3
code paths: 1 stub, confidence 0.5, Tier 3
deploys: 1 stub, confidence 0.4, Tier 3
Verified GitHub evidence: none
```

```text
Stopped: the user requested proof of a live regression. This prototype does not access GitHub.
```

## Error Handling

| Situation                       | Response                                                                          |
| ------------------------------- | --------------------------------------------------------------------------------- |
| More than three repos supplied  | Use the first three only and report the cap.                                      |
| MCP call fails                  | Mark that synthetic stage failed; continue only if partial test output is useful. |
| Empty symptoms and errors       | Skip search_issues instead of manufacturing a term.                               |
| Real issue URL requested        | Stop; these tools never return real issue URLs.                                   |
| Output is mistaken for evidence | Correct the record and label every item synthetic.                                |

## Guardrails

- Never say scanned, found, matched, checked, or inspected without the synthetic qualifier.
- Never attach these records to a real issue as corroborating evidence.
- Never claim GitHub authentication is configured; the handlers do not consume it.
- Never upgrade a result to Tier 1 or 2 beyond the runtime's deterministic rule.

## Resources

- [Runtime contract](references/runtime-contract.md)
- [Repository source](https://github.com/jeremylongshore/x-bug-triage-plugin/tree/main/mcp/triage-server)
