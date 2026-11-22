# Agent City plugin for Claude Code

Watch your Claude Code sessions as gangs in [Agent City](https://github.com/Lulu-The-Narwhal/agent-city), a local 3D
open-world city that runs on your machine. The plugin only reports session events to the city: it is watch-only and
carries no cost data.

## Install

In a Claude Code session:

```text
/plugin marketplace add Lulu-The-Narwhal/agent-city
/plugin install agent-city@agent-city
```

Then start the city with `npx agent-city-ai` (needs Node 20 or newer). New Claude Code sessions appear in the city;
running ones after a restart. If you run the city on another port, start Claude Code with the same `AGENT_CITY_PORT`.

Use this plugin or `npx agent-city-ai install-claude`, not both. While `install-claude`'s hooks are in your user
settings the plugin stays silent, so no event is counted twice.

Remove it with `/plugin uninstall agent-city@agent-city`.

## What the plugin runs and accesses

- **Runs:** one Node script, `hooks/forward.mjs`, with `node` on each hook event (3 s timeout). It has no
  dependencies and no install or build step.
- **Reads:** the hook event on stdin, `~/.agent-city/token`, and your Claude settings
  (`$CLAUDE_CONFIG_DIR/settings.json`, default `~/.claude/settings.json`), only to see whether `install-claude`'s
  hooks are already there.
- **Sends:** one POST per event to `http://127.0.0.1:$AGENT_CITY_PORT/hooks/claude-code` (default port 4646), and
  nothing to any other host. It authenticates with a token derived from `~/.agent-city/token`, never the token itself.
- **Never:** writes a file, prints to stdout, blocks or steers Claude, or exits non-zero. When it skips an event
  (city stopped, no token) it writes one line to stderr.

## License

MIT. See [LICENSE](https://github.com/Lulu-The-Narwhal/agent-city/blob/main/LICENSE).
