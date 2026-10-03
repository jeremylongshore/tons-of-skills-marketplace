<h1 align="center">Bob's Big Brain — the plugin</h1>

<p align="center">
  The governed team brain — cited recall, hash-chained receipts. A local-first Claude Code + Cowork
  plugin: turn <em>your own</em> files into a governed, <code>qmd://</code>-cited brain with a
  tamper-evident, SHA-256 hash-chained audit trail.<br>
  <strong>Compile, then govern.</strong> One plugin, two modes: <strong>local</strong> (default — in-process, no daemon, no runtime network after first-start provisioning, no API key for retrieval) or <strong>team</strong> (proxy to a shared governed brain over your network).
</p>

<p align="center">
  <img src="https://img.shields.io/badge/License-Apache--2.0-10b981?style=flat-square" alt="License: Apache-2.0">
  <img src="https://img.shields.io/badge/local--first-in--process-0ea5e9?style=flat-square" alt="local-first">
  <img src="https://img.shields.io/badge/MCP-stdio-8b5cf6?style=flat-square" alt="MCP stdio">
</p>

---

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/U5S225PTME)

## 📍 This product lives in two homes

| | Repo | What it is |
|---|---|---|
| **Landing / thesis** | **[intent-solutions-io/bobs-big-brain-umbrella](https://github.com/intent-solutions-io/bobs-big-brain-umbrella)** | The umbrella — *why* this exists, the competitive teardown, the "Compile, Then Govern" thesis, the receipts argument. Start here for the **story**. |
| **The plugin** (you are here) | **[jeremylongshore/bobs-big-brain-plugin](https://github.com/jeremylongshore/bobs-big-brain-plugin)** | The installable code — the local stdio MCP server + skills. Start here to **run it**. |

It stacks on three engines:

| Engine | Repo | Layer |
|---|---|---|
| **Bob's Big Brain Compiler** | [jeremylongshore/bobs-big-brain-compiler](https://github.com/jeremylongshore/bobs-big-brain-compiler) | **Compile** — derive knowledge from a corpus (optional; the only part that egresses) |
| **Bob's Big Brain Registrar** | [jeremylongshore/bobs-big-brain-registrar](https://github.com/jeremylongshore/bobs-big-brain-registrar) | **Govern** — deterministic dedupe → policy → promote + the hash-chained audit |
| **qmd** | [tobi/qmd](https://github.com/tobi/qmd) (`@tobilu/qmd`) | **Retrieve** — on-device search; every hit is a `qmd://` citation |

This plugin **bundles** the compiled Registrar packages, so it runs the govern + retrieve loop fully
in-process — the engines stay independent repos; nothing here forks or privatizes them.

**Powered by [tobi/qmd](https://github.com/tobi/qmd).** We pin `@tobilu/qmd` and ride upstream via Dependabot — we do **not** fork the search engine. For the **team** index (not personal `~/.cache/qmd`), operators on a Registrar checkout use `./scripts/bbb-qmd` and `pnpm search-canary` (see [bobs-big-brain-registrar ops runbook](https://github.com/jeremylongshore/bobs-big-brain-registrar/blob/main/000-docs/042-OD-OPSM-bbb-qmd-operator-runbook.md)).

## What it does

Most "AI memory" gives an agent better *recall*. This does two things the category skips: it
**governs** what's allowed to become durable memory (deterministic dedupe / policy / promotion — by
code, not a model), and it ships a **receipt** — a `qmd://` citation plus a SHA-256 hash-chained audit
event — for every write. Runs on your machine; your files never leave it (retrieval is local; the
optional *compile* step (Bob's Big Brain Compiler) is the only thing that egresses, and it's opt-in).

### Tool surface

| Tool | Kind | What it does |
|---|---|---|
| `brain_search` | read | Cited search over your governed memory (`qmd://` receipts), in-process — native-FTS5 + `qmd` reciprocal-rank fusion, then a freshness/category rerank |
| `brain_status` | read | Counts by lifecycle state + category |
| `brain_audit_verify` | read | Verify the audit trail — the SHA-256 hash chain **and** the external anchor log; flags any tamper |
| `brain_capture` | write | Capture a fact as a governance **proposal** (to the local spool) |
| `brain_govern` | write | Drain the spool → dedupe → policy → **promote**, with a hash-chained audit receipt — daemon-free |
| `brain_transition` | write | Retire / re-lifecycle a memory (audited) |

Two skills front these: **`/brain`** (cited answers) and **`/brain-save`** (governed capture).

## What the receipt does *not* do

Honesty is the point of a receipt. The chain gives you **tamper-*detection*** — integrity + ordering,
so an edited or reordered record is caught by `verify`. It is **not** tamper-proof: on your own machine
a writer with access can edit an event *and* re-hash the chain forward. Within a single trust boundary
(your machine) that's exactly the integrity guarantee you want; cross-actor non-repudiation needs an
external chain-head anchor (on the roadmap). It is **not** a blockchain and **not** immutable storage.

## Independently verify the anchor log

`brain_audit_verify` is the *in-box* check — it runs inside the same codebase that wrote the chain
(circular trust). For "don't trust us, run it yourself," there's a **standalone, zero-dependency
verifier** that re-derives every anchor hash itself, importing **nothing** from this plugin or the
engines. It's the `cat log.md` of receipts — one file, node built-ins only (`crypto`, `fs`,
`child_process`), no build step:

```bash
# defaults to $HOME/.teamkb/audit/anchors.jsonl
node scripts/verify-anchors.mjs

# be explicit, and cross-check the live DB head against the latest anchor
node scripts/verify-anchors.mjs \
  --anchors "$HOME/.teamkb/audit/anchors.jsonl" \
  --audit-dir "$HOME/.teamkb/audit" \
  --db "$HOME/.teamkb/teamkb.db"

npm run verify-anchors        # same, via the package script
node scripts/verify-anchors.mjs --json   # machine-readable output
```

It checks four things against the external anchor log (`anchors.jsonl`, an append-only hash chain):

1. **Per-record integrity** — recomputes each `anchorHash` from the canonical body; any edit is an
   `ANCHOR_HASH_MISMATCH`.
2. **Chain linkage** — `record[0].prevAnchorHash` is `null`, each subsequent `prevAnchorHash` equals
   the prior record's `anchorHash`, and `chainedRows` never regresses.
3. **External witness (git)** — confirms the anchor log is committed and clean (an uncommitted or
   un-pushed log is only *locally* witnessed — surfaced as a warning, not a hard fail).
4. **Optional DB cross-check** (`--db`, needs `sqlite3` on PATH) — the latest anchor's `chainHead`
   must equal the live audit chain's current head and its `chainedRows` must not exceed the current
   count, catching a silent rewrite of history the in-box chain-walk alone would miss.

Exit `0` on pass (witness-only warnings still exit `0`); non-zero on any integrity, linkage, or
history-rewrite failure. Run the verifier's own tests with `npm run verify-anchors:test`.

## Install

Local-mode marketplace installs provision three lockfile-pinned native modules (`better-sqlite3`,
`fs-ext`, and `sqlite-vec`) inside the plugin on first start. That one-time step uses npm; after it
completes, local capture, governance, audit, and retrieval run in-process without a service daemon.
Team mode does not load or install those local-store modules.

One command, two modes:

```bash
# A) zero-egress (default for regulated/client data) — nothing leaves the machine
npx governed-second-brain init <your-folder> --index-only

# B) full compile — the Compiler derives knowledge (6 passes) before governing; opt-in egress to DeepSeek
DEEPSEEK_API_KEY=… npx governed-second-brain init <your-folder>
```

It builds a governed, `qmd://`-cited, hash-chained-audited brain under `~/.teamkb`, installs the native
dep per-platform, and **auto-registers the MCP server with Claude Code** (`claude mcp add`; `--no-register`
to skip). Full mode runs a loud pre-flight consent (your file text goes to DeepSeek; `--yes` to skip the
prompt). Requires Node 20+, a C/C++ toolchain (for `better-sqlite3`), and `qmd` 2.x on PATH for retrieval.

After it finishes, start a new Claude Code session — the `governed-brain` tools are live. For the
`/brain` and `/brain-save` skills too, `claude plugin install governed-second-brain`.

### Forker/local mode — bring your own brain

A fork does not need the team API, a bearer token, or a shared corpus. Leave
`TEAMKB_API_URL` unset (or empty) and point the local runtime at the fork's own
brain root and tenant:

```bash
export TEAMKB_API_URL=""
export TEAMKB_BASE_PATH="$HOME/.teamkb-my-fork"
export TEAMKB_TENANT_ID="my-fork"

# Optional: keep the governed Markdown export somewhere else. This is the qmd
# source tree, not the qmd index itself.
export TEAMKB_EXPORT_DIR="$TEAMKB_BASE_PATH/kb-export"
```

The qmd index is derived and tenant-scoped at
`$TEAMKB_BASE_PATH/qmd-index/$TEAMKB_TENANT_ID`. The plugin sets qmd's XDG
registry/cache paths to that directory, so personal and forked brains do not
share an index. `brain_govern` exports governed Markdown and refreshes the
index; do not point `TEAMKB_EXPORT_DIR` at the index directory.

For a new brain, the installer applies the same contract and registers it with
Claude Code:

```bash
npx governed-second-brain init "$HOME/my-notes" \
  --index-only \
  --base "$HOME/.teamkb-my-fork" \
  --tenant "my-fork"
```

For an existing brain, set the two path components so the derived qmd path
matches the index you want to use. `brain_status` reports `mode`, `tenantId`,
`basePath`, `exportDir`, and `qmdIndexPath`; then `/brain "a few distinctive
keywords"` should return a `qmd://` citation. A non-empty `TEAMKB_API_URL`
switches to team mode, so do not set it for BYO/local grounding.

### Team mode — point it at a shared brain

The **same** plugin runs in **team mode** when `TEAMKB_API_URL` is set: instead of an in-process local
brain, it proxies to a shared governed-brain HTTP API (the Registrar's `apps/api`) over your network — so a
whole team queries and contributes to **one** governed brain. Set two environment variables:

- **`TEAMKB_API_URL`** — your team brain's API base (e.g. `http://localhost:3847`)
- **`TEAMKB_API_TOKEN`** — your personal bearer token (issued by the brain's operator)

You need network reachability to that API — typically a private network / VPN such as **Tailscale**
(the brain is meant to stay off the public internet). The dispatcher auto-detects mode from
`TEAMKB_API_URL`: set → team, unset → local. Same `/brain` + `/brain-save` skills either way.

#### Install it as a team member

The plugin runs in **Claude Code** or **Cowork** — the same install in both. It **cannot** run in
claude.ai in a web browser or the phone apps (a browser tab can't reach a local plugin or a private
network); **Claude Desktop** can, via a manual `mcpServers` config (see below). On macOS **or** Windows:

1. **Join the team network** (Tailscale) so your machine can reach the brain's API.
2. **Add the plugin** — in Claude Code or Cowork. It's a public repo, so no org membership or `gh`
   login is needed:
   ```
   /plugin marketplace add jeremylongshore/bobs-big-brain-plugin
   /plugin install governed-second-brain@governed-second-brain
   ```
3. **Save your connection** to `~/.teamkb/team.json` (Windows: `%USERPROFILE%\.teamkb\team.json`) at
   mode `600`. This file is read **before** shell env vars, so a Dock/GUI-launched Claude still reaches
   team mode:
   ```json
   {
    "apiUrl": "http://localhost:3847",
     "apiToken": "<your per-user token>",
     "tenantId": "<your tenant, e.g. intent-solutions>"
   }
   ```
4. **Restart the app**, then ask with **keywords** (retrieval is keyword-based, so strong words beat a
   full sentence): `/brain shipped this week`. A cited `qmd://` answer means you're connected.

macOS + Claude Code has a one-click installer that does steps 2–3 for you, and there's a full
per-platform walkthrough (incl. the **Claude Desktop** `mcpServers` config) in
[`onboarding/`](onboarding/README.md).

In team mode the tool surface is **`brain_search`** + **`brain_status`** (read),
**`brain_capture`** (propose), and **`brain_inbox`** / **`brain_approve`** / **`brain_reject`** /
**`brain_transition`** (admin review and lifecycle). Govern runs server-side, so there's no client
`brain_govern`: **the model proposes, the server disposes**, and each promotion gets a hash-chained
receipt. A member token can read + propose; admin actions return a clear 403 otherwise.

> Team mode is **dependency-free** — it uses only `fetch` + the MCP SDK, never the native store — so it
> runs straight from a marketplace clone with zero build.

<details><summary><strong>Build from source</strong> (to hack on the runtime)</summary>

```bash
pnpm -C ../bobs-big-brain-registrar build   # the bundle inlines the Registrar's compiled packages (sibling checkout, built)
pnpm install && pnpm build            # esbuild → plugin-runtime/governed-brain.cjs
node bin/init.mjs init <your-folder> --index-only
```
</details>

**Supply chain (shipped in 0.1.4):** npm **provenance** (via the CI release workflow) and the
`gsb.lock.json` reproducible pin — the exact Compiler × Registrar × qmd × plugin tuple, verified by a
hermetic full-chain CI smoke against the pinned set.

**Coming:** automatic Cowork MCP registration.

## License

Apache-2.0. The umbrella and both engine repos are Apache-2.0; qmd (upstream) is MIT by its author,
[@tobi](https://github.com/tobi).

---

<p align="center">
  Built by <a href="https://github.com/jeremylongshore">Jeremy Longshore</a> ·
  <a href="https://intentsolutions.io/">Intent Solutions</a> ·
  thesis at <a href="https://github.com/intent-solutions-io/bobs-big-brain-umbrella">intent-solutions-io/bobs-big-brain-umbrella</a>
</p>
