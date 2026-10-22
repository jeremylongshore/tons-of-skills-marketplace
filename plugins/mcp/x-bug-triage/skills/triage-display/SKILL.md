---
name: triage-display
description: |
    Format supplied cluster data as bounded terminal Markdown and parse one
    review-command string with the triage MCP parser. Use when previewing triage
    output or validating command syntax without mutating cluster state.
    Trigger with "format this triage summary" or "parse this review command".
allowed-tools: "Read, mcp__triage__parse_review_command"
version: 0.2.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: "Designed for Claude Code with the x-bug-triage-plugin MCP server; formatting is model-authored and the only exposed display helper is a syntax parser."
tags: [triage, terminal, markdown, command-parser, preview]
argument-hint: "<cluster-json-or-command-text>"
model: inherit
effort: medium
---

# Triage Display

Render data already supplied by the caller or validate review-command syntax. This skill does not
load clusters, execute commands, mutate SQLite, send Slack messages, or file issues.

## Overview

The MCP server exposes parse_review_command. It recognizes command shape and numeric cluster tokens,
but it does not know the current run and cannot confirm that a cluster number exists. Formatting and
confirmation text are library helpers, not separate MCP tools. Read
[the runtime contract](references/runtime-contract.md) for exact limits.

## Prerequisites

- Start the triage MCP server when command parsing is requested.
- Supply already-redacted cluster, evidence, routing, and source-status data for display.
- Omit raw X text and secret-bearing URLs. This skill does not perform redaction.

## Authentication

No external authentication is used. The local MCP parser accepts text and performs no network call.

## Instructions

### Format a summary

1. Validate that every cluster record has an identifier, severity, report count, and state.
2. Sort by the caller-provided severity ordering; do not compute or raise severity here.
3. Show no more than five clusters in the compact view and state how many remain.
4. Label synthetic repo evidence as synthetic. Omit an owner when routing is uncertain.
5. Keep the compact result near 20 lines when the input permits it.

### Parse a command

1. Call parse_review_command with message_text.
2. Return the parsed command, cluster number, optional lower-cased arguments, validity, and error.
3. Validate the cluster number against the caller's current displayed list; the MCP parser cannot.
4. Treat a valid parse as syntax only. Never claim the requested action ran.

## Output

Return either terminal Markdown or a command parse receipt. Include:

- input cluster count and displayed count;
- source/degradation warnings provided by the caller;
- evidence provenance labels;
- parser validity plus separate current-run validation;
- a clear no-mutation statement for commands.

## Examples

```text
X Bug Triage - supplied preview
3 clusters
1. API timeout - low - 4 reports - owner uncertain
   Evidence: synthetic Tier 3 records only
2 more clusters shown...
```

```text
Input: dismiss 3 false positive
Parser: valid syntax; clusterNumber=3; args=false positive
Execution: not performed
Current-run validation: required
```

## Error Handling

| Situation                             | Response                                                                |
| ------------------------------------- | ----------------------------------------------------------------------- |
| Missing cluster fields                | Mark the row incomplete; do not fabricate values.                       |
| Parser reports invalid                | Show its error and stop.                                                |
| Parser accepts an out-of-range number | Reject it during current-run validation.                                |
| Command requests a mutation           | Return syntax only and require a separate implementation/approval path. |
| Unredacted sensitive text is supplied | Refuse to display it.                                                   |

## Guardrails

- Never emit action-confirmation prose unless an external executor supplies a successful receipt.
- Never say a cluster was dismissed, filed, merged, escalated, snoozed, split, or rerouted from parser
  output alone.
- Never claim Slack delivery; no Slack tool is exposed by this plugin.

## Resources

- [Runtime contract](references/runtime-contract.md)
- [Repository source](https://github.com/jeremylongshore/x-bug-triage-plugin/tree/main/mcp/triage-server)
