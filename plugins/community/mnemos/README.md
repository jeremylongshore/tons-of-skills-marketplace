# Mnemos

Mnemos is a memory layer for AI coding agents. I built it because Claude Code keeps forgetting conventions, corrections, and decisions between sessions, and that gets old fast.

[![release](https://img.shields.io/github/v/release/polyxmedia/mnemos?sort=semver)](https://github.com/polyxmedia/mnemos/releases)
[![CI](https://github.com/polyxmedia/mnemos/actions/workflows/ci.yml/badge.svg)](https://github.com/polyxmedia/mnemos/actions/workflows/ci.yml)
[![coverage](https://codecov.io/gh/polyxmedia/mnemos/branch/main/graph/badge.svg)](https://codecov.io/gh/polyxmedia/mnemos)
[![license: MIT](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

Most memory tools care about retrieval, how stuff comes back out. I care more about whether anything gets recorded in the first place, because agents almost never bother unless you force them. So mnemos has both, and it ships with a verifier that runs Claude twice on a fixed scenario set (once with mnemos enabled, once disabled) so you can actually see what changes.

The basic shape: you correct your agent for retrying blindly on a 401. Mnemos stores:

```json
{
  "type": "correction",
  "tried": "retry on 401",
  "wrong_because": "401 is auth failure, not transient",
  "fix": "refresh token, then retry once"
}
```

Next session, that entry surfaces in the prewarm context before the agent gets near that code path again. Three corrections clustered on the same agent, project, and topic get promoted into a skill by the consolidation pass. There's no LLM running inside the memory layer, just clustering and templating over structured records, so the same input always gives you the same output and you can audit the whole pipeline end to end.

`mnemos replay <session_id>` regenerates a past session as markdown with everything you've recorded since layered in. Useful for "what would I do differently now" sessions.

Single static Go binary, ~15 MB, runs on Linux, macOS, and Windows. State lives in `~/.mnemos/mnemos.db` (SQLite).

## Install

```bash
curl -fsSL https://raw.githubusercontent.com/polyxmedia/mnemos/main/scripts/install.sh | bash
mnemos doctor
```

The installer runs `mnemos init`, which auto wires Claude Code, Claude Desktop, Cursor, Windsurf, and OpenAI Codex CLI. Restart your agent and the `mnemos_*` tools show up next session.

Or with Homebrew:

```bash
brew install polyxmedia/tap/mnemos
mnemos init
mnemos doctor
```

Brew gets you `brew upgrade mnemos` for free, the curl installer auto-wires agent clients in one shot. Either path works.

For Claude Code, also install the agent skill so it records back to the store on its own:

```bash
mkdir -p ~/.claude/skills/mnemos
curl -fsSL https://raw.githubusercontent.com/polyxmedia/mnemos/main/.claude/skills/mnemos/SKILL.md \
  -o ~/.claude/skills/mnemos/SKILL.md
```

Other paths: `go install github.com/polyxmedia/mnemos/cmd/mnemos@latest` or grab a [release binary](https://github.com/polyxmedia/mnemos/releases). `mnemos update` swaps the binary in place after verifying its sha256.

## Verify

I got tired of memory tools claiming lift without measuring it, so I built a harness. Three modes:

```bash
mnemos verify retrieval   # do memories surface for their trigger queries?
mnemos verify behavior    # does the agent behave differently with mnemos on vs off?
mnemos verify capture     # does the agent record corrections handed to it?
```

Behaviour A/B against Claude Code, n=5 paired runs:

```
scenario                        on    off   lift
session_start_on_edit           5/5   0/5   +100%
oss_first_for_protocol          5/5   0/5   +100%
no_ai_attribution_in_commit     5/5   5/5    +0%
no_cgo_proposal                 5/5   5/5    +0%
migration_locked_refused        5/5   5/5    +0%
overall                         25/25 15/25  +40%
```

The lift concentrates on two places. First, contrarian or project-specific conventions, where the model has no prior to lean on. Second, the recursive case where the agent forgets to use its own memory tools at all (looking at you, `session_start_on_edit`). On widely-known practices the model already gets right, mnemos doesn't add anything, and it doesn't subtract either, on-arm and off-arm match exactly.

Capture is the uglier half. Baseline was 7%. I tuned trigger-phrase examples in the tool descriptions and got a few points. The structural fix that actually moved the number was a `UserPromptSubmit` hook that pattern matches correction-shaped phrasing in your prompt and emits a `[mnemos: capture required]` directive into context, basically making the trigger non skippable. That got it to 53%.

```
scenario                        captured  rate
explicit_save_request           3/3       100%
inline_correction               2/3        67%
quiet_convention_mention        2/3        67%
silent_correction_mid_work      1/3        33%
architectural_decision          0/3         0%
overall                         8/15       53%
```

Architectural decisions buried inside larger task prompts still sit at 0/3 even with the directive lever, the bigger task framing seems to override the capture cue. I don't have a clean fix for that yet. If you've got ideas I'd love to hear them.

Fixtures and runner: [`verify/`](verify/).

## Design

The interesting parts. If you skim anything, skim here.

### Correction journal

Corrections have their own observation type with the schema `tried / wrong_because / fix`. Search ranks them above generic observations on the same topic, so when you're about to walk the same path again the past mistake surfaces first.

### Skill promotion

The consolidation pass clusters corrections by agent, project, and topic. Three or more in the same cluster get templated into a skill, and a stable origin hash means a second pass extends the existing skill instead of creating a new one. The whole thing is deterministic, no LLM is calling itself in a loop deciding what counts as similar enough.

### Rumination

Skills rot. Threshold monitors flag the ones that drop in effectiveness, sit untouched for months, keep accumulating corrections after promotion, or get explicitly contradicted by a `contradicts` link. Once a skill is flagged you can't just edit it, you have to write down what new prediction the new version makes that the old one didn't. It's a Popperian guard at the tool boundary, basically forcing falsifiability into the revision process so you can't quietly paper over a wrong belief.

### Bi-temporal store

Facts have valid and invalid timestamps. The default ranker only surfaces currently valid facts, but old ones stay queryable for replay and audit. Same idea Graphiti uses, the implementation is just much simpler.

### Prompt-injection scanner

Memory stores are a write-time attack surface. Anything that can write an observation can plant fake tool-call syntax, MCP spoofing payloads, zero-width unicode, bidi overrides, or instruction overrides, all the stuff that ends up in your context next session and looks like it came from you. The scanner runs at write time and either sanitises the content or wraps it in a `[MNEMOS: FLAGGED]` banner so the model can see it for what it is.

### Hybrid retrieval

BM25 plus cosine similarity via Reciprocal Rank Fusion. Auto enables when Ollama is reachable. Falls back to pure FTS5 when it isn't, which is fine for most projects, embeddings only really pay off on paraphrased queries.

### Composed prewarm

`mnemos_session_start` and the `SessionStart` hook return a token budgeted block (conventions, recent sessions, matching skills, corrections, hot files) capped at 500 tokens by default. Fires once per session, no per-turn cost. I measured: empty store is ~20 tokens, populated hits the cap around 460.

### Compaction recovery

When Claude Code compacts mid-session you lose your in-session state. `mnemos_context` in `recovery` mode reconstructs goal, decisions, and in-session observations so the agent can keep going.

### Skill packs and Obsidian export

Export a skill as a JSON pack, share by file or URL, install with `mnemos skill import <file-or-url>`. Or run `mnemos vault export|watch` to write the whole store as a markdown graph with wikilinks, in case you want to read it in Obsidian.

## Setup per agent

`mnemos init` is idempotent and handles all of the below. Manual configurations if you'd rather:

### Claude Code

`~/.claude.json`:

```json
{
  "mcpServers": {
    "mnemos": { "command": "/full/path/to/mnemos", "args": ["serve"] }
  }
}
```

`mnemos init` also writes hooks to `~/.claude/settings.json` (honours `CLAUDE_CONFIG_DIR`) and removes ones earlier releases installed that are no longer used. The two `SessionStart` hooks open a session with a prewarm block, and restore that session's state after a compaction:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|resume|clear",
        "hooks": [{ "type": "command", "command": "/full/path/to/mnemos prewarm", "timeout": 10 }]
      },
      {
        "matcher": "compact",
        "hooks": [{ "type": "command", "command": "/full/path/to/mnemos prewarm --mode compaction_recovery", "timeout": 10 }]
      }
    ]
  }
}
```

`mnemos doctor` lists the rest (`UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `SessionEnd`) and flags any obsolete entry still installed.

### Cursor / Windsurf / Claude Desktop / Codex CLI

Same `mcpServers.mnemos` shape. Paths:

| Client | Config path |
| --- | --- |
| Cursor | `~/.cursor/mcp.json` |
| Windsurf | `~/.codeium/windsurf/mcp_config.json` |
| Claude Desktop (macOS) | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Claude Desktop (Windows) | `%APPDATA%\Claude\claude_desktop_config.json` |

Codex CLI uses TOML at `~/.codex/config.toml`:

```toml
[mcp_servers.mnemos]
command = "/full/path/to/mnemos"
args    = ["serve"]
```

### Any MCP-compatible client

Stdio: point the client at `mnemos serve`. The server advertises 17 tools and 4 resources on the `initialize` handshake (21 tools when rumination is enabled).

### HTTP transport

For multi-agent or remote setups:

```bash
MNEMOS_API_KEY=$(openssl rand -hex 32) mnemos serve --http :8080
```

Use `pkg/client` from Go or call `POST /v1/observations` directly. Reference: [docs/MCP_TOOLS.md](docs/MCP_TOOLS.md).

## CLI

| Command | |
| --- | --- |
| `mnemos serve [--http :PORT]` | MCP stdio (default) or HTTP API |
| `mnemos init` | Wire agent clients |
| `mnemos doctor` | Verify install |
| `mnemos prewarm` | Print session-start prewarm block |
| `mnemos search <query>` | Search store |
| `mnemos stats` | Counts and tags |
| `mnemos sessions` | Recent sessions |
| `mnemos replay <session_id>` | Markdown recap of a past session |
| `mnemos export [file]` | JSON dump |
| `mnemos import <file>` | Restore from JSON |
| `mnemos prune` | Remove expired observations |
| `mnemos dream [--watch]` | Consolidation pass |
| `mnemos vault export\|watch\|status` | Obsidian sync |
| `mnemos embed status\|backfill` | Embedding tools |
| `mnemos skill list\|export\|import` | Manage skill packs |
| `mnemos verify retrieval\|behavior\|capture\|all` | Run verification harness |
| `mnemos update [--yes]` | Self-update with sha256 verify |
| `mnemos config` / `mnemos version` | Print config / version |

## MCP tools

`mnemos_save` `mnemos_search` `mnemos_get` `mnemos_delete` `mnemos_link` `mnemos_session_start` `mnemos_session_end` `mnemos_context` `mnemos_premortem` `mnemos_promote` `mnemos_correct` `mnemos_convention` `mnemos_touch` `mnemos_skill_match` `mnemos_skill_save` `mnemos_skill_score` `mnemos_stats`

With `[rumination].enabled = true`: `mnemos_ruminate_list` `mnemos_ruminate_pack` `mnemos_ruminate_resolve` `mnemos_ruminate_dismiss`

Parameters: [docs/MCP_TOOLS.md](docs/MCP_TOOLS.md).

## Configuration

`~/.mnemos/config.toml`, auto-created on first run. Every field is optional.

```toml
[storage]
path = "~/.mnemos/mnemos.db"

[search]
decay_rate         = 0.05
default_limit      = 20
max_context_tokens = 2000
hybrid_alpha       = 0.5    # 1.0 = pure BM25, 0.0 = pure vector

[embedding]
provider  = "auto"          # auto | ollama | openai | none
model     = "nomic-embed-text"
dimension = 768

[vault]
enabled        = false
path           = "~/.mnemos/vault"
watch_interval = "5m"

[dream]
interval     = ""           # e.g. "6h"
stale_days   = 30
decay_amount = 1

[rumination]
enabled                   = true
skill_effectiveness_floor = 0.3
skill_min_uses            = 10
stale_skill_days          = 90
stale_skill_floor         = 0.5
correction_repeat_n       = 3
contradiction_threshold   = 1

[server]
transport = "stdio"
http_addr = ":8080"
api_key   = ""
```

Nothing leaves your machine by default. Network calls only happen if you set `[embedding].provider = "openai"` or run with `[server].transport = "http"`.

## Architecture

```
internal/storage      SQLite + FTS5 (modernc.org/sqlite), bi-temporal schema
internal/memory       observations, hybrid ranker (BM25 + cosine via RRF)
internal/session      session service
internal/skills       procedural memory service
internal/prewarm      session_start and compaction-recovery composers
internal/safety       prompt-injection scanner
internal/dream        consolidation daemon
internal/rumination   threshold monitors, hostile-review packaging
internal/vault        Obsidian export and watcher
internal/embedding    Ollama / OpenAI / Noop providers
internal/mcp          official MCP Go SDK wrapper
internal/api          HTTP REST transport
internal/installer    agent client wire-up
pkg/client            typed Go HTTP client
```

More in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Build

```bash
make test           # -race, full suite
make cover          # coverage.html
make lint           # golangci-lint
make release V=v0.X.Y
```

Coverage 70% overall, 80 to 95% on the core domain packages. API is stable at v0.1.x and the schema is bi-temporal so migrations stay non-breaking.

## License

MIT. By [André Figueira](https://x.com/voidmode) at [Polyxmedia](https://polyxmedia.com). [AUTHORS.md](AUTHORS.md), [ROADMAP.md](ROADMAP.md), [CONTRIBUTING.md](CONTRIBUTING.md). Issues and PRs welcome, I read them.
