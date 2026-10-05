![CI](https://github.com/jeremylongshore/x-bug-triage-plugin/actions/workflows/ci.yml/badge.svg)
![Version](https://img.shields.io/github/v/release/jeremylongshore/x-bug-triage-plugin)

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/U5S225PTME)

# X Bug Triage Plugin v0.6.7

Public prototype for collecting bounded X/Twitter complaint samples and evaluating local triage heuristics and downstream contracts. Live X intake is implemented; GitHub scanning, owner lookup, issue filing, severity automation, Slack delivery, and end-to-end orchestration are not.

## Quick Start

```bash
bun install --frozen-lockfile
bun run db:migrate
bun test

# Export this only in the MCP server environment.
export X_BEARER_TOKEN="..."

# In Claude Code terminal:
/x-bug-triage @AnthropicAI --window 24h

# Claude can fetch a bounded public sample. Local libraries can be
# evaluated separately; downstream MCP tools demonstrate contracts.
```

The committed approved-search and surface-to-repository mappings are empty. Configure them before using those workflows. Never put the bearer token in a prompt, committed file, or command output.

## Architecture

```
Implemented: X API v2 → six live intake tools
             fixtures → local parser/redactor/scorer/dedupe/cluster/database libraries

Prototype contracts only: synthetic repo records → empty routing results
                          → local draft text → simulated filing receipt
```

One MCP server (`triage`) exposes 19 tools. Their runtime status is explicit:

| Tool Group    | Tools | Purpose                                                                    |
| ------------- | ----- | -------------------------------------------------------------------------- |
| X Intake      | 6     | X API v2 ingestion (mentions, search, conversations, quotes)               |
| Repo Analysis | 4     | Synthetic Tier-3 schema records; no GitHub access                          |
| Routing       | 5     | Offline contract stubs; no owner or provider lookup                        |
| Issue Draft   | 3     | Local text, caller-supplied title comparison, and simulated filing receipt |
| Review        | 1     | Syntax parsing only; no command execution or state mutation                |

The local Bun modules implement deterministic parsing, pattern-based redaction, fixed heuristic scoring, text deduplication, clustering, SQLite helpers, and tests. No checked-in runner currently connects those modules to live MCP intake.

## Public Skills

All five directories under `skills/` are public marketplace skills:

- `x-bug-triage` — bounded live intake and honest prototype evaluation
- `bug-clustering` — fixture-driven local heuristic evaluation
- `repo-scanning` — synthetic repository-evidence contract testing
- `owner-routing` — offline routing-precedence contract testing
- `triage-display` — safe terminal-summary formatting guidance

Each skill links to a runtime contract that distinguishes implemented behavior from planned integrations. The plugin exposes no Slack tool and does not automatically integrate with the separate Slack plugin.

## Project Structure

```
mcp/triage-server/      # Single MCP server (19 tools: server.ts + lib.ts)
lib/                    # Shared library (types, db, config, audit)
db/                     # SQLite schema and migrations
config/                 # 8 operational config files
skills/                 # 5 public skills with policy and runtime references
agents/                 # 4 subagent definitions
data/                   # Runtime data (SQLite DB, reports, audit logs)
tests/fixtures/         # Mock API responses for deterministic testing
000-docs/               # Durable project documentation
```

## License

MIT — see [LICENSE](LICENSE).
