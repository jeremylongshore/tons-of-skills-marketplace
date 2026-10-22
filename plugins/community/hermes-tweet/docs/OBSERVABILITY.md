# Runtime checks

Hermes Tweet reports runtime state through tool output, plugin logs, and slash
commands.

## Runtime status

- `/xstatus` returns account, subscription, and usage status.
- `/xtrends` confirms authenticated read access and current trend availability.
- Tool handlers return JSON strings for both success and error cases.
- API failures include HTTP status and response payload without exposing
  credentials.
- `hermes plugins list` shows whether the plugin is installed and enabled.
- `hermes tools list` shows the `hermes-tweet` toolset in non-interactive
  terminals. Bare `hermes tools` opens the interactive tool UI and requires a
  TTY. Current Hermes Agent releases list plugin toolsets there, not every
  individual plugin tool name.
- The Hermes plugin registry exposes loaded tools, slash commands, and bundled
  plugin skills for deterministic runtime smoke tests.
- Hermes Agent v0.16.0 Desktop, TUI, CLI, and gateway sessions can all use
  the same enabled `hermes-tweet` runtime toolset.
- Remote gateway profiles execute plugin code on the remote Hermes host, so
  install state and environment variables must be verified there.

## Safety checks

- `tweet_read` rejects private or write-like endpoints.
- `tweet_action` rejects every call unless `HERMES_TWEET_ENABLE_ACTIONS=true`.
- Dashboard-only admin, billing, credit top-up, support-ticket, API-key, and
  account re-authentication endpoints are omitted from the catalog.

## CI checks

Public CI runs workflow linting, formatting, linting, type checking, tests,
coverage, security scan, dependency audit, package build, and package metadata
validation.
The release workflow uses current artifact actions so trusted-publishing runs
stay ahead of GitHub Actions runtime deprecations.

## Runtime smoke test

Use this check after installing or updating Hermes Tweet:

```bash
hermes tools list
hermes -z "Use tweet_explore, then read /api/v1/account. Do not call tweet_action." --toolsets hermes-tweet
```

Record only sanitized outcomes:

- Catalog exploration succeeded.
- Copied endpoint URLs resolved only to catalog-listed `/api/v1/...` paths.
- Without `XQUIK_API_KEY`, Hermes exposed only `tweet_explore` from this plugin.
- With `XQUIK_API_KEY`, account read succeeded or returned a status code.
- `tweet_action` stayed hidden or disabled when `HERMES_TWEET_ENABLE_ACTIONS`
  was unset.
- `/xstatus` and `/xtrends` were registered.

Hermes one-shot runs cannot verify slash-command registration through
`hermes -z "/xstatus"` or `hermes -z "/xtrends"`; that text can
route as a model prompt. Verify slash-command registration in an active CLI,
TUI, Desktop, or gateway session, or through the plugin registry tests. Use
one-shot `hermes -z` for tool-call probes such as `tweet_explore` and
`tweet_read`.

Do not store API keys in shell history, docs, issue comments, CI logs, PR bodies,
or Hermes prompts. Use an ephemeral environment variable for one-off smoke tests
or `~/.hermes/.env` for local persistent Hermes sessions. After changing
`~/.hermes/.env`, run `/reload` in an interactive CLI session before the smoke
test. Gateway and cron sessions need a restart or new session so they read the
new values.
