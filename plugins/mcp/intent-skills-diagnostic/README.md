# Intent Skills Diagnostic

A hosted MCP app from Intent Solutions. It asks a few questions about how you use Claude or Codex, then recommends at most two plugins from a reviewed list of Tons of Skills plugins and Intent Solutions offerings, each with the install route for the tool you use.

## What it does

- Asks only what it still needs: where you use AI, what you use it for, how far your setup goes, what you keep explaining to the AI, and where it goes wrong. Every choice question takes as many answers as apply, and the welcome card's examples start the questions already filled in. It asks what you build only for software work, and never when it can read the project instead.
- On Claude Code or Codex, it can list the names of installed skills and plugins (names only, never config contents) so it does not recommend what you already have.
- Returns one of four results: a fitting match, more information needed, no verified match, or no new tool needed. It never invents a pick.
- Every pick shows why it fits, its source page, the date it was checked, and install buttons for your tool: Open Plugins and Copy on claude.ai and Desktop, Copy on Cowork, copyable commands on Claude Code and Codex.
- An optional link to Intent Solutions, shown only when you ask for more help. Nothing is booked or submitted.

All five tools are read-only. Nothing is stored or sent. The app installs nothing itself; on Claude Code or Codex, Claude can run the install commands for you only after you say yes.

## Install

Claude Code:

```
/plugin marketplace add jeremylongshore/claude-code-plugins
/plugin install intent-skills-diagnostic@claude-code-plugins-plus
```

claude.ai, Claude Desktop or Cowork: add it as a custom connector (Settings, Connectors, Add custom connector) with this URL:

```
https://intent-skills-diagnostic.max-sheahan.workers.dev/mcp
```

The connector has no sign-in. If the dialog says it could not check how the server signs in, choose Continue anyway, then no authentication.

## Try it

- "What skills should I add to Claude Code?"
- "I keep telling Claude how to write our commit messages. Is there a skill for that?"
- "I teach middle school and use claude.ai for lesson plans. What would help?"

## Tools

| Tool | Returns |
|---|---|
| `start_here` | Welcome card with examples |
| `scan_setup` | What to list on Claude Code or Codex (names only) |
| `ask_questions` | The questions still open, on a card |
| `recommend_skills` | Up to two reviewed picks with install routes |
| `talk_to_intent` | A link to intentsolutions.io/contact |

## Verification (2026-10-15, updated 2026-10-16)

- End-to-end smoke suite: 50 checks against the live endpoint, all passing.
- Browser QA of every card state at 375 px and desktop width, light and dark.
- Security: secure-launch 0.3.0, 0 FAIL, 0 UNKNOWN, 24 PASS; security headers on every path.
- Install routes: Claude Code and Codex installs verified in throwaway homes (the exact CLI commands the card copies); the claude.ai route (Add marketplace from this repository, then search the plugin and press Add) completed live on 2026-10-16; Cowork from Anthropic's documentation.
