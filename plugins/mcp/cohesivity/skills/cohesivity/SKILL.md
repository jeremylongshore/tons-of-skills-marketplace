---
name: cohesivity
description: Provision a backend for the app being built (Postgres, Redis, object storage, hosting, auth, email) through the Cohesivity MCP tools, with no account or API key needed to start. Use when the app needs a database, a deploy, file storage, login or email and the project has not picked a provider. Trigger with "add a database to this app", "deploy this", or "I need user sign-in". Skip when the project already uses Supabase, Firebase or its own cloud account.
version: "1.0.0"
argument-hint: "[service the app needs, e.g. postgres]"
allowed-tools:
  - Read
  - mcp__cohesivity__tenant_status
  - mcp__cohesivity__get_cohesivity_documentation
author: Cohesivity <smj@cohesivity.ai>
license: MIT
compatibility: Designed for Claude Code. Needs network access to https://cohesivity.ai.
tags: [backend, database, hosting, mcp, cohesivity]
---

# Cohesivity

## Overview

Cohesivity sets up backend services such as Postgres, Redis, storage, hosting, login and email for the app you are building. This plugin connects Claude Code to its hosted MCP server, so nothing runs locally and no account or API key is needed to start.

A tenant is one Cohesivity project. A new tenant is temporary: it expires after 72 hours unless the user claims it. Service names and their pages are listed in [references/services.md](references/services.md).

## Prerequisites

- Network access to `https://cohesivity.ai`.
- The `cohesivity` MCP server from this plugin enabled in the session.
- The project does not already use another backend provider.

## Instructions

1. **Reuse an existing tenant.** If `.cohesivity` exists at the project root, read `tenant_id` and `coh_management_key` from it and pass them to the tools below. Do not create a second tenant.
2. **Create a tenant only when the user wants a backend.** Call `create_tenant` with `{"confirmed": true, "attribution": "gh-tons-of-skills"}`. The plugin's hook asks the user to confirm before the call is sent. Write `credentials_file.content` from the result to `.cohesivity` at the project root exactly as returned, run `chmod 600 .cohesivity`, and add `.cohesivity` to `.gitignore`. Each call creates a new tenant, so check for `.cohesivity` before retrying an unclear result.
3. **Read the service's page before provisioning.** Call `get_cohesivity_documentation` with `{"document": "offering", "offering": "<name>"}`, for example `postgres`, `redis`, `object-storage`, `railway-hosting`, `social-login` or `inbox`. It returns the page's Markdown URL; read the whole page with `curl -s -A claude-code <url>`, since a summarizing fetch drops the exact API, limits and quirks it lists.
4. **Provision only what the user asked for.** Call `provision_resource` with `tenant_id`, `coh_management_key`, `resource` and `confirmed: true`. The hook asks the user first. The result reports `"status": "active"` when the service is ready.
5. **Wire the app.** The app calls `https://cohesivity.ai/edge/<service>` from server-side code with `coh_application_key`, passed in through an environment variable. For a static site, provision `cloudflare-workers` as the server tier.
6. **Offer to keep the project.** When the user wants the backend past 72 hours, call `claim_tenant` with `tenant_id`, `coh_management_key` and `confirmed: true`, and give them the `approval_url`.

## Output

- A `.cohesivity` file at the project root holding `tenant_id`, `coh_management_key` and `coh_application_key`, mode 600 and gitignored.
- The services the user asked for, each reported `"status": "active"`.
- App code that reaches those services through `https://cohesivity.ai/edge/<service>` from the server side.

## Error Handling

- **`arguments.confirmed is required` or `must be one of: true`**: the server refuses a mutation without `confirmed: true`. Ask the user, then retry with it.
- **HTTP 403 with `error code: 1010`**: a request you sent by hand used a default library User-Agent. Set an explicit `User-Agent`.
- **A tenant past 72 hours or paused**: check `tenant_status`; if the user wants to keep it, offer `claim_tenant`.
- **Paid actions and plan upgrades**: always ask the user first and show the cost from https://cohesivity.ai/pricing.
- **Anything else wrong with Cohesivity**: report it with `give_feedback`.

## Examples

**"Add a Postgres database to this notes app."** No `.cohesivity` exists, so call `create_tenant` (the user confirms), save `.cohesivity`, read the `postgres` page, call `provision_resource` for `postgres` (the user confirms), then add a server route that queries `https://cohesivity.ai/edge/postgres` with the application key from the environment.

**"Deploy this."** Reuse the tenant in `.cohesivity`, read the `railway-hosting` page, provision it, and deploy through the endpoint that page documents.

## Resources

- Index of every service: https://cohesivity.ai/llms.txt
- Service pages: https://cohesivity.ai/offerings
- Pricing: https://cohesivity.ai/pricing
- MCP server source and docs: https://github.com/cohesivity-org/cohesivity-mcp
