---
name: hermes-tweet
description: 'Use Xquik in Hermes Agent for public X research, monitoring, thread summaries, creator discovery & approved actions. Not affiliated with X Corp. Use when the user requests X data or a named action. Trigger with "search X", "monitor X", "post tweet", or "X trends".'
allowed-tools:
  - tweet_explore
  - tweet_read
  - tweet_action
version: 0.1.13
author: Burak Bayır (@kriptoburak), Xquik
license: MIT
compatibility: Requires Hermes Agent plugin support and Xquik API access.
argument-hint: "[X task, endpoint, or approved action]"
repo: https://github.com/Xquik-dev/hermes-tweet
homepage: https://github.com/Xquik-dev/hermes-tweet#readme
commit: c6ebdd7060965dd16a89e8cc12675ff834b5cc94
languages:
  - en
tags:
  - hermes-agent
  - xquik
  - twitter
  - x
  - social-media
  - automation
metadata:
  version: 0.1.13
  author: Xquik
  tags:
    - hermes-agent
    - xquik
    - twitter
    - x
    - social-media
    - automation
required_environment_variables:
  - name: XQUIK_API_KEY
    prompt: Xquik API key
    help: Create an API key at https://dashboard.xquik.com
    required_for: tweet_read, /xstatus, /xtrends, and authenticated Xquik API calls
capabilities:
  shell:
    required: false
    justification: Optional Hermes CLI checks are used only for installation and registry diagnostics.
  network:
    required: true
    justification: Hermes Tweet tools call Xquik API routes for X/Twitter reads and approved actions.
  files:
    required: false
    justification: Normal use does not require local file reads or writes.
  environment:
    required: true
    variables:
      - XQUIK_API_KEY
      - HERMES_TWEET_ENABLE_ACTIONS
      - HERMES_ENABLE_PROJECT_PLUGINS
    justification: Runtime configuration controls authenticated reads, gated actions, and trusted project-local plugin loading.
  mcp:
    required: false
    justification: No MCP server access is required.
  tools:
    - tweet_explore
    - tweet_read
    - tweet_action
---

# Hermes Tweet

## Overview

Discover catalog-listed Xquik routes and run authenticated reads without guessed endpoints.
Private or state-changing operations require the action gate and user approval.
Enable `tweet_action` only after the user approves its endpoint, payload, account, and effects.

## When to use Hermes Tweet

Use this Skill for X/Twitter research, social listening, monitoring, support triage,
creator research, giveaway audits, community audits, and controlled publishing.

Use `tweet_explore` first when the user asks for a capability, endpoint, route,
or Xquik API route. Use `tweet_read` only after a read-only endpoint is known.
Use `tweet_action` only after the user requests a write, private read, monitor,
webhook, extraction job, giveaway draw, or media operation that requires action
permissions.

## Prerequisites

- Install and enable the plugin with
  `hermes plugins install Xquik-dev/hermes-tweet --enable`.
- Review Hermes security-scan warnings. Dangerous plugins are blocked.
- Configure `XQUIK_API_KEY` on the Hermes runtime host for authenticated reads.
  `tweet_explore` remains available without the key or network access.
- Leave `HERMES_TWEET_ENABLE_ACTIONS` unset or false unless the workflow needs
  an approved write-like or private operation.
- For project-local plugins, set `HERMES_ENABLE_PROJECT_PLUGINS=true` only in a
  trusted repository.
- Restart a gateway after environment changes and start a new session. Active
  CLI sessions can use `/reload`.

## Permissions and capabilities

- Use `tweet_explore`, `tweet_read`, and `tweet_action` only through the enabled
  Hermes Tweet toolset.
- Network access is limited to catalog-listed Xquik API routes reached by those
  tools. Do not create direct HTTP fallbacks.
- Shell access is not part of normal operation. Use Hermes CLI commands only for
  the install and registry checks listed in Testing.
- Local file access is not part of normal operation. Do not write reports,
  credentials, logs, screenshots, or cached API payloads unless the user asks
  for an explicit export workflow.
- Environment access is limited to configuration presence checks for
  `XQUIK_API_KEY`, `HERMES_TWEET_ENABLE_ACTIONS`, and
  `HERMES_ENABLE_PROJECT_PLUGINS`. Never request or echo their values.
- MCP access is not required.

## Instructions

1. Confirm the plugin is enabled with `hermes plugins list` and confirm tool
   registration with `hermes tools list`.
2. Use `tweet_explore` to find the catalog endpoint and method.
3. Use `tweet_read` for public read-only endpoints after the API key is
   configured.
4. Before `tweet_action`, state the exact endpoint, payload, account, reason,
   and expected side effects, then get explicit approval.
5. Verify the tool response. Report policy, authentication, validation, or
   account errors without retrying through alternate routes.

## Choose a tool

- For endpoint discovery, call `tweet_explore` with a short query.
- For catalog-listed `GET` routes, call `tweet_read`.
- For private or write-like routes, require enabled actions and user approval.
- When `tweet_action` is disabled, explain the environment gate.
- When `XQUIK_API_KEY` is missing, ask the user to configure it.
- Never request the key value in chat.
- When Hermes shows `not enabled`, run `hermes plugins enable hermes-tweet`.
- Project-local plugins require `HERMES_ENABLE_PROJECT_PLUGINS=true` in trusted
  repositories.
- For unattended work, prefer `tweet_read` and keep actions disabled.
- Remote Desktop profiles run tools on the remote Hermes host.
- Keep dashboard-managed secrets in the runtime environment.

## Safety

- Never ask for or reveal API keys, signing keys, passwords, cookies, or TOTP secrets.
- Never pass credentials in tool arguments.
- Use only catalog-listed `/api/v1/...` endpoints.
- Copied endpoint URLs are accepted only when they resolve to catalog-listed paths.
- Do not use account connection, re-authentication, API key, billing, credit top-up, or support-ticket endpoints.
- For posting, deleting, following, DMs, profile changes, monitors, webhooks, extraction jobs, and draws, summarize the action before calling `tweet_action`.

## Known risks and mitigations

- **Broad requests.** Start with `tweet_explore` and prefer `tweet_read`.
  Require an approved endpoint and payload before `tweet_action`.
- **Exposed secrets.** Ask only whether environment configuration exists.
  Never request key values or pass credentials as tool arguments.
- **Guessed endpoints.** Accept only catalog-listed `/api/v1/...` paths.
  Never create a direct HTTP fallback.
- **Account changes.** Keep `HERMES_TWEET_ENABLE_ACTIONS=false` by default.
  Summarize each account-changing call before approval.

## Output

- Return endpoint choices, result summaries, action previews, and fixes.
- Use concise Markdown and JSON-like Hermes Tweet payloads.
- `tweet_explore` does not call the API.
- `tweet_read` performs authenticated reads.
- `tweet_action` can change state only after explicit approval.

## Error handling

Use the narrowest recovery step that preserves the read-first and action-gated
contract:

- **Missing tool.** Confirm the plugin is enabled. Run `hermes tools list`.
- **Missing API key.** Configure `XQUIK_API_KEY` on the runtime host without pasting
  its value into chat, then run `/reload` in an active CLI session or run
  `hermes gateway restart` and start a new gateway session.
- **Unknown endpoint.** Call `tweet_explore` again. Never guess paths or create a
  direct HTTP fallback.
- **Disabled action.** Keep it blocked unless the user requested it and
  `HERMES_TWEET_ENABLE_ACTIONS=true` is intentionally configured.
- **Request failure.** Return the sanitized error and corrective step.
  Do not retry through another route.
- **Missing slash command.** Verify registration in an active Hermes session.
  Prompt text does not prove registration.
- **Secret in input.** Stop and ask the user to rotate it.

## Examples

**Search tweets.**

```json
{"query":"tweet search","method":"GET"}
```

Then call:

```json
{"path":"/api/v1/x/tweets/search","query":{"q":"AI agents","limit":25}}
```

**Inspect trends.**

Run `/xtrends` in an active Hermes session. Use `tweet_explore` when the task
needs a catalog endpoint or structured response instead of the slash command.

**Post a tweet.**

```json
{"query":"post tweet","include_actions":true}
```

Then call `tweet_action` with:

```json
{"path":"/api/v1/x/tweets","method":"POST","body":{"account":"@example","text":"Hello from Hermes Tweet"},"reason":"Post the user-approved tweet."}
```

## Testing

After installing or upgrading the plugin in Hermes Agent:

1. Run `hermes plugins enable hermes-tweet` unless the install used `--enable`.
2. Run `hermes plugins list` and confirm the plugin is `enabled`.
3. Run `hermes tools list` and confirm the `hermes-tweet` toolset is enabled.
4. Confirm `tweet_explore` is available without `XQUIK_API_KEY`.
5. Confirm `tweet_read` appears only when `XQUIK_API_KEY` is configured.
6. Confirm `tweet_action` stays hidden or disabled unless `HERMES_TWEET_ENABLE_ACTIONS=true`.

Useful CLI checks:

```bash
hermes plugins enable hermes-tweet
hermes tools list
```

## Release trust gate

Before presenting this skill as NVIDIA-verified or ready for broad enterprise
deployment:

1. Run SkillSpector against the complete skill directory and resolve critical or
   high findings.
2. Complete `skill-card.md` with owner, license, use case, deployment
   geography, risks, references, output shape, and release version.
3. Include Tier-3 eval data and `BENCHMARK.md` for the reviewed release.
4. Sign the exact reviewed skill directory and publish `skill.oms.sig`.
5. Verify the published directory with the expected certificate chain.

Do not claim NVIDIA verification when those release artifacts are absent.

## Resources

- [Endpoint and approval contract](references/endpoint-contract.md)
- [Skill card](skill-card.md)
- [Hermes Tweet repository](https://github.com/Xquik-dev/hermes-tweet)
- [Hermes Agent plugin guide](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/features/plugins.md)
- [Xquik Hermes Tweet guide](https://docs.xquik.com/guides/hermes-tweet)
