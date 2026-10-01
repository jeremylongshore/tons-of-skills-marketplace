# Slack Integration (Optional)

The Slack layer is a design target involving [`claude-code-slack-channel`](https://github.com/jeremylongshore/claude-code-slack-channel), a separate Claude Code plugin. It is **not bundled**, and x-bug-triage currently contains no automatic bridge to it.

## How It Works

The intended future flow is:

1. Triage results (Step 8) are displayed in the terminal AND sent to a configured Slack channel
2. Team members can send review commands from Slack
3. Claude processes commands from both terminal and Slack

The current runtime exposes no Slack delivery tool and no stateful terminal review loop. Installing the peer plugin does not activate this flow without additional orchestration.

## Setup

1. Install `claude-code-slack-channel` per its README
2. Register it in your Claude Code MCP config (separate from this plugin's `.mcp.json`)
3. Configure Slack tokens in the bridge's `.env`
4. Implement and test an explicit redacted-data handoff before using the design in production

See [000-docs/004-AT-REFF-slack-review-flow.md](../../000-docs/004-AT-REFF-slack-review-flow.md) for the review flow design.
