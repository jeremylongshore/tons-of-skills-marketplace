# PostWire

Publish one idea to every social network, with a **different post written for each one**.

TikTok, Instagram, YouTube, LinkedIn, X, Bluesky, Mastodon, Facebook, Threads, Reddit, Telegram and
Discord, through a single API key. Accounts are connected once by OAuth in the PostWire dashboard,
so there is no per-platform developer app or review queue to maintain.

## Why not just send the same string everywhere

Because it reads badly and the platforms suppress it. A LinkedIn post written like a tweet performs
like neither. PostWire has a generate step that writes a caption per network — length, tone, hashtags
and link handling — from one prompt.

## The part that matters in an agent loop

Media rules are checked **before** the post is queued:

| network | requires |
|---|---|
| TikTok, YouTube | a video |
| Instagram | a photo or video |
| everything else | text is enough |

So an agent gets `media_required` at the moment it asks, rather than a silent failure at 7am. The
skill documents the error codes worth branching on: `not_connected`, `media_required`, `preview_key`.

## Install

The plugin ships both a skill and an MCP server:

- **Skill** — `skills/postwire/SKILL.md`, documents the REST API with verified examples.
- **MCP** — `https://postwire.io/mcp` (HTTP), so the agent calls tools instead of writing curl.

Set `POSTWIRE_API_KEY` from the **API & MCP** page of the dashboard. The free tier is one brand and
30 posts a month, no card.

## Links

- Site: https://postwire.io
- MCP endpoint: https://postwire.io/mcp
- npm (stdio variant): https://www.npmjs.com/package/postwire-mcp
