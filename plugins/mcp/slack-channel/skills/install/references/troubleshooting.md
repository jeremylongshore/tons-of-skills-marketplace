# Troubleshooting — top silent-failure modes

When the install seems complete but the bot doesn't respond, work through
this list in order. The top five cover ~95% of fresh-install issues.

For automated diagnosis, run `/slack-channel:install doctor` — it checks
all ten conditions below and reports a structured pass/fail. Then run
`/slack-channel:install repair` to auto-fix the fixable ones.

## 1. Bot is not in the channel (silent killer)

**Symptom**: pairing DM works, but `@bot hello` in a channel produces silence.

**Why**: Slack installs apps to the workspace without joining channels.
The bot is in your workspace but not in the specific channel where you
sent the message. The event never reaches the server because the bot
isn't listening to that channel.

**Fix**:

1. Open Slack → navigate to the channel.
2. Click the channel name at the top → **Integrations** tab.
3. Click **Add an App** → select your bot.
4. Confirm the bot now appears in the channel's member list.

For private channels, the bot needs explicit invitation. For multiple
channels, repeat per channel.

## 2. Claude Code version too old

**Symptom**: Channels plugin doesn't load at all; `claude --channels ...`
either errors or starts without the plugin active.

**Why**: the installed build does not expose the current Channels contract.

**Fix**:

```bash
claude --version
claude --help | grep -- --channels
# upgrade per https://code.claude.com/docs/en/setup
```

## 3. Authentication or organization policy blocks Channels

**Symptom**: plugin fails to register, or registers but channel events
don't arrive. Logs at `~/.claude/logs/` show auth-related errors.

**Why**: Channels accepts a `claude.ai` account or an Anthropic Console API
key, but not Bedrock, Google Cloud Agent Platform, or Microsoft Foundry
authentication. Team and Enterprise organizations must also enable Channels.

**Fix**:

```bash
claude auth status
# claude.ai users can complete the browser flow when needed:
claude login
```

If authentication is valid, ask an organization Owner to check **Admin
settings → Claude Code → Channels**, or inspect managed settings for
`channelsEnabled`. Do not rotate Slack tokens to fix an Anthropic policy block.

## 4. Bun not installed

**Symptom**: `bun: command not found` when starting the MCP server.

**Fix**:

```bash
curl -fsSL https://bun.sh/install | bash
# restart shell, then re-run install
```

Or fall back to Node.js + edit `.mcp.json` per
[`references/prerequisites.md`](prerequisites.md#nodejs-fallback).

## 5. Wrong file permissions on `.env`

**Symptom**: server starts but rejects tokens, or `.env` is rejected
with a "file mode too permissive" warning.

**Why**: CCSC enforces `0600` on the token file to prevent other users
on the same system from reading credentials.

**Fix**:

```bash
chmod 0600 ~/.claude/channels/slack/.env
```

`/slack-channel:install repair` does this automatically.

## 6. Token has wrong prefix

**Symptom**: `/slack-channel:configure` rejects the tokens with an
"invalid token prefix" error.

**Why**: Easy to swap the two tokens by accident. Bot token starts with
`xoxb-`, app token starts with `xapp-`.

**Fix**: re-copy from the Slack app dashboard. The Bot User OAuth Token
lives at **OAuth & Permissions** (top of the page after install). The
App-Level Token lives at **Basic Information** → scroll to **App-Level Tokens**.

## 7. Missing OAuth scope

**Symptom**: bot connects and replies in DMs but a specific feature
silently fails (no reactions, files don't download, display names show
as user IDs).

**Why**: bot needs all 8 OAuth scopes per the install playbook. Missing
scopes cause silent feature failures, not connection failures.

**Fix**:

1. Open https://api.slack.com/apps → your app → **OAuth & Permissions**.
2. Compare **Bot Token Scopes** against the required 8:
   `chat:write`, `channels:history`, `groups:history`, `im:history`,
   `reactions:write`, `files:read`, `files:write`, `users:read`.
3. Add any missing scope.
4. Slack shows a banner at the top: **Reinstall your app**. Click it.
5. Run `/slack-channel:configure` again with the new tokens (reinstall
   can rotate them).

## 8. Missing event subscription

**Symptom**: bot connects but doesn't see messages of a specific type
(e.g., sees DMs but not channel messages, or vice versa).

**Why**: each event type (`message.im`, `message.channels`,
`message.groups`, `app_mention`) is a separate subscription.

**Fix**: at **Event Subscriptions** → **Subscribe to bot events**,
add the missing event. Save. (No reinstall needed for event subscription
changes — they take effect immediately.)

## 9. Socket Mode not enabled (or app token revoked)

**Symptom**: server starts but immediately errors with `socket_mode_token_revoked`
or `not_authed`.

**Why**: either Socket Mode was disabled at the app level, or the
specific `xapp-` token was revoked / deleted.

**Fix**:

1. **Settings** → **Socket Mode** → confirm toggle is **on**.
2. **Basic Information** → **App-Level Tokens** → confirm the token
   exists. If not, generate a new one with `connections:write` scope.
3. Re-run `/slack-channel:configure` with the new app token.

## 10. Audit log hash break

**Symptom**: `bun server.ts --verify-audit-log <path>` reports
`broken at line N`.

**Why**: either a write to the log was lost (rare — filesystem issue,
process crash mid-write), or the log was tampered with externally
(more likely if you have multiple writers, which you shouldn't).

**Fix**: this is NOT auto-repairable. The journal is supposed to be
tamper-evident — a break is a finding, not a bug. Surface it for
incident review:

1. Don't truncate or rewrite `audit.log`. Move it aside as
   `audit.log.broken.<timestamp>` for forensic inspection.
2. Start fresh: the server creates a new `audit.log` on next boot if
   the file is missing.
3. Investigate root cause before treating as resolved.

## When all else fails

1. Run `/slack-channel:install doctor` and share the output.
2. Check `~/.claude/logs/` for the most recent Claude Code session log.
3. Check `~/.claude/channels/slack/audit.log` for `gate.dropped` events
   — they record why messages were rejected.
4. File an issue at https://github.com/jeremylongshore/claude-code-slack-channel/issues
   with the doctor output and the last 50 lines of relevant logs.

Do NOT include token values, full user IDs, or message content in
bug reports. The journal's redactor scrubs known secret patterns, but
the conservative move is to redact yourself before sharing.
