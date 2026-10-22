# CCSC lifecycle mode procedures

Read this reference only for `doctor`, `verify`, `repair`, `manifest`, `reset`,
`tour`, or `uninstall`. The main skill owns fresh installation.

## Doctor

Run a read-only health check and report one pass, warning, or failure per check.
Verify `curl` and `jq` with `command -v` before starting.

Load Slack tokens only from `~/.claude/channels/slack/.env` in a scoped shell.
Never paste tokens into command arguments, output, logs, or process titles.

Run these checks in order:

1. The state directory exists, belongs to the current user, and has mode `0700`.
2. `.env` exists, belongs to the current user, and has mode `0600`.
3. `.env` contains an `xoxb-` bot token and `xapp-` app-level token.
4. Call Slack `auth.test` with the bot token and report only `team` and `bot_id`.
5. Call Slack `apps.connections.open` with the app-level token. Require `ok:
true` and a `wss://` URL, but never print the URL because it is temporary
   connection material.
6. `access.json` exists, has mode `0600`, and parses as valid JSON with `jq`.
7. `allowFrom` contains at least one paired user.
8. If `audit.log` exists, run `bun server.ts --verify-audit-log PATH` and report
   the hash-chain result.
9. Claude Code exposes `--channels`, uses `claude.ai` or Anthropic Console
   authentication, and is not blocked by organization policy.
10. For each opted-in channel, use Slack `conversations.members` to confirm the
    bot is a member.

Use Bearer authentication exactly as Slack documents:

```bash
set -a
. ~/.claude/channels/slack/.env
set +a
curl --fail-with-body --silent --show-error \
  -H "Authorization: Bearer $SLACK_BOT_TOKEN" \
  https://slack.com/api/auth.test | jq '{ok, team, bot_id, error}'
unset SLACK_BOT_TOKEN SLACK_APP_TOKEN
```

Do not claim that `curl --fail` validates Slack's application-level `ok`
field; inspect the JSON response too. Map `invalid_auth`, `token_revoked`,
`account_inactive`, and `missing_scope` to explicit operator actions.

Return exit status 0 only when all checks pass. Suggest `repair` only for
findings it can safely correct.

## Verify

Ask the operator to send `@<bot> hello` in a channel where the bot is a member.
Observe the audit journal for up to 30 seconds and require the repository's
current allowed-gate event followed by its successful reply event. Report the
exact event names observed. On timeout, run `doctor`; do not infer success from
a connected WebSocket alone.

## Repair

Repair only deterministic local permission and state-shape findings:

| Doctor finding                  | Repair action                                                                                                |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| State directory missing         | Create it with `mkdir`, then set mode `0700`                                                                 |
| `.env` permissions wrong        | Set mode `0600` with `chmod`                                                                                 |
| `access.json` permissions wrong | Set mode `0600` with `chmod`                                                                                 |
| `access.json` is corrupt JSON   | Use `date` for a suffix, archive it with `mv`, write a minimal replacement with `Write`, and set mode `0600` |
| Audit chain fails               | Do not modify it; preserve evidence and start incident review                                                |
| Bot is absent from a channel    | Print the Slack UI invitation path; do not attempt an API-side membership mutation                           |
| Slack token is invalid          | Direct the operator to regenerate or revoke it in Slack; never handle the replacement outside `configure`    |
| Channels is disabled by policy  | Direct an organization Owner to the Channels setting; do not rotate Slack tokens                             |

Never modify valid `access.json` policy content automatically and never modify
the audit journal. Re-run `doctor` after repair and show the before/after result.

## Manifest

Use `Write` to create `slack-app-manifest.json` in the operator-approved current
directory. Configure the product's eight bot scopes and four event
subscriptions:

```json
{
  "display_information": {
    "name": "Claude Code Channel",
    "description": "Bridge between Claude Code and Slack via Socket Mode + MCP",
    "background_color": "#1a1a1a"
  },
  "features": {
    "bot_user": { "display_name": "Claude Code", "always_online": true }
  },
  "oauth_config": {
    "scopes": {
      "bot": [
        "chat:write",
        "channels:history",
        "groups:history",
        "im:history",
        "reactions:write",
        "files:read",
        "files:write",
        "users:read"
      ]
    }
  },
  "settings": {
    "event_subscriptions": {
      "bot_events": [
        "message.im",
        "message.channels",
        "message.groups",
        "app_mention"
      ]
    },
    "interactivity": { "is_enabled": true },
    "socket_mode_enabled": true,
    "org_deploy_enabled": false,
    "token_rotation_enabled": false
  }
}
```

Tell the operator to import it through **Create New App → From an app
manifest**, install the app to the workspace, generate an app-level token with
`connections:write`, and pass both resulting tokens to `configure`. The
manifest does not contain credentials.

## Reset

Explain the exact impact and obtain confirmation before changing state. Preserve
one rollback path:

1. Use `date` to create a timestamp.
2. Archive `access.json` and `sessions/` with `mv`; do not delete them.
3. Use `Write` to create a minimal `access.json`, then set mode `0600`.
4. Leave `.env` and `audit.log` untouched.
5. Tell the operator to restart Claude Code and pair again.

## Tour

Make no changes. Explain the five-layer defense, signed audit journal, policy
effects, multi-agent loop controls, and four-principal model. Link to the
repository's `README.md`, `ARCHITECTURE.md`, and relevant `000-docs/` files.

## Uninstall

Explain that local tokens, access state, sessions, and audit history will move
out of the active path. Obtain explicit confirmation, use `date` for a suffix,
and archive the entire state directory with `mv` to
`~/.claude/channels/slack.uninstalled.<timestamp>`. Do not permanently delete
the archive. Provide Slack's app-management path for revoking tokens or deleting
the app, and explain how to restore the archived directory.

## Authoritative sources

- [Claude Code Channels](https://code.claude.com/docs/en/channels)
- [Slack Socket Mode](https://docs.slack.dev/apis/events-api/using-socket-mode/)
- [Slack token types](https://docs.slack.dev/authentication/tokens/)
- [Slack `auth.test`](https://docs.slack.dev/reference/methods/auth.test/)
- [Slack `apps.connections.open`](https://docs.slack.dev/reference/methods/apps.connections.open/)
