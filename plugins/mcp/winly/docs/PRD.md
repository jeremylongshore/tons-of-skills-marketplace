# PRD: winly

**Author:** Winly AI
**Date:** 2026-11-25
**Status:** Draft

## Problem

Winly connects your Instagram and Facebook DM inbox to any MCP-compatible AI agent. This plugin gives Claude Code that connection through Winly's official remote MCP server, so you can run your Instagram and Facebook DMs from Claude Code.

## Target users

| User                       | Context                                       | Primary need                                     |
| -------------------------- | --------------------------------------------- | ------------------------------------------------ |
| Winly users on Claude Code | Working with their Instagram and Facebook DMs | Read chats, tag leads and reply from Claude Code |

## Success criteria

1. Installing the plugin registers the `winly` server at `https://app.sbccrm.com/bld/api/mcp` over Streamable HTTP.
2. The user can authenticate with OAuth 2.1 (PKCE, dynamic client registration) or an API key in the `X-API-Key` header.

## Functional requirements

- **FR-1:** Read chats and search contacts.
- **FR-2:** Tag leads, set a stage and owner, and add notes.
- **FR-3:** Reply to comments on your posts.
- **FR-4:** Pull reports like speed to lead and response rate.
- **FR-5:** Send the replies the user asks it to.

## Out of scope

- Hosting the server locally. Winly is a proprietary hosted server with no public repository.
