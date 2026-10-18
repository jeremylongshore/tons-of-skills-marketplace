# ADR: cohesivity — hosted MCP only, with a host-side confirmation hook

**Author:** Shouryamaan Jain (Cohesivity)
**Date:** 2026-10-16
**Status:** Accepted

## Context

The first submission (#1144) mirrored Cohesivity's Claude Code plugin. Its local MCP server downloaded `https://cohesivity.ai/quickstart.sh` and ran it with the host environment, and tenant creation and credential writes had no confirmation enforced in code. The maintainer closed it and asked for a pinned or bundled installer, execution limited to the workspace with a minimal environment, and code-enforced confirmation with behavioral tests (FR-1, FR-2).

## Decision

We ship a plugin that connects only to Cohesivity's hosted MCP server (`https://cohesivity.ai/mcp`) over HTTPS and has no installer, no local MCP process and no downloaded code. A `PreToolUse` hook matches `create_tenant`, `provision_resource` and `claim_tenant` under both the bare and the plugin-scoped tool names and returns `permissionDecision: "ask"`, so the host prompts the user before any of those calls is sent. The server also marks those three tools `anthropic/requiresUserInteraction: true`, which Claude Code honors by prompting even when the tool is allowed or auto mode is on, and rejects them unless `confirmed: true` is passed.

## Alternatives considered

| Alternative                                         | Why rejected                                                                                     |
| --------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| Mirror Cohesivity's plugin again (Path B)           | Its local MCP still downloads and runs `quickstart.sh`, the objection #1144 was closed for.      |
| Bundle a local MCP server in this plugin            | Puts executable code and a build in this repo for no gain; the hosted server already does the work. |
| Rely on the server's `confirmed` flag alone         | The model sets that flag, so it is not a host-side gate. The hook makes the user the one who decides. |

## Consequences

**Positive:**

- Nothing runs on the user's machine except a 20-line hook script that prints a fixed JSON decision.
- Every state-changing call needs the user's approval in the host, independent of what the model passes.
- The plugin stays current without updates here: tool behavior lives on the hosted server.

**Negative / accepted tradeoffs:**

- Needs network access to `cohesivity.ai`; there is no offline mode.
- The hook asks on every matched call, including a second provision in the same session. That is the intended trade for a hard gate.
- The skill text is frozen at submission (Path A), so changes to it need a PR here.

## Tool-permission scope

The skill pre-approves only tools that read. Everything else, including writing `.cohesivity`, goes through Claude Code's normal permission flow.

| Tool                                              | Why it's needed                                            |
| ------------------------------------------------- | ---------------------------------------------------------- |
| Read                                              | Read `tenant_id` and the management key from `.cohesivity` |
| mcp\_\_cohesivity\_\_tenant_status                | Read lifecycle and limits (read-only)                      |
| mcp\_\_cohesivity\_\_get_cohesivity_documentation | Get a service's docs page before using it (read-only)      |
