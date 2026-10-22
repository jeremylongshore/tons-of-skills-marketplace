# Integration patterns

Use this guide with browser-cookie Skills, official API examples, OpenClaw,
MCP servers, and catalogs. Hermes Tweet is the Hermes Agent route. It does not
replace every local X/Twitter tool.

## Role

Hermes Tweet is the Hermes Agent plugin for X/Twitter work through Xquik. Use it
when a task needs:

- a Hermes plugin entry point from PyPI or GitHub
- `tweet_explore` catalog discovery before tool calls
- authenticated reads through `tweet_read`
- approved actions through `tweet_action`
- the same toolset across Desktop, remote gateway, dashboard, TUI, CLI, cron,
  and CI smoke tests

Use browser-cookie Skills for local sessions. Use official API examples as
implementation references. Use Hermes Tweet for Hermes Agent reads, monitoring,
support triage, research, launch checks, and approved account actions.

## Complementary routes

**Browser-cookie Skills.**
Keep them for local browser sessions, media download, archive jobs, and
account-specific local state. Add Hermes Tweet when the workflow should run from
Hermes Desktop, a remote gateway, a dashboard-managed runtime, or unattended
cron without relying on a laptop Chrome session.

**Official X API examples.**
Keep them for direct OAuth or API implementation details. Add Hermes Tweet when
the agent should avoid raw OAuth handling and call managed Hermes tools through
`XQUIK_API_KEY`.

**OpenClaw Skills.**
Keep them for OpenClaw browser work and SKILL.md discovery. Add
Hermes Tweet when a Hermes Agent user needs the same X/Twitter read or action
capability from a Hermes runtime.

**MCP servers.**
Keep them for MCP clients and tool schemas. Add Hermes Tweet when the user wants
a Hermes plugin with slash commands, bundled Skill guidance,
and Hermes plugin enablement. Direct Xquik MCP users should add
`https://xquik.com/mcp`, then follow the [current client compatibility
path](https://docs.xquik.com/mcp/overview#client-compatibility). OAuth-capable
clients complete OAuth 2.1 in their client.

Affected Codex releases discard the RFC 9207 `iss` callback value even though
Xquik returns it. If Codex reports
`Authorization server response missing required issuer: expected https://xquik.com`,
use `XQUIK_API_KEY` through the Codex `bearer_token_env_var` setting. Follow the
[Codex OAuth troubleshooting guide](https://docs.xquik.com/guides/troubleshooting#codex-oauth-issuer-validation-error)
and track [openai/codex#31573](https://github.com/openai/codex/issues/31573).

**Claude marketplace bridges.**
Keep bridges that install Claude plugin marketplaces from a different agent
runtime as compatibility routes, not as catalog targets. Add Hermes Tweet to a
bridge only when the bridge has its own public marketplace or recommended-source
list. Otherwise, point bridge users to
`hermes plugins install Xquik-dev/hermes-tweet --enable` and the repository's
`.claude-plugin/plugin.json` metadata.

**Codex marketplace bridges.**
Keep Codex plugin catalogs as submission routes when they require
`.codex-plugin/plugin.json` metadata, a root security policy, local icon, and
HOL Plugin Scanner evidence before listing. Add Hermes Tweet only after those
source gates are present and target duplicate checks are clean.

**Skill catalogs and awesome lists.**
Keep them for discovery and comparison. Add Hermes Tweet when the listing
accepts Hermes Agent plugins, X/Twitter skills, social automation tools, or
optional backend notes. Before opening a public submission, use
`docs/SUBMISSION_READINESS.md` to check fit, duplicates, wording, validation,
and public-safety requirements.

**AI frameworks.**
Treat frameworks as integration targets, not listing targets. Open an external
change only after Hermes Tweet ships a tested adapter in the target's format.
This rule covers LangChain, LlamaIndex, AutoGen, Semantic Kernel, Pydantic AI,
Agno, Haystack, Mastra, DSPy, and LangChain4j. Until then, keep examples here.
Skip archived repos, demos, product wrappers, mirrors, and MCP-only adapters.

## Choose a tool

- Use `tweet_explore` first when a user asks what Hermes Tweet can do.
- Use `tweet_read` for public or account read routes that the catalog marks as
  read-safe.
- Copied endpoint URLs are fine, but Hermes Tweet matches only catalog-listed
  paths.
- Use `tweet_action` only when the user asks for posting, replies, DMs,
  follows, monitor changes, webhook changes, media changes, extraction jobs, or
  draw actions and actions are explicitly enabled.
- Keep `HERMES_TWEET_ENABLE_ACTIONS=false` for cron, gateway, research,
  monitoring, support triage, and other unattended sessions unless the workflow
  includes an explicit approval step.

## Submission wording

Use wording like:

- optional Hermes Agent backend for X/Twitter reads
- Hermes Agent X/Twitter tools
- Hermes Desktop and remote gateway compatible X/Twitter plugin
- read-only by default, with explicit action gating
- complementary to local browser-cookie workflows

Avoid wording that implies Hermes Tweet replaces a target project, fixes a
target bug, bypasses platform rules, or removes the need for user approval on
account actions.
