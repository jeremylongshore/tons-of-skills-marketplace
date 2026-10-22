# Context7 guide

Use this page as the compact Context7-facing guide for Hermes Tweet. It focuses
on install, auth, safe tool use, and smoke tests for coding agents.

## Install

Install from the public GitHub repository:

```bash
hermes plugins install Xquik-dev/hermes-tweet --enable
```

Hermes plugins are opt-in. If the plugin was installed without `--enable`, run:

```bash
hermes plugins enable hermes-tweet
hermes plugins list
```

Install the published Python package into the Hermes Python environment:

```bash
uv pip install --python ~/.hermes/hermes-agent/venv/bin/python hermes-tweet
hermes plugins enable hermes-tweet
```

Use the PyPI package name `hermes-tweet` and the Hermes toolset name
`hermes-tweet`.

Hermes Agent v0.16.0 includes Desktop and remote gateway profiles. For a remote
gateway profile, install and enable Hermes Tweet on the remote Hermes host and
set `XQUIK_API_KEY` there. The desktop app is only the client unless it
also runs the Hermes runtime locally.

## Configure

Create an API key in the Xquik dashboard and set it in the runtime environment:

```bash
export XQUIK_API_KEY="xq_..."
```

Optional settings:

```bash
export XQUIK_BASE_URL="https://xquik.com"
export HERMES_TWEET_ENABLE_ACTIONS="false"
```

Hermes Tweet never accepts credentials through tool arguments. If
`XQUIK_API_KEY` is missing, Hermes should expose only `tweet_explore`. That is
expected safe gating.

## Tools

| Tool | Use |
| --- | --- |
| `tweet_explore` | Search the bundled Xquik endpoint catalog without an API call. |
| `tweet_read` | Call catalog-listed read-only Xquik API endpoints. |
| `tweet_action` | Call write-like or private endpoints when actions are enabled. |

Use `tweet_explore` first. Then call `tweet_read` with a concrete
`/api/v1/...` path for account checks, tweet search, user lookup, trends,
media reads, monitors, webhooks, draws, or extraction jobs.
Copied endpoint URLs are accepted only when they resolve to catalog-listed
paths.

## Hermes Agent patterns

- Treat Hermes Tweet as the X context layer for Hermes Agent research,
  monitoring, support, launch, and content workflows.
- Use read-only routes for cron, gateway, and unattended sessions.
- Keep action routes for explicit user-approved posting, DMs, follows, monitor
  edits, webhook edits, media uploads, extraction jobs, and draws.
- Use `hermes plugins list` for enablement diagnostics because current Hermes
  Agent versions distinguish `enabled`, `disabled`, and `not enabled` plugins.
- Use project-local `.hermes/plugins/` copies only in trusted repositories and
  only with `HERMES_ENABLE_PROJECT_PLUGINS=true`.
- In Hermes Desktop, TUI, CLI, and gateway sessions, use `/xstatus` and
  `/xtrends` as interactive commands. Use `hermes -z` for tool-call probes.
- The Hermes dashboard can help administer gateway credentials and webhooks, but
  Hermes Tweet still reads `XQUIK_API_KEY` and action gating from the runtime
  environment.

Keep `HERMES_TWEET_ENABLE_ACTIONS=false` for unattended sessions. Enable actions
only when the workflow intentionally allows posting, replies, likes, retweets,
follows, DMs, monitor changes, webhook changes, media uploads, or other account
changes.

## Smoke test

```bash
hermes tools list
hermes -z "Use tweet_explore, then read /api/v1/account. Do not call tweet_action." --toolsets hermes-tweet
```

Expected result:

- `tweet_explore` finds endpoints without using the API key.
- `tweet_read` can read `/api/v1/account` after `XQUIK_API_KEY` is set.
- `tweet_action` stays disabled unless `HERMES_TWEET_ENABLE_ACTIONS=true`.
- `/xstatus` and `/xtrends` are registered slash commands.

If you edit `~/.hermes/.env` during an active Hermes CLI session, run
`/reload`. Gateway and cron sessions need a restart or new session.

## Public sources

- [GitHub repository](https://github.com/Xquik-dev/hermes-tweet)
- [Repository guide](https://github.com/Xquik-dev/hermes-tweet#readme)
- [PyPI package](https://pypi.org/project/hermes-tweet/)
- [DeepWiki](https://deepwiki.com/Xquik-dev/hermes-tweet)
- [Context7](https://context7.com/xquik-dev/hermes-tweet)
- [Hermes Agent plugins guide](https://hermes-agent.nousresearch.com/docs/user-guide/features/plugins/)
- [Build a Hermes Plugin](https://hermes-agent.nousresearch.com/docs/developer-guide/plugins)
