# claude-code-slack-channel v0.12.0

The Slack-native governance substrate for Claude Code — the kernel other governance tooling builds on. Humans, Claude Code sessions, and peer agents converse safely in shared channels: every tool call passes through a declarative, tier-aware policy engine; every decision lands in a hash-chained, **Ed25519-signed** audit journal you can verify offline. Per-thread session isolation, identity-aware permission gates, operator admin commands with cross-channel approval, multi-agent loop control + backpressure, **lease-fenced sessions that survive a process crash with loss-proof reply delivery**, and defense-in-depth against prompt injection. The policy/journal/relay kernel here is the substrate that the companion **[agent-governance-plane (AGP)](#companion-tooling)** reimplements for cross-runtime governance.

[![CI](https://github.com/jeremylongshore/claude-code-slack-channel/actions/workflows/ci.yml/badge.svg)](https://github.com/jeremylongshore/claude-code-slack-channel/actions/workflows/ci.yml)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/jeremylongshore/claude-code-slack-channel/badge)](https://scorecard.dev/viewer/?uri=github.com/jeremylongshore/claude-code-slack-channel)

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/U5S225PTME)

**Links:** [Roadmap & Scope](ROADMAP.md) · [Gist One-Pager](https://gist.github.com/jeremylongshore/2bef9c630d4269d2858a666ae75fca53) · [GitHub Pages](https://jeremylongshore.github.io/claude-code-slack-channel/) · [Release Notes](https://github.com/jeremylongshore/claude-code-slack-channel/releases/tag/v0.12.0)

> **Research Preview** — Channels require a current Claude Code build and
> Anthropic authentication through either `claude.ai` or a Console API key.
> Team and Enterprise organizations must enable Channels before use.

## How It Works

```
Slack workspace (cloud)
    ↕ WebSocket (Socket Mode — outbound only, no public URL)
server.ts (local MCP server, spawned by Claude Code)
    ↕ stdio (MCP transport)
Claude Code session
```

Socket Mode means **no public URL needed** — works behind firewalls, NAT, anywhere.

## Quick Start

**For AI-assisted setup**: run `/slack-channel:install` and your AI assistant will walk you through every step below. The install skill also supports `doctor` (health check), `verify` (round-trip test), `repair` (auto-fix), `manifest` (one-click Slack-app import), `reset`, `tour`, and `uninstall` modes — see [`skills/install/SKILL.md`](skills/install/SKILL.md).

### Prerequisites

Before step 1, confirm you have:

- **Bun ≥ 1.0** — install with `curl -fsSL https://bun.sh/install | bash`. Node.js / Docker fallbacks are documented in [Option B](#option-b-nodejs--npx) / [Option C](#option-c-docker) below.
- **A current Claude Code build with Channels support** — upgrade through the
  [official install guide](https://code.claude.com/docs/en/setup).
- **Supported Anthropic authentication** — use either a `claude.ai` account or
  an Anthropic Console API key. On Team and Enterprise plans, an Owner must
  enable Channels in Admin settings (or deploy `channelsEnabled: true`).

### 1. Create a Slack App

1. Go to [api.slack.com/apps](https://api.slack.com/apps) → **Create New App** → From scratch
2. **Socket Mode**: Settings → Socket Mode → Enable → Generate App-Level Token (`xapp-...`) with `connections:write` scope
3. **Event Subscriptions**: Enable → Subscribe to bot events:
   - `message.im` — DMs
   - `message.channels` — public channels
   - `message.groups` — private channels
   - `app_mention` — @ mentions
4. **Bot Token Scopes** (OAuth & Permissions):
   - `chat:write` — send messages
   - `channels:history` — read public channels
   - `groups:history` — read private channels
   - `im:history` — read DMs
   - `reactions:write` — add reactions
   - `files:read` — download shared files
   - `files:write` — upload files
   - `users:read` — resolve display names
5. **Install to Workspace** → Copy Bot Token (`xoxb-...`)

### 2. Configure Tokens

```bash
/slack-channel:configure xoxb-your-bot-token xapp-your-app-token
```

### 3. Run

Pick your runtime:

<a id="option-a-bun-recommended"></a>
#### Option A: Bun (recommended)

```bash
bun install
# Current (claude-code-plugins marketplace):
claude --channels plugin:slack-channel@claude-code-plugins
# Future (after upstream approval):
# claude --channels plugin:slack-channel@claude-plugins-official
```

<a id="option-b-nodejs--npx"></a>
#### Option B: Node.js / npx

```bash
npm install
# In .mcp.json, change command to: "npx", args: ["tsx", "server.ts"]
claude --channels plugin:slack-channel@claude-code-plugins
```

<a id="option-c-docker"></a>
#### Option C: Docker

```bash
docker build -t claude-slack-channel .
# In .mcp.json, change command to: "docker", args: ["run", "--rm", "-i", "-v", "~/.claude/channels/slack:/state", "claude-slack-channel"]
claude --channels plugin:slack-channel@claude-code-plugins
```

### 3.5. Add the bot to your Slack channel

**This step is the most common silent failure.** Slack installs apps to the workspace without joining any channels. The pairing DM in step 4 works because DMs auto-route, but a channel test message in step 5 will hit silence — the bot literally isn't in the channel to see the event.

1. Open Slack → navigate to the channel where you want the bot to live
2. Click the channel name at the top → **Integrations** tab
3. Click **Add an App** → select your bot
4. Confirm: the bot now appears in the channel's member list

Private channels need explicit invitation. Repeat per channel if the bot needs to be in more than one.

### 4. Pair Your Account

1. DM the bot in Slack — you'll get a 6-character pairing code
2. In your terminal: `/slack-channel:access pair <code>`
3. You're connected. Chat away.

### 5. Verify it's working

In the channel where you added the bot in step 3.5, send:

```
@<bot-name> hello
```

The bot should reply within 10 seconds. If you get silence, run `/slack-channel:install doctor` for a structured diagnosis, then `/slack-channel:install repair` to auto-fix what's fixable. See [Troubleshooting](#troubleshooting) for the top failure modes.

### Troubleshooting

The five silent-failure modes that cover ~95% of fresh-install issues:

1. **Bot is not in the channel** — see step 3.5 above. Channel test messages hit silence because the bot can't see the event.
2. **Claude Code lacks Channels support** — run `claude --version`, upgrade
   through the official install path, and retry with `--channels`.
3. **Authentication or organization policy blocks Channels** — authenticate
   with `claude.ai` or a Console API key. Team and Enterprise Owners must also
   enable Channels; Bedrock, Google Cloud Agent Platform, and Microsoft
   Foundry authentication are not supported for Channels.
4. **Bun not installed** — `bun: command not found`. Install with `curl -fsSL https://bun.sh/install | bash` or use the Node.js fallback in Option B.
5. **Wrong file permissions on `.env`** — must be `0600`. Run `chmod 0600 ~/.claude/channels/slack/.env`, or run `/slack-channel:install repair`.

Full troubleshooting matrix (10 failure modes): [`skills/install/references/troubleshooting.md`](skills/install/references/troubleshooting.md).

## Policy Engine (v0.6.0+)

Author rules in `access.json.policy` to automate permission decisions for Claude Code tool calls. Three rule effects, evaluated strictest-tier-first then first-applicable within a tier (detailed below):

```json
{
  "policy": [
    {
      "id": "safe-reads-in-ops",
      "effect": "auto_approve",
      "match": { "tool": "Read", "channel": "C_OPS_DOCS" }
    },
    {
      "id": "no-shell",
      "effect": "deny",
      "match": { "tool": "Bash" },
      "reason": "Shell execution is not permitted."
    },
    {
      "id": "dangerous-writes",
      "effect": "require_approval",
      "match": { "tool": "Write", "channel": "C_DEPLOY" },
      "approvers": 2,
      "ttlMs": 300000
    }
  ]
}
```

- **`auto_approve`** — skip the Block Kit prompt; the tool call runs immediately and a `policy.allow` event is journaled.
- **`deny`** — the reason is posted back into the originating thread and the call is rejected. `policy.deny` is journaled.
- **`require_approval`** — route through human approver(s). `approvers: 2` requires two **distinct** Slack `user_id`s (NIST two-person integrity; the same user cannot double-satisfy quorum by clicking twice). A single deny from any allowlisted user rejects the request immediately regardless of quorum count.
- Successful approvals grant a TTL window scoped to `(rule, channel, thread)` so a chain of similar calls doesn't re-prompt.
- Parse errors in `access.json.policy` are **fatal at boot** — policy is safety-critical, silent degradation is not offered. Missing or empty `policy` is fine (first-install path).

**Tier-aware evaluation**: rules carry a tier (`admin` → `user` → `workspace` → `default`). Evaluation is strictest-tier-wins — a higher tier's `deny` cannot be overridden by a lower tier's `auto_approve`, so a workspace-level guardrail can't be relaxed by a per-user rule. Within a tier, first-applicable ordering holds.

When a call is denied, the result returned to Claude is **context-stripped** to a bare `{ behavior: 'deny' }` — the rule id and reason are journaled and posted to the thread, but not handed back to the model, so a denied tool call can't be reverse-engineered into a rephrase-and-retry loop.

Full schema reference: [`ACCESS.md`](ACCESS.md#policy-schema-v050). Decision procedure: [`000-docs/policy-evaluation-flow.md`](000-docs/policy-evaluation-flow.md). Release scope and what was deliberately deferred: [`000-docs/v0.6.0-release-plan.md`](000-docs/v0.6.0-release-plan.md).

## Access Control

See [ACCESS.md](ACCESS.md) for the full schema.

```bash
/slack-channel:access policy allowlist       # Only pre-approved users
/slack-channel:access add U12345678          # Add a user
/slack-channel:access remove U12345678       # Remove a user
/slack-channel:access channel C12345678      # Opt in a channel (default: mention-to-engage)
/slack-channel:access channel C12345678 --ambient  # Ambient: Claude hears every message
/slack-channel:access status                 # Show current config
```

**Interaction modes.** A newly opted-in channel defaults to **mention-to-engage** (`requireMention: true`): people converse freely and Claude only sees messages that `@`-mention it — and once a human mentions the bot in a thread, they can keep talking in that thread without re-mentioning (peer agents must `@`-mention every time). Pass `--ambient` for a dedicated bot channel where Claude hears everything, or `--allow <ids>` to restrict which humans are heard. See [ACCESS.md](ACCESS.md#interaction-modes).

### Multi-agent coordination

Channels can opt in to cross-bot message delivery by listing trusted bot user IDs in `allowBotIds`. Useful when multiple Claude Code instances (or other bots you operate) need to coordinate in a shared channel — e.g., an ops-monitor agent and an engineering agent in `#incidents`. Default is no cross-bot delivery: every bot message is dropped at the gate. See [ACCESS.md](ACCESS.md) for the full schema and security tradeoffs.

Example `access.json` entry:

```json
{
  "channels": {
    "C_INCIDENTS": {
      "requireMention": false,
      "allowFrom": ["U_OPS_BOT", "U_ENG_BOT", "U_HUMAN"],
      "allowBotIds": ["U_OPS_BOT", "U_ENG_BOT"]
    }
  }
}
```

Self-echoes from this bot are always filtered regardless of `allowBotIds`. Peer bots cannot approve permission prompts — the permission relay gates on the top-level `allowFrom`, not the channel policy.

**For the full multi-agent recipe** — registering a second bot, configuring `allowBotIds` mutually, mention-driven addressing, the per-bot rate limit + channel-wide circuit breaker + global session backpressure, per-user session isolation, the `!mute`/`!unmute` write verbs and `!agents`/`!mute-status`/`!rate-limit` read-only verbs, common failure modes, what you DON'T get — see [`000-docs/multi-agent-channels.md`](000-docs/multi-agent-channels.md).

This is a prompt-injection vector by design. The security model is documented threat-model-first in [`SECURITY.md`](SECURITY.md): (1) the adversary and the four principals, (2) the mitigations below — each with its own stated limit, and (3) an explicit list of **what this does NOT protect against** (same-UID host compromise, in-process token exposure, supply-chain, Slack/Anthropic platform bugs). Start there for the full picture; the defense-in-depth layers are:

- **Sender gating**: Every inbound message hits a gate. Ungated messages are silently dropped before reaching Claude.
- **Outbound gate**: Replies only work to channels that passed the inbound gate.
- **File exfiltration guard**: Cannot send `.env`, `access.json`, `audit.log`, or other state files through the reply tool.
- **Prompt-injection defense**: System instructions explicitly tell Claude to refuse pairing/access requests from Slack messages — peer-bot messages carry the same risk as human messages.
- **Bot filtering**: `bot_id` messages are dropped by default. Channels that host multiple cooperating agents can opt in to specific peers via `allowBotIds`; self-echoes are always filtered via `bot_id` / `bot_profile.app_id` / `user` triple-check.
- **Link unfurling disabled**: All outbound messages set `unfurl_links: false, unfurl_media: false`.
- **Token security**: `.env` is `chmod 0o600`, never logged, never in tool results.
- **Static mode**: Set `SLACK_ACCESS_MODE=static` to freeze access at boot (no runtime mutation).
- **Signed audit journal**: Every tool-call decision is written to a hash-chained, **Ed25519-signed** journal (RFC 8785 JCS canonical form). The chain is verifiable offline against a published public key — see [Audit Signing](#audit-signing).
- **Admin-command hardening**: Operator verbs (`!clear`, `!restart`) route through gate → policy → journal → execute and require a server-minted **HMAC nonce confirmed from a second channel**. Claude cannot self-invoke them — no MCP tool name begins with `admin.`. This closes the EchoLeak / operator-coercion class ([CVE-2025-32711](https://github.com/jeremylongshore/claude-code-slack-channel/blob/main/000-docs/THREAT-MODEL.md), threat T11): a prompt injected into one channel cannot drive a privileged action, because confirmation must come from a channel the attacker doesn't control.
- **Multi-agent loop control + backpressure**: A per-`(channel, bot_id)` sliding-window rate limit (default 10 msg/60s) breaks A→B→A runaway loops; a channel-wide circuit breaker trips a 3+-bot ring (A→B→C→A) the pairwise limiter misses; an optional global `maxConcurrentSessions` cap sheds load before file handles / memory are exhausted (journaling `session.activate_rejected`). Operators can `!mute <@bot>` / `!unmute <@bot>` a peer and inspect state read-only with `!agents`, `!mute-status`, `!rate-limit`. Optional per-user session isolation (`perUserSessions`) gives each sender their own bridge session within a shared thread.
- **Crash-safe sessions + loss-proof replies**: Each active session holds a fencing lease (monotonic token + heartbeat) so exactly one process owns a turn; a boot-time recovery sweep requeues work whose lease lapsed and quarantines anything it cannot prove safe. Replies are recorded as durable obligations **before** the send and drained by a leased, retrying, dead-lettering poller with idempotency keys — so a transient Slack error or a process crash redelivers **exactly once** instead of silently dropping the reply. Live for single-message, chunked, and streaming replies (file-upload durability is in progress — see [Reliability & crash-safety](#reliability--crash-safety)).

Each layer's limit, and an explicit **"what this does NOT protect against"** section, are in [`SECURITY.md`](SECURITY.md). Trust boundaries, per-primitive attack surface, and threats T1–T11 are documented in [`000-docs/THREAT-MODEL.md`](000-docs/THREAT-MODEL.md).

## Audit Signing

Every decision the gate makes is journaled to `~/.claude/channels/slack/audit.log` — hash-chained and, as of v0.10, **Ed25519-signed** — so a third party can verify the log against a public key without trusting the host.

```bash
# Verify a journal end-to-end (hash chain + signatures):
bun server.ts --verify-audit-log ~/.claude/channels/slack/audit.log

# Operator key lifecycle (Ed25519 over RFC 8785 JCS):
bun audit-key-cli.ts init       # generate keypair, encrypt private half to .env, print public key
bun audit-key-cli.ts rotate     # fresh keypair, re-sign chain head, archive the old public key
bun audit-key-cli.ts verify     # verify the log against active + archived public keys
bun audit-key-cli.ts show       # print active public key + key id
```

The key is loaded at boot from SOPS+age-encrypted `.env`. Run with `--no-audit-signing` to fall back to hash-chain-only. Design + rotation lifecycle: [`000-docs/audit-journal-architecture.md`](000-docs/audit-journal-architecture.md) and [`000-docs/key-management.md`](000-docs/key-management.md).

## Reliability & crash-safety

A governance substrate that loses a decision — or a reply — is not trustworthy. The runtime is built so a process crash never silently drops work:

- **Fencing lease per turn.** Each active session holds a monotonic-token + heartbeat lease, so exactly one process owns a turn even if an old one resurrects. A fenced write from a superseded owner is rejected and the handle is driven into quarantine (no split-brain).
- **Boot-time recovery sweep.** On startup the supervisor reads every session file and classifies in-flight work: a lapsed heartbeat (owner provably dead) is **requeued**; a still-fresh marker or an unreadable file is **orphaned into quarantine** and fails closed until a human clears it. Both are journaled (`session.recovery.requeued` / `session.recovery.orphaned`).
- **Transactional reply outbox.** A reply is recorded as a durable `DeliveryObligation` **before** the Slack send, drained by a leased poller that retries transient errors with bounded exponential backoff and dead-letters permanent ones (a dead-letter always records *why* — never a silent black hole).
- **Exactly-once delivery.** Each obligation carries a deterministic idempotency key stamped into Slack message metadata; a redelivery after a lost ack is recognised and skipped. Live for **single-message, chunked, and streaming** replies; **file-upload** durability is landing in two parts (building blocks + design merged; production wiring in progress), because Slack file shares carry no app metadata and need a thread-scan dedup plus an exfil-guard that re-validates the bytes on every (re)upload.

Operator knobs (all optional, sensible defaults): `SLACK_SESSION_LEASE_TTL_MS` (lease TTL, default 30s), `SLACK_DELIVERY_POLL_MS` (outbox drain interval, default 15s), `SLACK_MAX_CONCURRENT_SESSIONS` (global backpressure cap, default unlimited). Design: [`000-docs/session-state-machine.md`](000-docs/session-state-machine.md) and the crash-safety addenda in [`000-docs/ADR-002`](000-docs/ADR-002-architecture-patterns-from-peer-runtime-audit.md).

## Companion tooling

**agent-governance-plane (AGP)** is a companion governance tool that builds **on** this substrate. AGP **reimplements** ("adapt-and-harden") a pinned baseline of CCSC's governance kernel — the policy engine, the hash-chained signed journal, the Slack relay, and nonce-bound HITL — under its own typed contracts to govern agent runtimes beyond a single Slack bridge. It is *not* a byte-for-byte vendored copy: AGP's ADR 040 superseded the original vendor approach for v0, tracking CCSC by a documented drift review against a pinned commit instead. The relationship is one-way by design: **CCSC is the substrate and has zero knowledge of AGP**; AGP is the downstream consumer. If you need governance across multiple agent runtimes (not just Claude Code in Slack), AGP is the layer to look at; if you need a governed Slack channel for Claude Code, CCSC is all you need. The substrate-extraction contract is in AGP's `000-docs/009-AT-ADR-...` (mechanism updated by its `040-AT-ADR-substrate-boundary-reconciliation`), and the patterns shared between the two are recorded in [`000-docs/ADR-002`](000-docs/ADR-002-architecture-patterns-from-peer-runtime-audit.md).

## Testing & Quality

Security-critical code earns a hard gate. `ci.yml` runs nine checks in sequence on every PR — a red on any one blocks merge:

| Gate | What it enforces |
|---|---|
| `bun run typecheck` | TypeScript strict, no `any` escape hatches |
| Biome lint | curated rule set |
| `bun test` | **1,251 tests / 6,782 assertions** across unit + property + Gherkin suites |
| coverage floor | **≥ 95%** line + function (`scripts/coverage-floor.sh`) |
| dependency-cruiser | architecture invariants (e.g. `policy.ts` may never import `manifest.ts`) |
| Gherkin lint | acceptance-feature style, `--strict` |
| harness-hash verify | SHA-256 tamper check on pinned `.feature` + arch-rule files |
| `bun audit` | dependency CVEs at `--audit-level=high` |
| crap-score | cyclomatic-complexity ceiling (30) |

Out of band: **CodeQL**, **gitleaks** secret scanning, **OpenSSF Scorecard**, and manual **Stryker mutation testing** (`bunx stryker run`, baselines in [`000-docs/MUTATION_REPORT.md`](000-docs/MUTATION_REPORT.md)). The seven Wall-1 acceptance primitives (61 scenarios across 7 `.feature` files) live in [`features/*.feature`](features/) and run against the real code via a hand-rolled Gherkin runner.

```bash
bun test                  # full suite
bun run typecheck         # strict type check
bunx @biomejs/biome check .
```

## Development

```bash
# Dev mode (bypasses plugin allowlist):
claude --dangerously-load-development-channels server:slack
```

## One-Pager & System Analysis

[Full project one-pager and operator-grade system analysis](https://gist.github.com/jeremylongshore/2bef9c630d4269d2858a666ae75fca53)

## Changelog

Every user-visible change is recorded in [`CHANGELOG.md`](CHANGELOG.md) (Keep a Changelog format). Release notes: [GitHub Releases](https://github.com/jeremylongshore/claude-code-slack-channel/releases).

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for branching, commits, PR workflow, and the quality-gate checklist. AI assistants helping with contributions should read [`AGENTS.md`](AGENTS.md) first.

## Contributors

- [@jeremylongshore](https://github.com/jeremylongshore) — author, maintainer
- [@maui-99](https://github.com/maui-99) — security hardening review (v0.3.0)
- [@jinsung-kang](https://github.com/jinsung-kang) — clean shutdown on client disconnect (v0.3.1)
- [@CaseyMargell](https://github.com/CaseyMargell) — event deduplication fix (v0.3.1), cross-bot delivery via `allowBotIds` (v0.4.0)

## Support

[![Sponsor on GitHub](https://img.shields.io/badge/Sponsor-GitHub-ea4aaa?logo=githubsponsors&logoColor=white)](https://github.com/sponsors/jeremylongshore)
[![Buy Me a Coffee](https://img.shields.io/badge/Buy_Me_a_Coffee-ffdd00?logo=buymeacoffee&logoColor=black)](https://www.buymeacoffee.com/jeremylongshore)

This is open-source software maintained by [Jeremy Longshore](https://github.com/jeremylongshore). If it saves you time, consider [sponsoring on GitHub](https://github.com/sponsors/jeremylongshore) or [buying a coffee](https://www.buymeacoffee.com/jeremylongshore) — it funds continued development and keeps the project independent.

## License

Apache License 2.0 — see [LICENSE](LICENSE).
