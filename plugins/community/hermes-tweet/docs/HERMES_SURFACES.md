# Hermes runtime hosts

Use this guide when deciding where to install Hermes Tweet and where to keep
runtime credentials. Hermes Tweet uses one plugin entry point across Hermes
Desktop, remote gateway profiles, the web dashboard, TUI, CLI, cron, and
CI-style smoke tests. The difference is where the Hermes runtime executes.

| Hermes client | Install Hermes Tweet | Configure `XQUIK_API_KEY` | Notes |
| --- | --- | --- | --- |
| Desktop, local runtime | Local machine running Desktop | Local runtime environment or `~/.hermes/.env` | Use Desktop for review and explicit approvals. |
| Desktop, remote gateway profile | Remote Hermes host | Remote Hermes host environment or `~/.hermes/.env` on that host | The Desktop app is only the client. |
| Web dashboard | Runtime host behind the dashboard | Runtime host environment | Dashboard credential pages do not replace plugin env gating. |
| TUI or CLI | Machine running the command | Same process environment or `~/.hermes/.env` | Run `/reload` after editing `.env` in an active CLI session. |
| Cron or unattended gateway | Scheduled runtime host | Service environment before process start | Keep actions disabled unless the workflow has an approval step. |
| CI smoke test | CI job environment | Ephemeral secret store only when testing reads | Prefer `tweet_explore` checks when no secret is available. |

## Check the installation

- Install with `hermes plugins install Xquik-dev/hermes-tweet --enable`, or run
  `hermes plugins enable hermes-tweet` after installation.
- Confirm `hermes plugins list` shows `hermes-tweet` as enabled.
- Confirm `hermes tools list` shows the `hermes-tweet` toolset.
- Use `tweet_explore` first; it does not need `XQUIK_API_KEY`.
- Use only catalog-listed paths; copied endpoint URLs must resolve to one.
- Use `docs/SUBMISSION_READINESS.md` before proposing Hermes Tweet to public
  Skill, plugin, catalog, registry, awesome-list, or integration listings.
- Set `XQUIK_API_KEY` only on the host that executes plugin tools.
- Keep `HERMES_TWEET_ENABLE_ACTIONS=false` for research, monitoring, support,
  launch checks, and other unattended sessions.
- Set `HERMES_TWEET_ENABLE_ACTIONS=true` only for sessions where posting,
  replies, DMs, follows, monitor changes, webhook changes, or media changes are
  intended and approved.

## Common mistakes

- Installing Hermes Tweet only on a laptop while Desktop is connected to a
  remote gateway. Install on the remote Hermes host instead.
- Pasting API keys into prompts, issues, PR comments, or tool arguments. Use the
  runtime environment or `~/.hermes/.env`.
- Testing slash commands with one-shot `hermes -z "/xstatus"`. Use an active
  CLI, TUI, Desktop, or gateway session for `/xstatus` and `/xtrends`; use
  `hermes -z` for tool-call probes.
- Treating install as enablement. Hermes discovers third-party plugins before
  it executes them, so enablement is a separate step unless `--enable` was used.
