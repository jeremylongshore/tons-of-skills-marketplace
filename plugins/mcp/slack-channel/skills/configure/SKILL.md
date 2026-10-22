---
name: configure
description: Configure Slack channel tokens (bot token + app-level token). Use when writing or rotating the Slack bot and app-level tokens for the slack-channel plugin. Trigger with "/slack-channel:configure", "configure slack tokens", or "set up my slack bot token".
version: 1.1.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: Apache-2.0
compatibility: Requires Claude Code with the slack-channel plugin and a Slack app that already exists (tokens come from api.slack.com/apps); POSIX shell for chmod/mkdir.
tags: [slack, tokens, configuration, security]
user-invocable: true
argument-hint: "<bot-token> <app-token>"
allowed-tools: [Write, "Bash(chmod:*)", "Bash(install:*)", "Bash(mkdir:*)", "Bash(mv:*)", "Bash(rm:*)"]
model: inherit
effort: medium
---

# /slack-channel:configure

## Overview

Configure the Slack channel with its bot and app-level tokens. This is the only
token-writing path: validate prefixes, write `.env` with owner-only
permissions, never echo secrets, and return control to the install walkthrough.

## Prerequisites

- A Slack app already created (via `/slack-channel:install` Step 1 or
  manually at api.slack.com/apps) with:
  - the **Bot User OAuth Token** (`xoxb-...`) from **OAuth & Permissions**, and
  - the **App-Level Token** (`xapp-...`, scope `connections:write`) from
    **Socket Mode** settings.
- A writable home directory — state lives at `~/.claude/channels/slack/`.

## Usage

Pass both tokens as arguments, bot token first. Obtain them directly from the
Slack app dashboard and avoid shell history or shared transcripts:

```
/slack-channel:configure <xoxb-bot-token> <xapp-app-token>
```

## Authentication

- The `xoxb-` Bot User OAuth Token represents the installed bot and authorizes
  Web API calls within its granted bot scopes.
- The `xapp-` app-level token represents the Slack app and requires
  `connections:write` to open the Socket Mode WebSocket.
- Prefix checks establish token type, not validity. `install doctor` verifies
  liveness against Slack without printing the credential.
- Store tokens only in `~/.claude/channels/slack/.env`; never commit them or
  include them in output, logs, screenshots, or issue reports.

Read [`references/official-auth.md`](references/official-auth.md) when creating,
rotating, revoking, or diagnosing either token type.

## Instructions

1. Parse the two arguments from `$ARGUMENTS`:
   - First token must start with `xoxb-` (Bot User OAuth Token)
   - Second token must start with `xapp-` (App-Level Token)

2. If either token is missing or has the wrong prefix, show this error and stop:

   ```
   Error: Two tokens required.
     - Bot token (starts with xoxb-) from OAuth & Permissions
     - App token (starts with xapp-) from Socket Mode settings

   Usage: /slack-channel:configure xoxb-... xapp-...
   ```

3. Create the state directory if it doesn't exist, then make the directory
   owner-only **before writing any secret-bearing file**:

   ```bash
   mkdir -p ~/.claude/channels/slack
   # 0700 = owner may read/write/traverse; no group or other access
   chmod 700 ~/.claude/channels/slack
   ```

4. Pre-create the fixed candidate path with owner-only permissions, then use
   `Write` to replace its complete contents. This makes the file `0600` from
   the instant it exists, independent of the process umask:

   ```bash
   # 0600 = owner read/write; no group or other access
   install -m 600 /dev/null ~/.claude/channels/slack/.env.tmp
   ```

   Write this complete content to `~/.claude/channels/slack/.env.tmp`:

   ```
   SLACK_BOT_TOKEN=<bot-token>
   SLACK_APP_TOKEN=<app-token>
   ```

5. Set the candidate file to owner-only, then atomically replace `.env`. If
   `Write`, `chmod`, or `mv` fails before replacement, remove only the exact
   candidate path `~/.claude/channels/slack/.env.tmp`; leave the prior `.env`
   untouched.

   ```bash
   # 0600 = owner read/write; no group or other access
   chmod 600 ~/.claude/channels/slack/.env.tmp
   mv ~/.claude/channels/slack/.env.tmp ~/.claude/channels/slack/.env
   ```

6. Confirm success:
   ```
   Slack channel configured.

   Start Claude with the Slack channel:
     claude --channels plugin:slack-channel@claude-code-plugins

   Or for development:
     claude --dangerously-load-development-channels server:slack

   Next: opt in a channel and pick its interaction mode with
   /slack-channel:access channel <id>  (defaults to mention-to-engage;
   pass --ambient for a dedicated bot channel). See ACCESS.md "Interaction modes".
   ```

## Output

- On success: `~/.claude/channels/slack/.env` atomically replaced with both
  tokens and mode `0600`, plus the confirmation block above (server start
  command and the pointer to channel opt-in). Tokens are never echoed.
- On failure: the two-token usage error from step 2 and no file changes.

## Error Handling

- **Missing token or wrong prefix** — show the step-2 error block and stop;
  nothing is written. Bot tokens must start with `xoxb-`, app tokens with
  `xapp-`.
- **Tokens swapped** — the prefix check catches it; re-run with the bot token
  first.
- **Existing `.env`** — re-running atomically replaces it; this is the
  supported token-rotation path (rotation happens at api.slack.com/apps).
- **Write, permission, or move failure** — remove only the fixed candidate
  `~/.claude/channels/slack/.env.tmp`, leave the previous `.env` intact, and
  report only the failed stage without printing values.
- **Revoked/invalid tokens** — this skill only validates prefixes, not
  liveness. If the server later fails auth, run
  `/slack-channel:install doctor` (checks 4–5 test both tokens live against
  the Slack API).

## Examples

Both flows are the same command — the second run simply overwrites `.env`:

```
# First-time setup (illustrative placeholders, not live credentials)
/slack-channel:configure xoxb-WORKSPACE-EXAMPLE xapp-APP-EXAMPLE

# Rotation after regenerating tokens in the Slack UI — same command, overwrites .env
/slack-channel:configure xoxb-NEW-TOKEN xapp-NEW-TOKEN
```

## Security

- Never echo the tokens back in the confirmation message
- Never log tokens to stdout or any file other than `.env`
- Secure the state directory as `0700` before writing the candidate
- Always set `0600` on the candidate before atomically moving it into place

## Safety justification

`rm` is permitted only to clean the single fixed candidate path
`~/.claude/channels/slack/.env.tmp` after a failed rotation. Never pass a
variable, glob, directory, recursive flag, or any other path to `rm`; never
remove the previous `.env`.

## Resources

- [`skills/install/SKILL.md`](https://github.com/jeremylongshore/claude-code-slack-channel/blob/main/skills/install/SKILL.md) — the full install lifecycle that delegates to this skill (Step 3) and the doctor that verifies token liveness
- [`skills/access/SKILL.md`](https://github.com/jeremylongshore/claude-code-slack-channel/blob/main/skills/access/SKILL.md) — the next step after configuring: channel opt-in and pairing
- [`ACCESS.md`](https://github.com/jeremylongshore/claude-code-slack-channel/blob/main/ACCESS.md) — interaction modes referenced in the confirmation message
- [`README.md`](https://github.com/jeremylongshore/claude-code-slack-channel/blob/main/README.md) — quick start, including Node.js and Docker server alternatives
