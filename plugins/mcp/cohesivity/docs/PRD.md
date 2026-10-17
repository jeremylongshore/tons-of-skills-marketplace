# PRD: cohesivity

**Author:** Shouryamaan Jain (Cohesivity)
**Date:** 2026-10-16
**Status:** Active

## Problem

An agent asked to build an app with a database, login or a deploy can write the code and then stall, because every backend needs a person to create an account, provision the service and paste credentials back. Agents that keep going anyway tend to hardcode a connection string or commit a key. The submission issue (#1143) describes the gap in more detail.

The first submission of this plugin (#1144) also showed what a safe version has to look like: no mutable installer code running on the host, and a confirmation step for every call that changes external state that is enforced in code, not only described in the skill.

## Target users

| User                               | Context                                                  | Primary need                                           |
| ---------------------------------- | -------------------------------------------------------- | ------------------------------------------------------ |
| Developer building an app with Claude Code | The app needs Postgres, storage, hosting or login mid-build | A working backend without leaving the session          |
| Developer prototyping              | Wants a throwaway backend for a demo                     | Something free and temporary that can be kept later    |

## Success criteria

1. With the plugin installed, Claude Code lists the six Cohesivity tools from `https://cohesivity.ai/mcp` without any local install step.
2. Every `create_tenant`, `provision_resource` and `claim_tenant` call is held for user confirmation by the plugin's hook, and the server rejects the same calls when `confirmed: true` is missing.
3. A request such as "add a Postgres database to this app" ends with a `.cohesivity` file (mode 600, gitignored) and the service reported `"status": "active"`.

## Functional requirements

- **FR-1:** Connect to Cohesivity's hosted MCP server over HTTPS; download and execute nothing locally.
- **FR-2:** Ask the user before any tool call that creates a tenant, provisions a service or starts a claim.
- **FR-3:** Reuse the project's existing tenant instead of creating a second one.
- **FR-4:** Keep credentials in a private, gitignored `.cohesivity` file and out of client code.

## Out of scope

- Billing, plan upgrades and deleting resources. The hosted MCP server exposes no tools for these.
- Signing in to a Cohesivity account. Optional sign-in exists on the server; this plugin uses anonymous access only.
- Installing Cohesivity's own Claude Code plugin or its local MCP server.
