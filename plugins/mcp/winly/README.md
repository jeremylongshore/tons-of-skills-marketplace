# Winly

Run your Instagram and Facebook DMs from Claude, ChatGPT or any AI agent.

This plugin connects Claude Code to Winly, the official remote MCP server run by Winly AI.

## What it does

Winly connects your Instagram and Facebook DM inbox to any MCP-compatible AI agent. The agent can read chats, search contacts, tag leads, set a stage and owner, add notes, reply to comments on your posts and pull reports like speed to lead and response rate. It can also send the replies you ask it to. Built on Meta's official API.

## Installation

```bash
/plugin marketplace add jeremylongshore/claude-code-plugins
/plugin install winly@claude-code-plugins-plus
```

Or add the server directly:

```bash
claude mcp add --transport http winly https://app.sbccrm.com/bld/api/mcp
```

The plugin ships this `.mcp.json`:

```json
{
  "mcpServers": {
    "winly": {
      "type": "http",
      "url": "https://app.sbccrm.com/bld/api/mcp"
    }
  }
}
```

## Server

- URL: `https://app.sbccrm.com/bld/api/mcp`
- Transport: Streamable HTTP

## Authentication

- OAuth 2.1 (PKCE, dynamic client registration)
- Or an API key in the `X-API-Key` header

## Links

- Homepage: https://getwinly.ai/mcp/
- Support: hello@getwinly.ai

## License

Proprietary. Winly is a hosted server by Winly AI with no public repository.
